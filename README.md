# Autonomous Coding Agent

An autonomous coding agent that processes Jira tickets, generates code using LangChain, validates builds and tests, and automatically pushes to GitHub.

## Features

- 🔗 **Jira Integration**: Fetches ticket information, acceptance criteria, and descriptions
  - Supports both direct API and MCP server integration
- 🤖 **AI Code Generation**: Uses LangChain with OpenAI GPT-4 to generate code based on acceptance criteria
- 🔨 **Build Validation**: Automatically runs build and test processes
- 🌿 **Git Automation**: Creates branches, commits, and pushes to GitHub
  - Supports both direct API and MCP server integration
- ✅ **Quality Gates**: Only pushes code if build and tests pass
- 🔌 **MCP Support**: Optional MCP (Model Context Protocol) server integration for Jira and GitHub

## Prerequisites

- Python 3.8+
- Git installed and configured
- Access to Jira API
- GitHub Personal Access Token
- OpenAI API Key

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd LangChainProject
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

4. Configure your `.env` file with the following variables:

```env
# Jira Configuration
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token

# GitHub Configuration
GITHUB_TOKEN=your-github-personal-access-token
GITHUB_REPO_OWNER=your-username
GITHUB_REPO_NAME=your-repo-name

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Git Configuration
GIT_USER_NAME=Your Name
GIT_USER_EMAIL=your-email@example.com

# MCP Configuration (Optional)
# Set to 'true' to use MCP servers instead of direct API calls
USE_MCP_JIRA=false
USE_MCP_GITHUB=false
```

### Getting API Tokens

#### Jira API Token
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the token to `JIRA_API_TOKEN`

#### GitHub Personal Access Token
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate a new token with `repo` scope
3. Copy the token to `GITHUB_TOKEN`

#### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key to `OPENAI_API_KEY`

## Usage

### Basic Usage

Process a Jira ticket:
```bash
python autonomous_agent.py PROJ-123
```

### Advanced Usage

Specify a different repository path:
```bash
python autonomous_agent.py PROJ-123 --repo-path /path/to/repo
```

Skip pushing to GitHub (useful for testing):
```bash
python autonomous_agent.py PROJ-123 --no-push
```

## How It Works

The agent follows these steps:

1. **Fetch Ticket**: Connects to Jira and retrieves ticket information, including:
   - Summary and description
   - Acceptance criteria
   - Status and metadata

2. **Create Branch**: Creates a new Git branch named after the ticket (e.g., `proj-123`)

3. **Analyze Repository**: Scans the repository structure to understand existing code

4. **Generate Code**: Uses LangChain with GPT-4 to generate code that fulfills the acceptance criteria

5. **Write Files**: Saves generated code files to the repository

6. **Stage & Commit**: Adds files to Git and commits with a descriptive message

7. **Validate**: Runs build and test processes to ensure code quality

8. **Push**: If validation passes, pushes the branch to GitHub

## Workflow

```
┌─────────────┐
│ Jira Ticket │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Fetch Ticket Info│
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Create Branch   │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Generate Code    │
│  (LangChain AI)  │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Commit Changes  │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Run Build/Test  │
└──────┬───────────┘
       │
       ▼
    ┌─────┐
    │Pass?│
    └─┬─┬─┘
      │ │
   Yes│ │No
      │ │
      ▼ ▼
  ┌───────┐  ┌──────────┐
  │ Push  │  │ Report   │
  │  to   │  │ Errors   │
  │ GitHub│  └──────────┘
  └───────┘
```

## Project Structure

```
LangChainProject/
├── autonomous_agent.py      # Main orchestration script
├── jira_client.py           # Jira API integration
├── github_client.py         # GitHub API integration
├── code_generator.py        # LangChain code generation
├── build_validator.py       # Build and test validation
├── git_operations.py        # Git operations
├── requirements.txt         # Python dependencies
├── .env                     # Configuration (create from .env.example)
└── README.md               # This file
```

## Supported Build Systems

The agent automatically detects and runs:
- Python: `pip install`, `pytest`, `unittest`
- Node.js: `npm install`, `npm test`
- Java: `mvn`, `gradle`
- Custom: `build.sh`, `test.sh` scripts

## Error Handling

- If build fails: Code is committed locally but not pushed to GitHub
- If tests fail: Same behavior as build failure
- All errors are reported in the output and summary

## Limitations

- Requires acceptance criteria to be clearly defined in the Jira ticket
- Generated code quality depends on the clarity of requirements
- Build/test detection may need adjustment for custom setups
- Large codebases may require more context in prompts

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## MCP Server Support

This agent supports using MCP (Model Context Protocol) servers instead of direct API calls for Jira and GitHub. This provides a more standardized and flexible approach to integration.

To enable MCP mode:
1. Set `USE_MCP_JIRA=true` and/or `USE_MCP_GITHUB=true` in your `.env` file
2. Configure MCP servers in your MCP framework (e.g., Cursor settings)
3. The agent will automatically use MCP servers when enabled

See [MCP_SETUP.md](MCP_SETUP.md) for detailed setup instructions.

## Support

For issues or questions, please open an issue in the repository.

