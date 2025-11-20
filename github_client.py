"""GitHub API client for repository operations."""
import os
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

# Try to import MCP client
try:
    from mcp_client import GitHubMCPClient
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# Try to import GitHub API client
try:
    from github import Github
    GITHUB_API_AVAILABLE = True
except ImportError:
    GITHUB_API_AVAILABLE = False


class GitHubClient:
    """Client for interacting with GitHub API or MCP server."""
    
    def __init__(self, use_mcp: Optional[bool] = None):
        """
        Initialize GitHub client with token from environment.
        
        Args:
            use_mcp: Force MCP mode if True, API mode if False, auto-detect if None
        """
        self.use_mcp = use_mcp
        if self.use_mcp is None:
            self.use_mcp = os.getenv("USE_MCP_GITHUB", "false").lower() == "true"
        
        if self.use_mcp and MCP_AVAILABLE:
            # Use MCP client
            self.mcp_client = GitHubMCPClient()
            self.client = None
            print("🔌 Using MCP server for GitHub")
        else:
            # Use API client
            if not GITHUB_API_AVAILABLE:
                raise ImportError("PyGithub package not installed. Install with: pip install PyGithub")
            
            self.token = os.getenv("GITHUB_TOKEN")
            if not self.token:
                raise ValueError("Missing GITHUB_TOKEN in .env")
            
            self.client = Github(self.token)
            self.mcp_client = None
            self.repo_owner = os.getenv("GITHUB_REPO_OWNER")
            self.repo_name = os.getenv("GITHUB_REPO_NAME")
            print("🔌 Using API for GitHub")
    
    def get_repo(self, owner: Optional[str] = None, repo: Optional[str] = None):
        """
        Get repository object.
        
        Args:
            owner: Repository owner (defaults to GITHUB_REPO_OWNER)
            repo: Repository name (defaults to GITHUB_REPO_NAME)
            
        Returns:
            Repository object
        """
        owner = owner or self.repo_owner
        repo = repo or self.repo_name
        
        if not owner or not repo:
            raise ValueError("Repository owner and name must be specified")
        
        try:
            return self.client.get_repo(f"{owner}/{repo}")
        except Exception as e:
            raise Exception(f"Failed to access repository {owner}/{repo}: {str(e)}")
    
    def create_branch(self, branch_name: str, base_branch: str = "main", 
                     owner: Optional[str] = None, repo: Optional[str] = None) -> bool:
        """
        Create a new branch in the repository.
        
        Args:
            branch_name: Name of the new branch
            base_branch: Base branch to create from (default: main)
            owner: Repository owner
            repo: Repository name
            
        Returns:
            True if branch was created successfully
        """
        # Use MCP if enabled
        if self.use_mcp and self.mcp_client:
            return self.mcp_client.create_branch(branch_name, base_branch, owner, repo)
        
        # Otherwise use API
        try:
            repository = self.get_repo(owner, repo)
            
            # Get the base branch reference
            base_ref = repository.get_git_ref(f"heads/{base_branch}")
            
            # Create new branch
            repository.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base_ref.object.sha
            )
            
            print(f"✓ Created branch: {branch_name}")
            return True
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"⚠ Branch {branch_name} already exists")
                return True
            raise Exception(f"Failed to create branch {branch_name}: {str(e)}")
    
    def push_file(self, branch_name: str, file_path: str, content: str, 
                  commit_message: str, owner: Optional[str] = None, 
                  repo: Optional[str] = None) -> bool:
        """
        Push a file to a branch.
        
        Args:
            branch_name: Branch to push to
            file_path: Path of the file in the repository
            content: File content
            commit_message: Commit message
            owner: Repository owner
            repo: Repository name
            
        Returns:
            True if file was pushed successfully
        """
        # Use MCP if enabled
        if self.use_mcp and self.mcp_client:
            return self.mcp_client.push_file(branch_name, file_path, content, commit_message, owner, repo)
        
        # Otherwise use API
        try:
            repository = self.get_repo(owner, repo)
            
            # Get the branch
            branch = repository.get_branch(branch_name)
            
            # Get the current file if it exists
            try:
                file = repository.get_contents(file_path, ref=branch_name)
                # Update existing file
                repository.update_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    sha=file.sha,
                    branch=branch_name
                )
            except:
                # Create new file
                repository.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    branch=branch_name
                )
            
            print(f"✓ Pushed file: {file_path}")
            return True
        except Exception as e:
            raise Exception(f"Failed to push file {file_path}: {str(e)}")
    
    def create_pull_request(self, title: str, body: str, head_branch: str,
                           base_branch: str = "main", owner: Optional[str] = None,
                           repo: Optional[str] = None) -> Optional[str]:
        """
        Create a pull request.
        
        Args:
            title: PR title
            body: PR description
            head_branch: Source branch
            base_branch: Target branch (default: main)
            owner: Repository owner
            repo: Repository name
            
        Returns:
            PR URL or None if creation failed
        """
        # Use MCP if enabled
        if self.use_mcp and self.mcp_client:
            return self.mcp_client.create_pull_request(title, body, head_branch, base_branch, owner, repo)
        
        # Otherwise use API
        try:
            repository = self.get_repo(owner, repo)
            pr = repository.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            print(f"✓ Created pull request: {pr.html_url}")
            return pr.html_url
        except Exception as e:
            print(f"⚠ Failed to create pull request: {str(e)}")
            return None

