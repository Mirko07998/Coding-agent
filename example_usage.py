"""Example usage of the autonomous coding agent."""
import os
from autonomous_agent import AutonomousCodingAgent

# Example: Process a Jira ticket
if __name__ == "__main__":
    # For testing: Use file mode instead of Jira API
    # Option 1: Set environment variable
    os.environ["JIRA_USE_FILE"] = "true"
    os.environ["JIRA_FILE_PATH"] = "/Users/DJM8BG/PycharmProjects/Coding-agent/test_ticket.json"  # Optional, defaults to test_ticket.json
    
    # Option 2: Modify jira_client.py initialization in autonomous_agent.py
    # to pass use_file=True to JiraClient()
    
    # Initialize the agent
    agent = AutonomousCodingAgent(repo_path=".")
    
    # Process a ticket (replace with your actual ticket key)
    # In file mode, the ticket_key is ignored and data is read from the file
    ticket_key = "TEST-123"  # or "PROJ-123" for real Jira tickets
    
    print(f"Processing ticket: {ticket_key}")
    results = agent.process_ticket(ticket_key, push_to_github=True)
    
    # Print results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Success: {results['success']}")
    print(f"Branch: {results['branch_name']}")
    print(f"Files Generated: {results['files_generated']}")
    print(f"Build Success: {results['build_success']}")
    print(f"Pushed: {results['pushed']}")
    
    if results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")

