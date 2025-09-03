import os
from agent.dispute_agent import DisputeResolutionAgent
from data.sample_data import transaction_history, customer_interactions, policies

def main():
    """
    Main function to demonstrate the Dispute Resolution Agent with AWS Bedrock
    """
    print("=== Dispute Resolution Agent Demo ===\n")
    
    # Initialize the agent with policies
    try:
        agent = DisputeResolutionAgent(policies, aws_region="us-east-1")
        print("✓ Agent initialized successfully with AWS Bedrock")
    except Exception as e:
        print(f"⚠ Agent initialization warning: {e}")
        print("Continuing with limited functionality...")
        agent = DisputeResolutionAgent(policies)
    
    print(f"\n--- Case Details ---")
    print("Transaction History:")
    print(transaction_history)
    print("\nCustomer Interactions:")
    print(customer_interactions)
    
    # Step 1: Classify the dispute
    print(f"\n--- Step 1: Dispute Classification ---")
    dispute_type = agent.classify_dispute(transaction_history, customer_interactions)
    print(f"Dispute Type: {dispute_type}")
    
    # Step 2: Suggest next action using RAG
    print(f"\n--- Step 2: Next Action Suggestion ---")
    next_action = agent.suggest_next_action(dispute_type, transaction_history, customer_interactions)
    print(f"Suggested Next Action:\n{next_action}")
    
    # Step 3: Generate draft response
    print(f"\n--- Step 3: Draft Customer Response ---")
    draft_response = agent.generate_draft_response(dispute_type, next_action, customer_name="John Doe")
    print(f"Draft Response:\n{draft_response}")
    
    print(f"\n=== Demo Complete ===")

if __name__ == "__main__":
    # Set up environment variables for AWS (if not already configured)
    # Uncomment and set these if needed:
    # os.environ['AWS_ACCESS_KEY_ID'] = 'your-access-key'
    # os.environ['AWS_SECRET_ACCESS_KEY'] = 'your-secret-key'
    # os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    main()
