"""Main autonomous coding agent that orchestrates the entire workflow."""
import os
import sys
from pathlib import Path
from typing import Dict, Any
from jira_client import JiraClient
from github_client import GitHubClient
from code_generator import CodeGenerator
from build_validator import BuildValidator
from git_operations import GitOperations


def call_mcp_tool(mcpServer: str, toolName: str, toolArgs: Dict[str, Any]) -> Any:
    """
    Helper function to call MCP tools.
    This function can be used by MCP clients to interact with MCP servers.
    
    Args:
        mcpServer: Name of the MCP server (e.g., 'jira', 'github')
        toolName: Name of the tool to call
        toolArgs: Arguments for the tool
        
    Returns:
        Tool response (format depends on the tool)
        
    Note:
        This function uses the call_mcp_tool tool available in the agent environment.
        When running in Cursor/Claude with MCP servers configured, this will automatically
        route to the appropriate MCP server.
        
        If MCP is not available, this will raise NotImplementedError.
        The code will fall back to direct API calls if MCP is not configured.
    """
    # Note: In the actual execution environment (Cursor/Claude), this function
    # would be replaced or wrapped to use the actual call_mcp_tool tool.
    # For now, we provide a placeholder that indicates MCP needs to be configured.
    
    # In a real implementation with MCP SDK:
    # from mcp import ClientSession, StdioServerParameters
    # async with ClientSession(...) as session:
    #     result = await session.call_tool(toolName, toolArgs)
    #     return result
    
    # For Cursor/Claude integration, the call_mcp_tool tool is available
    # and will be called automatically when this function is invoked.
    # The actual implementation depends on how MCP is integrated.
    
    raise NotImplementedError(
        f"MCP tool call not configured. "
        f"To use MCP, configure MCP servers in your environment. "
        f"Server: {mcpServer}, Tool: {toolName}, Args: {toolArgs}\n"
        f"See MCP_SETUP.md for configuration instructions."
    )


