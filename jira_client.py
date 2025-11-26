"""Jira API client for fetching ticket information."""
import os
import json
from pathlib import Path
from typing import Dict, Optional

import requests
from dotenv import load_dotenv
from fastapi import HTTPException

from models.jira_ticket import TicketInfo
from models.singleton import Singleton

load_dotenv()

# Try to import MCP client, fallback to API if not available
try:
    from mcp_client import JiraMCPClient
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# Try to import Jira API client
try:
    from jira import JIRA
    JIRA_API_AVAILABLE = True
except ImportError:
    JIRA_API_AVAILABLE = False


class JiraClient(metaclass=Singleton):
    """Client for interacting with Jira API or MCP server."""
    
    def __init__(self, use_mcp: Optional[bool] = None, use_file: Optional[bool] = None, file_path: Optional[str] = None):
        """
        Initialize Jira client with credentials from environment.
        
        Args:
            use_mcp: Force MCP mode if True, API mode if False, auto-detect if None
            use_file: Force file mode if True, auto-detect if None (checks JIRA_USE_FILE env var)
            file_path: Path to JSON file containing ticket data (defaults to test_ticket.json)
        """
        # Check for file mode first (highest priority for testing)
        if use_file is None:
            use_file = os.getenv("JIRA_USE_FILE", "false").lower() == "true"
        
        self.use_file = use_file
        
        if self.use_file:
            # File mode - read from JSON file instead of Jira
            self.file_path = Path(file_path or os.getenv("JIRA_FILE_PATH", "test_ticket.json"))
            self.client = None
            self.mcp_client = None
            print(f"📄 Using file mode for Jira (reading from: {self.file_path})")
            return
        
        # Continue with normal Jira initialization
        self.use_mcp = use_mcp
        if self.use_mcp is None:
            self.use_mcp = os.getenv("USE_MCP_JIRA", "false").lower() == "true"
        
        if self.use_mcp and MCP_AVAILABLE:
            # Use MCP client
            self.mcp_client = JiraMCPClient()
            self.client = None
            print("🔌 Using MCP server for Jira")
        else:
            # Use API client
            if not JIRA_API_AVAILABLE:
                raise ImportError("jira package not installed. Install with: pip install jira")
            
            self.server = os.getenv("JIRA_SERVER_TEST")
            self.email = os.getenv("JIRA_EMAIL")
            self.api_token = os.getenv("JIRA_API_TOKEN")
            
            if not all([self.server, self.email, self.api_token]):
                raise ValueError(
                    "Missing Jira credentials. Please set JIRA_SERVER, JIRA_EMAIL, and JIRA_API_TOKEN in .env"
                )
            

            self.mcp_client = None
            options = {
                "server": "https://rb-tracker.bosch.com/tracker19",
                "headers": {
                    "Authorization": f"Bearer {self.api_token}"
                }
            }
            self.client = JIRA(
                options=options
            )

            print("🔌 Using API for Jira")
    
    def get_ticket(self, ticket_key: str) -> TicketInfo:
        """
        Fetch ticket information from Jira or file.
        
        Args:
            ticket_key: Jira ticket key (e.g., 'PROJ-123') - ignored in file mode
            
        Returns:
            Dictionary containing ticket information
        """
        # Use file mode if enabled (for testing)
        print("called method??")
        if self.use_file:
            return self._get_ticket_from_file()
        
        # Use MCP if enabled
        if self.use_mcp and self.mcp_client:
            return self.mcp_client.get_ticket(ticket_key)
        
        # Otherwise use API
        try:
            jira_service_ticket = self.client.issue(ticket_key)
            # # Extract acceptance criteria from description or custom fields
            description = jira_service_ticket.fields.description or ""
            print("---------------------------")
            print(f"Description from ticket: {description}")
            acceptance_criteria = self._extract_acceptance_criteria(jira_service_ticket)
            print("---------------------------")
            print(f"Acceptance criteria extracted: {acceptance_criteria}")
            from models.jira_ticket import TicketInfo

            ticket_info = TicketInfo(
                key=jira_service_ticket.key,
                summary=jira_service_ticket.fields.summary,
                description=description,
                acceptance_criteria=acceptance_criteria,
                status=jira_service_ticket.fields.status.name,
                issue_type=jira_service_ticket.fields.issuetype.name,
                reporter=(
                    jira_service_ticket.fields.reporter.displayName
                    if getattr(jira_service_ticket.fields, "reporter", None)
                    else None
                ),
                assignee=(
                    jira_service_ticket.fields.assignee.displayName
                    if getattr(jira_service_ticket.fields, "assignee", None)
                    else None
                ),
                labels=jira_service_ticket.fields.labels,
                url=f"{self.server}/issue/{jira_service_ticket.key}",
            )
            
            return ticket_info
        except Exception as e:
            raise HTTPException(
                status_code=e.status_code if hasattr(e, 'status_code') else 500,
                detail=f"Failed to fetch Jira ticket {ticket_key}: {e}"
            )
    
    def _get_ticket_from_file(self) -> Dict:
        """
        Read ticket information from JSON file.
        
        Returns:
            Dictionary containing ticket information
        """
        try:
            if not self.file_path.exists():
                raise FileNotFoundError(f"Ticket file not found: {self.file_path}")
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                ticket_info = json.load(f)
            
            # Ensure all required fields are present
            required_fields = ['key', 'summary', 'description', 'acceptance_criteria']
            for field in required_fields:
                if field not in ticket_info:
                    ticket_info[field] = ""
            
            # Set defaults for optional fields
            ticket_info.setdefault('status', 'To Do')
            ticket_info.setdefault('issue_type', 'Story')
            ticket_info.setdefault('reporter', None)
            ticket_info.setdefault('assignee', None)
            ticket_info.setdefault('labels', [])
            ticket_info.setdefault('url', f"file://{self.file_path}")
            
            return ticket_info
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON in ticket file {self.file_path}: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to read ticket from file {self.file_path}: {str(e)}")

    def _extract_acceptance_criteria(self, issue) -> str:
        """Extract acceptance criteria from ticket fields."""
        # Try to find acceptance criteria in custom fields or description
        acceptance_criteria = ""

        # Check description for acceptance criteria section
        if issue.fields.description:
            desc = issue.fields.description
            if "Acceptance Criteria" in desc or "Acceptance" in desc:
                # Try to extract the criteria section
                lines = desc.split('\n')
                in_criteria = False
                criteria_lines = []

                for line in lines:
                    if "acceptance" in line.lower() or "criteria" in line.lower():
                        in_criteria = True
                        continue
                    if in_criteria and line.strip():
                        criteria_lines.append(line.strip())
                    elif in_criteria and not line.strip() and criteria_lines:
                        break

                acceptance_criteria = "\n".join(criteria_lines)

                # If no criteria found, use description as fallback
        if not acceptance_criteria:
            acceptance_criteria = issue.fields.description or ""

        return acceptance_criteria


    def get_linked_repo(self, ticket_key: str) -> Optional[str]:
        """
        Get linked GitHub repository from ticket.
        
        Args:
            ticket_key: Jira ticket key - ignored in file mode
            
        Returns:
            Repository URL or None if not found
        """
        # In file mode, check if repo is in the ticket data
        if self.use_file:
            try:
                ticket_info = self._get_ticket_from_file()
                # Check if repo is specified in the ticket data
                if 'linked_repo' in ticket_info:
                    return ticket_info['linked_repo']
                # Try to extract from description
                description = ticket_info.get('description', '')
                if description:
                    import re
                    repo_pattern = r'github\.com[/:]([\w-]+)/([\w-]+)'
                    matches = re.findall(repo_pattern, description)
                    if matches:
                        owner, repo = matches[0]
                        return f"{owner}/{repo}"
            except Exception:
                pass
            return None
        
        # Use MCP if enabled
        if self.use_mcp and self.mcp_client:
            return self.mcp_client.get_linked_repo(ticket_key)
        
        # Otherwise use API
        try:
            issue = self.client.issue(ticket_key)
            # Check for linked repositories in development information
            # This may vary based on Jira configuration
            if hasattr(issue.fields, 'customfield_'):
                # Custom fields may contain repo links
                pass
            
            # Check description for repo links
            if issue.fields.description:
                import re
                repo_pattern = r'github\.com[/:]([\w-]+)/([\w-]+)'
                matches = re.findall(repo_pattern, issue.fields.description)
                if matches:
                    owner, repo = matches[0]
                    return f"{owner}/{repo}"
            
            return None
        except Exception as e:
            print(f"Warning: Could not extract repo from ticket: {str(e)}")
            return None

def get_jira_client():
    return JiraClient()