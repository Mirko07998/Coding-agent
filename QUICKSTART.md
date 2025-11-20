# Quick Start Guide

## Setup (5 minutes)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file:**
   ```bash
   # Copy and edit with your credentials
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Configure your `.env` file:**
   - Get Jira API token from: https://id.atlassian.com/manage-profile/security/api-tokens
   - Get GitHub token from: https://github.com/settings/tokens (with `repo` scope)
   - Get OpenAI API key from: https://platform.openai.com/api-keys

## Usage

### Process a single ticket:
```bash
python autonomous_agent.py PROJ-123
```

### Process without pushing (for testing):
```bash
python autonomous_agent.py PROJ-123 --no-push
```

### Process with custom repo path:
```bash
python autonomous_agent.py PROJ-123 --repo-path /path/to/your/repo
```

## What Happens

1. ✅ Fetches ticket from Jira
2. ✅ Creates branch named after ticket (e.g., `proj-123`)
3. ✅ Generates code using AI based on acceptance criteria
4. ✅ Commits code to branch
5. ✅ Runs build and tests
6. ✅ Pushes to GitHub (if build/tests pass)

## Troubleshooting

### "Missing Jira credentials"
- Check your `.env` file has `JIRA_SERVER`, `JIRA_EMAIL`, and `JIRA_API_TOKEN`

### "Failed to access repository"
- Verify `GITHUB_TOKEN` has `repo` scope
- Check `GITHUB_REPO_OWNER` and `GITHUB_REPO_NAME` are correct

### "Missing OPENAI_API_KEY"
- Add your OpenAI API key to `.env`

### Build/Test failures
- The agent will not push if build or tests fail
- Check the error output to fix issues
- Re-run after fixing

## Example Output

```
============================================================
🚀 Processing Jira Ticket: PROJ-123
============================================================

📋 Step 1: Fetching ticket information from Jira...
✓ Ticket: Add user authentication
  Status: In Progress
  URL: https://your-domain.atlassian.net/browse/PROJ-123

🌿 Step 2: Creating branch...
✓ Created and checked out branch: proj-123

📁 Step 3: Analyzing repository structure...
✓ Found 15 files in repository

💻 Step 4: Generating code from acceptance criteria...
🤖 Generating code for ticket: PROJ-123
✓ Generated 3 file(s)

📝 Step 5: Writing generated files...
  ✓ Created: src/auth.py
  ✓ Created: tests/test_auth.py
  ✓ Created: requirements.txt

📦 Step 6: Staging files...
✓ Added to staging: src/auth.py
✓ Added to staging: tests/test_auth.py

💾 Step 7: Committing changes...
✓ Committed: PROJ-123: Add user authentication

✅ Step 8: Validating build and tests...
🔨 Running build...
✓ Build succeeded with: python -m pip install -r requirements.txt
🧪 Running tests...
✓ Tests passed with: python -m pytest

🚀 Step 9: Pushing to GitHub...
✓ Pushed branch proj-123 to origin

============================================================
✅ Successfully processed ticket: PROJ-123
============================================================
```