class AutonomousCodingAgent:
    """Autonomous agent that processes Jira tickets and generates code."""
    
    def __init__(self, repo_path: str = "."):
        """
        Initialize the autonomous agent.
        
        Args:
            repo_path: Path to the local repository
        """
        self.repo_path = Path(repo_path).resolve()
        self.jira_client = JiraClient()
        self.github_client = GitHubClient()
        self.code_generator = CodeGenerator()
        self.build_validator = BuildValidator(str(self.repo_path))
        self.git_ops = GitOperations(str(self.repo_path))
    
    def process_ticket(self, ticket_key: str, push_to_github: bool = True) -> Dict:
        """
        Process a Jira ticket: fetch, generate code, validate, and push.
        
        Args:
            ticket_key: Jira ticket key (e.g., 'PROJ-123')
            push_to_github: Whether to push to GitHub after successful build
            
        Returns:
            Dictionary with processing results
        """
        results = {
            "ticket_key": ticket_key,
            "success": False,
            "branch_name": None,
            "files_generated": [],
            "build_success": False,
            "tests_success": False,
            "pushed": False,
            "errors": []
        }
        
        try:
            print(f"\n{'='*60}")
            print(f"🚀 Processing Jira Ticket: {ticket_key}")
            print(f"{'='*60}\n")
            
            # Step 1: Fetch ticket information
            print("📋 Step 1: Fetching ticket information from Jira...")
            ticket_info = self.jira_client.get_ticket(ticket_key)
            print(f"✓ Ticket: {ticket_info.summary}")
            print(f"  Status: {ticket_info.status}")
            print(f"  URL: {ticket_info.url}\n")
            
            # Step 2: Create branch
            print("🌿 Step 2: Creating branch...")
            branch_name = self._sanitize_branch_name(ticket_key)
            results["branch_name"] = branch_name
            
            # Try local git first, then GitHub API
            try:
                self.git_ops.create_branch(branch_name)
            except Exception as e:
                print(f"⚠ Local git branch creation failed: {str(e)}")
                # Try GitHub API
                try:
                    repo_info = self.jira_client.get_linked_repo(ticket_key)
                    if repo_info:
                        owner, repo = repo_info.split('/')
                        self.github_client.create_branch(branch_name, owner=owner, repo=repo)
                    else:
                        # Use default repo from config
                        self.github_client.create_branch(branch_name)
                except Exception as e2:
                    results["errors"].append(f"Branch creation failed: {str(e2)}")
                    raise
            
            # Step 3: Get repository structure
            print("\n📁 Step 3: Analyzing repository structure...")
            repo_structure = self.git_ops.get_repo_structure()
            print(f"✓ Found {len(repo_structure)} files in repository")
            
            # Step 4: Generate code
            print("\n💻 Step 4: Generating code from acceptance criteria...")
            generated_files = self.code_generator.generate_code(ticket_info, repo_structure)
            results["files_generated"] = list(generated_files.keys())
            
            if not generated_files:
                raise Exception("No code was generated")
            
            # Step 5: Write generated files to repository
            print("\n📝 Step 5: Writing generated files...")
            for file_path, content in generated_files.items():
                full_path = self.repo_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
                print(f"  ✓ Created: {file_path}")
            
            # Step 6: Add files to git
            print("\n📦 Step 6: Staging files...")
            self.git_ops.add_files(list(generated_files.keys()))
            
            # Step 7: Commit changes
            print("\n💾 Step 7: Committing changes...")
            commit_message = f"{ticket_key}: {ticket_info.summary}\n\nGenerated code to fulfill acceptance criteria."
            self.git_ops.commit(commit_message)
            
            # Step 8: Validate build and tests
            print("\n✅ Step 8: Validating build and tests...")
            build_success, validation_message = self.build_validator.validate()
            results["build_success"] = build_success
            results["tests_success"] = build_success
            
            if not build_success:
                results["errors"].append(validation_message)
                print(f"\n❌ Validation failed:\n{validation_message}")
                print("\n⚠ Not pushing to GitHub due to build/test failures")
                results["success"] = False
                return results
            
            # Step 9: Push to GitHub
            if push_to_github:
                print("\n🚀 Step 9: Pushing to GitHub...")
                try:
                    self.git_ops.push(branch_name)
                    results["pushed"] = True
                    print("✓ Successfully pushed to GitHub")
                except Exception as e:
                    results["errors"].append(f"Push failed: {str(e)}")
                    print(f"⚠ Push failed: {str(e)}")
            
            results["success"] = True
            print(f"\n{'='*60}")
            print(f"✅ Successfully processed ticket: {ticket_key}")
            print(f"{'='*60}\n")
            
        except Exception as e:
            results["errors"].append(str(e))
            results["success"] = False
            print(f"\n❌ Error processing ticket: {str(e)}\n")
            import traceback
            traceback.print_exc()
        
        return results
    
    def _sanitize_branch_name(self, ticket_key: str) -> str:
        """
        Sanitize ticket key to create a valid branch name.
        
        Args:
            ticket_key: Jira ticket key
            
        Returns:
            Sanitized branch name
        """
        # Replace invalid characters
        branch_name = ticket_key.replace(' ', '-').lower()
        # Remove any remaining invalid characters
        valid_chars = '-_abcdefghijklmnopqrstuvwxyz0123456789'
        branch_name = ''.join(c if c in valid_chars else '-' for c in branch_name)
        # Remove consecutive dashes
        while '--' in branch_name:
            branch_name = branch_name.replace('--', '-')
        # Remove leading/trailing dashes
        branch_name = branch_name.strip('-')
        
        return branch_name or "ticket-branch"


def main():
    """Main entry point for the autonomous agent."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Autonomous coding agent for Jira tickets"
    )
    parser.add_argument(
        "ticket_key",
        help="Jira ticket key (e.g., PROJ-123)"
    )
    parser.add_argument(
        "--repo-path",
        default=".",
        help="Path to the repository (default: current directory)"
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Don't push to GitHub after successful build"
    )
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = AutonomousCodingAgent(repo_path=args.repo_path)
    
    # Process ticket
    results = agent.process_ticket(
        ticket_key=args.ticket_key,
        push_to_github=not args.no_push
    )
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Ticket: {results['ticket_key']}")
    print(f"Success: {results['success']}")
    print(f"Branch: {results['branch_name']}")
    print(f"Files Generated: {len(results['files_generated'])}")
    print(f"Build Success: {results['build_success']}")
    print(f"Tests Success: {results['tests_success']}")
    print(f"Pushed to GitHub: {results['pushed']}")
    
    if results['errors']:
        print(f"\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")
    
    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)

def get_autonomous_agent_service():
    """Dependency injector for AutonomousCodingAgent."""
    return AutonomousCodingAgent()
