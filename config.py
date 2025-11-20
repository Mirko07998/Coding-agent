"""Configuration management for the autonomous agent."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Jira Configuration
JIRA_SERVER = os.getenv("JIRA_SERVER")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# GitHub Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO_OWNER = os.getenv("GITHUB_REPO_OWNER")
GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Git Configuration
GIT_USER_NAME = os.getenv("GIT_USER_NAME")
GIT_USER_EMAIL = os.getenv("GIT_USER_EMAIL")

def validate_config():
    """Validate that all required configuration is present."""
    required_vars = {
        "Jira": [JIRA_SERVER, JIRA_EMAIL, JIRA_API_TOKEN],
        "GitHub": [GITHUB_TOKEN],
        "OpenAI": [OPENAI_API_KEY]
    }
    
    missing = []
    for service, vars_list in required_vars.items():
        if not all(vars_list):
            missing.append(service)
    
    if missing:
        raise ValueError(
            f"Missing required configuration for: {', '.join(missing)}\n"
            "Please check your .env file."
        )
    
    return True

