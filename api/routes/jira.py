from typing import Annotated

from fastapi import APIRouter, HTTPException, Request, Path, Depends

from autonomous_agent import AutonomousCodingAgent, get_autonomous_agent_service
from jira_client import JiraClient, get_jira_client

router = APIRouter()


@router.get("/issues/{id}")
def get_issue(id: Annotated[str, Path(title="The ID of the jira ticket to get")],
              autonomous_agent_service: AutonomousCodingAgent = Depends(get_autonomous_agent_service)):
    print(id, 'jira ticket id')
    res = autonomous_agent_service.process_ticket(id)
    return res