"""Git operations for branch creation, commit, and push."""
import os
from pathlib import Path
from typing import Optional
from git import Repo, GitCommandError
from dotenv import load_dotenv

load_dotenv()


class GitOperations:
    """Handles Git operations for the repository."""
    
    def __init__(self, repo_path: str = "."):
        """
        Initialize Git operations.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path).resolve()
        try:
            self.repo = Repo(self.repo_path)
        except Exception as e:
            raise Exception(f"Not a valid Git repository: {str(e)}")
        
        # Configure git user if not set
        self._configure_git_user()
    
    def _configure_git_user(self):
        """Configure git user name and email from environment."""
        git_name = os.getenv("GIT_USER_NAME")
        git_email = os.getenv("GIT_USER_EMAIL")
        
        if git_name:
            self.repo.config_writer().set_value("user", "name", git_name).release()
        if git_email:
            self.repo.config_writer().set_value("user", "email", git_email).release()
    
    def create_branch(self, branch_name: str, base_branch: str = "main") -> bool:
        """
        Create a new branch.
        
        Args:
            branch_name: Name of the new branch
            base_branch: Base branch to create from
            
        Returns:
            True if branch was created successfully
        """
        try:
            # Check if branch already exists
            if branch_name in [ref.name.split('/')[-1] for ref in self.repo.refs]:
                print(f"⚠ Branch {branch_name} already exists, checking it out")
                self.repo.git.checkout(branch_name)
                return True
            
            # Create and checkout new branch
            self.repo.git.checkout(base_branch)
            self.repo.git.pull()
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            
            print(f"✓ Created and checked out branch: {branch_name}")
            return True
        except GitCommandError as e:
            raise Exception(f"Failed to create branch {branch_name}: {str(e)}")
    
    def add_files(self, file_paths: list):
        """
        Add files to staging area.
        
        Args:
            file_paths: List of file paths to add
        """
        try:
            for file_path in file_paths:
                full_path = self.repo_path / file_path
                if full_path.exists():
                    self.repo.index.add([file_path])
                    print(f"✓ Added to staging: {file_path}")
                else:
                    print(f"⚠ File not found: {file_path}")
        except Exception as e:
            raise Exception(f"Failed to add files: {str(e)}")
    
    def commit(self, message: str) -> bool:
        """
        Commit staged changes.
        
        Args:
            message: Commit message
            
        Returns:
            True if commit was successful
        """
        try:
            if not self.repo.index.diff("HEAD") and not self.repo.untracked_files:
                print("⚠ No changes to commit")
                return False
            
            self.repo.index.commit(message)
            print(f"✓ Committed: {message}")
            return True
        except Exception as e:
            raise Exception(f"Failed to commit: {str(e)}")
    
    def push(self, branch_name: str, remote: str = "origin", force: bool = False) -> bool:
        """
        Push branch to remote repository.
        
        Args:
            branch_name: Branch to push
            remote: Remote name (default: origin)
            force: Whether to force push
            
        Returns:
            True if push was successful
        """
        try:
            remote_repo = self.repo.remote(remote)
            if force:
                remote_repo.push(branch_name, force=True)
            else:
                remote_repo.push(branch_name)
            
            print(f"✓ Pushed branch {branch_name} to {remote}")
            return True
        except GitCommandError as e:
            raise Exception(f"Failed to push branch {branch_name}: {str(e)}")
    
    def get_current_branch(self) -> str:
        """Get the current branch name."""
        return self.repo.active_branch.name
    
    def get_repo_structure(self) -> list:
        """
        Get list of files in the repository.
        
        Returns:
            List of file paths
        """
        files = []
        for root, dirs, filenames in os.walk(self.repo_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.git']]
            
            for filename in filenames:
                if not filename.startswith('.'):
                    rel_path = os.path.relpath(os.path.join(root, filename), self.repo_path)
                    files.append(rel_path)
        
        return files

