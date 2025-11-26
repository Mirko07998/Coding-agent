from typing import Optional, List
from pydantic import BaseModel

class TicketInfo(BaseModel):
    key: str
    summary: Optional[str]
    description: Optional[str]
    acceptance_criteria: Optional[str]
    status: Optional[str]
    issue_type: Optional[str]
    reporter: Optional[str]
    assignee: Optional[str]
    labels: List[str] = []
    url: Optional[str]
