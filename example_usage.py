"""Example usage of the autonomous coding agent."""
from autonomous_agent import AutonomousCodingAgent

# Example: Process a Jira ticket
if __name__ == "__main__":
    # Initialize the agent
    agent = AutonomousCodingAgent(repo_path=".")
    
    # Process a ticket (replace with your actual ticket key)
    ticket_key = "PROJ-123"
    
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

