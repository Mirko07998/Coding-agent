from typing import Annotated

from fastapi import APIRouter, HTTPException, Request, Path, Depends

from jira_client import JiraClient, get_jira_client

router = APIRouter()


@router.get("/issues/{id}")
def get_issue(id: Annotated[str, Path(title="The ID of the jira ticket to get")],
              jira_service: JiraClient = Depends(get_jira_client)):
    print(id, 'jira ticket id')
    ticket = jira_service.get_ticket(id)

    return ticket
