from typing import List, Optional
from pydantic import BaseModel

class ProcessTicketRes(BaseModel):
    ticket_key: str
    success: bool = False
    branch_name: Optional[str] = None
    files_generated: List[str] = []
    build_success: bool = False
    tests_success: bool = False
    pushed: bool = False
    errors: List[str] = []
    pr_url: Optional[str] = None
