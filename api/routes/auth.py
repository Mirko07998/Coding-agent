import ast
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.requests_client import OAuth2Session, OAuthError
from config import CLIENT_ID, CLIENT_SECRET, TENANT_ID, REDIRECT_URI, VERIFY,SCOPES
from helpers.generate_code_verifier import  code_verifier


router = APIRouter()


client = OAuth2Session(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scope=SCOPES,
    redirect_uri=REDIRECT_URI,
    code_challenge_method='S256'
    )



@router.get("/login")
async def login(request: Request):
    uri, state = client.create_authorization_url(f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize', code_verifier=code_verifier)
    # Save the state in the session to validate the callback
    request.session['oauth_state'] = state
    return RedirectResponse(uri)

@router.get("/callback")
async def auth_callback(request: Request):
    # Get the authorization response URL
    try:
        authorization_response = str(request.url)
        # Fetch the access token
        token = client.fetch_token(
            f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token',
            authorization_response=authorization_response,
            code_verifier=code_verifier,
            body=f'client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}',
            verify=ast.literal_eval(VERIFY)
        )
        # Save the token in the session or handle it as needed
        #request.session['oauth_token'] = token
        
        request.session['user'] = {"access_token": token["access_token"]}
        
        return RedirectResponse(url="/auth/me")
    except OAuthError as e:
        return {"error": str(e)}

# @router.get("/login")
# async def login(request: Request):
#     redirect_uri = REDIRECT_URI
#     return await oauth.azure.authorize_redirect(request, redirect_uri)

# @router.get("/callback")
# async def auth_callback(request: Request):
#     try:
#         token = await oauth.azure.authorize_access_token(request)
#         user_info = token.get('userinfo')
#         user = await oauth.azure.parse_id_token(token, user_info['nonce'])
#         #access_token = token.get('access_token')

#         request.session["user"] = {
#             "user_info": dict(user),
#             "access_token": token["access_token"]
#         }
#         return RedirectResponse(url="/auth/me")
#     except OAuthError as e:
#         return {"error": str(e)}

@router.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")

@router.get("/me")
async def me(request: Request):
    user = request.session.get("user")

    if not user:
        request.session.pop("user", None)
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user