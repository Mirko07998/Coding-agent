"""Jira API client for fetching ticket information."""
import os
from typing import Dict, Optional
from dotenv import load_dotenv

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


class JiraClient:
    """Client for interacting with Jira API or MCP server."""
    
    def __init__(self, use_mcp: Optional[bool] = None):
        """
        Initialize Jira client with credentials from environment.
        
        Args:
            use_mcp: Force MCP mode if True, API mode if False, auto-detect if None
        """
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
            
            self.server = os.getenv("JIRA_SERVER")
            self.email = os.getenv("JIRA_EMAIL")
            self.api_token = os.getenv("JIRA_API_TOKEN")
            
            if not all([self.server, self.email, self.api_token]):
                raise ValueError(
                    "Missing Jira credentials. Please set JIRA_SERVER, JIRA_EMAIL, and JIRA_API_TOKEN in .env"
                )
            
            self.client = JIRA(
                server=self.server,
                basic_auth=(self.email, self.api_token)
            )
            self.mcp_client = None
            print("🔌 Using API for Jira")
    
    def get_ticket(self, ticket_key: str) -> Dict:
        """
        Fetch ticket information from Jira.
        
        Args:
            ticket_key: Jira ticket key (e.g., 'PROJ-123')
            
        Returns:
            Dictionary containing ticket information
        """
        # Use MCP if enabled
        if self.use_mcp and self.mcp_client:
            return self.mcp_client.get_ticket(ticket_key)
        
        # Otherwise use API
        try:
            issue = self.client.issue(ticket_key)
            
            # Extract acceptance criteria from description or custom fields
            description = issue.fields.description or ""
            acceptance_criteria = self._extract_acceptance_criteria(issue)
            
            ticket_info = {
                "key": issue.key,
                "summary": issue.fields.summary,
                "description": description,
                "acceptance_criteria": acceptance_criteria,
                "status": issue.fields.status.name,
                "issue_type": issue.fields.issuetype.name,
                "reporter": issue.fields.reporter.displayName if issue.fields.reporter else None,
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None,
                "labels": issue.fields.labels,
                "url": f"{self.server}/browse/{issue.key}"
            }
            
            return ticket_info
        except Exception as e:
            raise Exception(f"Failed to fetch Jira ticket {ticket_key}: {str(e)}")
    
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
            ticket_key: Jira ticket key
            
        Returns:
            Repository URL or None if not found
        """
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

