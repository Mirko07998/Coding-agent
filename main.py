import uvicorn
from fastapi import FastAPI

from api.routes import jira

app = FastAPI()
if __name__ == "__main__":
    uvicorn.run(app, port=8000)

app.include_router(jira.router, tags=["jira"], prefix="/jira")
