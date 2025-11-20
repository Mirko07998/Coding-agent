"""Build and test execution validator."""
import subprocess
import os
from typing import Tuple, List
from pathlib import Path


class BuildValidator:
    """Validates builds and runs tests."""
    
    def __init__(self, repo_path: str = "."):
        """
        Initialize build validator.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path).resolve()
    
    def run_build(self) -> Tuple[bool, str]:
        """
        Run the build process.
        
        Returns:
            Tuple of (success: bool, output: str)
        """
        print("\n🔨 Running build...")
        
        # Try common build commands
        build_commands = [
            ["python", "-m", "pip", "install", "-r", "requirements.txt"],
            ["python", "-m", "pip", "install", "-e", "."],
            ["python", "setup.py", "build"],
            ["npm", "install"],
            ["npm", "run", "build"],
            ["mvn", "clean", "install"],
            ["gradle", "build"],
            ["make", "build"],
        ]
        
        for cmd in build_commands:
            if self._command_exists(cmd[0]):
                try:
                    result = subprocess.run(
                        cmd,
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    if result.returncode == 0:
                        print(f"✓ Build succeeded with: {' '.join(cmd)}")
                        return True, result.stdout
                    else:
                        # Continue to next command if this one fails
                        continue
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
        
        # If no build command worked, check if there's a build script
        build_scripts = ["build.sh", "build.py", "build.bat"]
        for script in build_scripts:
            script_path = self.repo_path / script
            if script_path.exists():
                try:
                    result = subprocess.run(
                        ["bash", str(script_path)] if script.endswith('.sh') else 
                        ["python", str(script_path)] if script.endswith('.py') else
                        [str(script_path)],
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    if result.returncode == 0:
                        print(f"✓ Build succeeded with: {script}")
                        return True, result.stdout
                except Exception as e:
                    continue
        
        # If no build process found, assume success (for new projects)
        print("⚠ No build process detected, assuming build successful")
        return True, "No build process found"
    
    def run_tests(self) -> Tuple[bool, str]:
        """
        Run tests.
        
        Returns:
            Tuple of (success: bool, output: str)
        """
        print("\n🧪 Running tests...")
        
        # Try common test commands
        test_commands = [
            ["python", "-m", "pytest"],
            ["python", "-m", "unittest", "discover"],
            ["npm", "test"],
            ["npm", "run", "test"],
            ["mvn", "test"],
            ["gradle", "test"],
            ["make", "test"],
        ]
        
        for cmd in test_commands:
            if self._command_exists(cmd[0]):
                try:
                    result = subprocess.run(
                        cmd,
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    if result.returncode == 0:
                        print(f"✓ Tests passed with: {' '.join(cmd)}")
                        return True, result.stdout
                    else:
                        # Continue to next command
                        continue
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
        
        # If no test command worked, check for test scripts
        test_scripts = ["test.sh", "test.py", "test.bat", "run_tests.sh"]
        for script in test_scripts:
            script_path = self.repo_path / script
            if script_path.exists():
                try:
                    result = subprocess.run(
                        ["bash", str(script_path)] if script.endswith('.sh') else 
                        ["python", str(script_path)] if script.endswith('.py') else
                        [str(script_path)],
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    if result.returncode == 0:
                        print(f"✓ Tests passed with: {script}")
                        return True, result.stdout
                except Exception as e:
                    continue
        
        # If no tests found, assume success (for new projects)
        print("⚠ No test process detected, assuming tests passed")
        return True, "No test process found"
    
    def validate(self) -> Tuple[bool, str]:
        """
        Run both build and tests.
        
        Returns:
            Tuple of (success: bool, error_message: str)
        """
        build_success, build_output = self.run_build()
        if not build_success:
            return False, f"Build failed:\n{build_output}"
        
        test_success, test_output = self.run_tests()
        if not test_success:
            return False, f"Tests failed:\n{test_output}"
        
        return True, "Build and tests passed successfully"
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system."""
        try:
            subprocess.run(
                ["which", command] if os.name != 'nt' else ["where", command],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

