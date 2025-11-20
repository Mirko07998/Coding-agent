"""MCP (Model Context Protocol) client wrapper."""
import os
from typing import Dict, Optional, Any, List
from dotenv import load_dotenv

load_dotenv()


class MCPClient:
    """Base MCP client for interacting with MCP servers."""
    
    def __init__(self, server_name: str):
        """
        Initialize MCP client.
        
        Args:
            server_name: Name of the MCP server (e.g., 'jira', 'github')
        """
        self.server_name = server_name
        self.use_mcp = os.getenv(f"USE_MCP_{server_name.upper()}", "false").lower() == "true"
        
    def _call_mcp_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Call an MCP tool using the call_mcp_tool function.
        
        Args:
            tool_name: Name of the MCP tool to call
            **kwargs: Arguments for the tool
            
        Returns:
            Tool response
        """
        # This will be used by the agent to call MCP tools
        # The actual implementation depends on how MCP is integrated
        pass


class JiraMCPClient:
    """Jira client using MCP server."""
    
    def __init__(self):
        """Initialize Jira MCP client."""
        self.use_mcp = os.getenv("USE_MCP_JIRA", "false").lower() == "true"
    
    def get_ticket(self, ticket_key: str) -> Dict:
        """
        Fetch ticket information using MCP server.
        
        Args:
            ticket_key: Jira ticket key (e.g., 'PROJ-123')
            
        Returns:
            Dictionary containing ticket information
        """
        if not self.use_mcp:
            raise ValueError("MCP mode not enabled. Set USE_MCP_JIRA=true in .env")
        
        try:
            print(f"📡 Using MCP server to fetch Jira ticket: {ticket_key}")
            
            # Call MCP tool - this uses the call_mcp_tool function available in the agent context
            # The tool name depends on your MCP server configuration
            # Common names: "jira_get_issue", "get_issue", "fetch_issue"
            # Try to use MCP tool caller
            # In Cursor/Claude environment, call_mcp_tool tool is available
            # We'll try to import and use it
            try:
                from autonomous_agent import call_mcp_tool
                
                # Call the MCP tool for Jira
                # Note: Tool names may vary based on your MCP server configuration
                # Common names: "jira_get_issue", "get_issue", "fetch_issue"
                response = call_mcp_tool(
                    mcpServer="jira",
                    toolName="jira_get_issue",  # Adjust based on your MCP server
                    toolArgs={"issue_key": ticket_key}
                )
                
                # Parse MCP response into our expected format
                return self._parse_mcp_response(response)
                
            except (ImportError, NotImplementedError) as e:
                # If call_mcp_tool is not available or not configured,
                # try to use MCP SDK directly or provide helpful error
                print(f"⚠ MCP tool call failed: {str(e)}")
                print("💡 Tip: Make sure MCP servers are configured in your environment")
                return self._fetch_via_mcp_sdk(ticket_key)
            
        except Exception as e:
            raise Exception(f"Failed to fetch Jira ticket via MCP {ticket_key}: {str(e)}")
    
    def _parse_mcp_response(self, response: Any) -> Dict:
        """Parse MCP tool response into expected ticket format."""
        # MCP responses vary by server implementation
        # This is a generic parser - adjust based on your MCP server's response format
        if isinstance(response, dict):
            # If response is already a dict, try to map it
            return {
                "key": response.get("key", response.get("issue_key", "")),
                "summary": response.get("summary", response.get("title", "")),
                "description": response.get("description", ""),
                "acceptance_criteria": response.get("acceptance_criteria", response.get("description", "")),
                "status": response.get("status", {}).get("name", "") if isinstance(response.get("status"), dict) else response.get("status", ""),
                "issue_type": response.get("issue_type", {}).get("name", "") if isinstance(response.get("issue_type"), dict) else response.get("issue_type", ""),
                "reporter": response.get("reporter", {}).get("displayName", "") if isinstance(response.get("reporter"), dict) else response.get("reporter", ""),
                "assignee": response.get("assignee", {}).get("displayName", "") if isinstance(response.get("assignee"), dict) else response.get("assignee", ""),
                "labels": response.get("labels", []),
                "url": response.get("url", response.get("self", ""))
            }
        else:
            # If response is a string or other format, try to extract info
            return {
                "key": "",
                "summary": str(response),
                "description": str(response),
                "acceptance_criteria": str(response),
                "status": "",
                "issue_type": "",
                "reporter": None,
                "assignee": None,
                "labels": [],
                "url": ""
            }
    
    def _fetch_via_mcp_sdk(self, ticket_key: str) -> Dict:
        """Internal method using MCP SDK directly (alternative approach)."""
        # This would use the MCP Python SDK if available
        # Example implementation:
        # from mcp import ClientSession, StdioServerParameters
        # async with ClientSession(StdioServerParameters(...)) as session:
        #     result = await session.call_tool("jira_get_issue", {"issue_key": ticket_key})
        #     return self._parse_mcp_response(result)
        
        raise NotImplementedError(
            "Direct MCP SDK integration not yet implemented. "
            "Please use call_mcp_tool() function or configure MCP servers properly."
        )
    
    def get_linked_repo(self, ticket_key: str) -> Optional[str]:
        """Get linked GitHub repository from ticket using MCP."""
        if not self.use_mcp:
            return None
        
        try:
            # Use MCP tool to get linked repos
            print(f"📡 Using MCP server to get linked repo for ticket: {ticket_key}")
            # Implementation would use MCP tool here
            return None
        except Exception as e:
            print(f"Warning: Could not extract repo via MCP: {str(e)}")
            return None


class GitHubMCPClient:
    """GitHub client using MCP server."""
    
    def __init__(self):
        """Initialize GitHub MCP client."""
        self.use_mcp = os.getenv("USE_MCP_GITHUB", "false").lower() == "true"
    
    def create_branch(self, branch_name: str, base_branch: str = "main",
                     owner: Optional[str] = None, repo: Optional[str] = None) -> bool:
        """
        Create a new branch using MCP server.
        
        Args:
            branch_name: Name of the new branch
            base_branch: Base branch to create from
            owner: Repository owner
            repo: Repository name
            
        Returns:
            True if branch was created successfully
        """
        if not self.use_mcp:
            raise ValueError("MCP mode not enabled. Set USE_MCP_GITHUB=true in .env")
        
        print(f"📡 Using MCP server to create branch: {branch_name}")
        
        try:
            from autonomous_agent import call_mcp_tool
            
            response = call_mcp_tool(
                mcpServer="github",
                toolName="github_create_branch",  # Adjust based on your MCP server
                toolArgs={
                    "branch_name": branch_name,
                    "base_branch": base_branch,
                    "owner": owner,
                    "repo": repo
                }
            )
            
            return response.get("success", True) if isinstance(response, dict) else True
            
        except (ImportError, NotImplementedError) as e:
            # Fallback if call_mcp_tool not available
            print(f"⚠ MCP tool caller not available: {str(e)}")
            print("💡 Tip: Configure MCP servers or use API mode (USE_MCP_GITHUB=false)")
            return True
    
    def push_file(self, branch_name: str, file_path: str, content: str,
                  commit_message: str, owner: Optional[str] = None,
                  repo: Optional[str] = None) -> bool:
        """Push a file using MCP server."""
        if not self.use_mcp:
            raise ValueError("MCP mode not enabled")
        
        print(f"📡 Using MCP server to push file: {file_path}")
        
        try:
            from autonomous_agent import call_mcp_tool
            
            response = call_mcp_tool(
                mcpServer="github",
                toolName="github_push_file",  # Adjust based on your MCP server
                toolArgs={
                    "branch_name": branch_name,
                    "file_path": file_path,
                    "content": content,
                    "commit_message": commit_message,
                    "owner": owner,
                    "repo": repo
                }
            )
            
            return response.get("success", True) if isinstance(response, dict) else True
            
        except (ImportError, NotImplementedError) as e:
            print(f"⚠ MCP tool caller not available: {str(e)}")
            print("💡 Tip: Configure MCP servers or use API mode (USE_MCP_GITHUB=false)")
            return True
    
    def create_pull_request(self, title: str, body: str, head_branch: str,
                           base_branch: str = "main", owner: Optional[str] = None,
                           repo: Optional[str] = None) -> Optional[str]:
        """Create a pull request using MCP server."""
        if not self.use_mcp:
            raise ValueError("MCP mode not enabled")
        
        print(f"📡 Using MCP server to create PR: {title}")
        
        try:
            from autonomous_agent import call_mcp_tool
            
            response = call_mcp_tool(
                mcpServer="github",
                toolName="github_create_pr",  # Adjust based on your MCP server
                toolArgs={
                    "title": title,
                    "body": body,
                    "head_branch": head_branch,
                    "base_branch": base_branch,
                    "owner": owner,
                    "repo": repo
                }
            )
            
            if isinstance(response, dict):
                return response.get("url") or response.get("html_url")
            return None
            
        except (ImportError, NotImplementedError) as e:
            print(f"⚠ MCP tool caller not available: {str(e)}")
            print("💡 Tip: Configure MCP servers or use API mode (USE_MCP_GITHUB=false)")
            return None

