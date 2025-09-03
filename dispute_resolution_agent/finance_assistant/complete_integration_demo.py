"""
Complete Personal Finance Assistant Integration Demo
Shows real-world usage with statement parsing and RAG integration
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from finance_assistant.personal_finance_ai import PersonalFinanceAssistant
from finance_assistant.statement_parser import StatementParser, parse_statement_from_text
from finance_assistant.sample_financial_data import sample_user_goals

def demo_statement_parsing():
    """Demonstrate parsing a real statement format"""
    print("=" * 70)
    print("📄 STATEMENT PARSING DEMO")
    print("=" * 70)
    
    # Sample statement text (as might come from OCR or copy-paste)
    raw_statement = """
    CREDIT CARD STATEMENT - September 2025
    
    Account: ****1234
    Statement Date: 09/30/2025
    
    Previous Balance: $3,500.75
    Payments: $1,000.00
    New Charges: $2,180.40
    Interest Charged: $68.92
    Current Balance: $4,681.15
    
    Credit Limit: $10,000.00
    Available Credit: $5,318.85
    Minimum Payment Due: $140.44
    Payment Due Date: 10/15/2025
    
    TRANSACTION DETAILS:
    09/01  Whole Foods Market         $78.45
    09/02  Shell Gas Station         $52.30  
    09/03  Amazon.com                $156.78
    09/05  Starbucks                 $12.85
    09/07  Delta Air Lines           $485.00
    09/10  Target Store              $134.22
    09/12  Olive Garden              $67.90
    """
    
    # Parse the statement
    parser = StatementParser()
    parsed_data = parser.parse_statement_text(raw_statement)
    
    print("✅ Statement parsed successfully!")
    print(f"📊 Extracted Data:")
    for key, value in parsed_data.items():
        if isinstance(value, (int, float)):
            print(f"   {key.replace('_', ' ').title()}: ${value:,.2f}")
        elif key not in ['raw_text', 'parsing_method']:
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    return parsed_data

def demo_csv_transaction_parsing():
    """Demonstrate parsing transaction CSV data"""
    print(f"\n" + "=" * 70)
    print("💳 TRANSACTION CSV PARSING DEMO")
    print("=" * 70)
    
    # Sample CSV data
    csv_data = """Date,Description,Amount,Category
09/01/2025,Whole Foods Market,-78.45,Groceries
09/02/2025,Shell Gas Station,-52.30,Gas
09/03/2025,Amazon.com,-156.78,Shopping
09/05/2025,Starbucks,-12.85,Dining
09/07/2025,Delta Air Lines,-485.00,Travel
09/10/2025,Target Store,-134.22,Shopping
09/12/2025,Olive Garden,-67.90,Dining
09/15/2025,Chevron,-48.75,Gas
09/18/2025,Apple Store,-299.99,Shopping
09/22/2025,Marriott Hotel,-148.00,Travel"""
    
    parser = StatementParser()
    transactions = parser.parse_csv_transactions(csv_data)
    
    print(f"✅ Parsed {len(transactions)} transactions")
    print(f"📊 Sample Transactions:")
    for i, tx in enumerate(transactions[:3], 1):
        print(f"   {i}. {tx['date']} - {tx['merchant']} - ${abs(tx['amount']):,.2f}")
    
    # Categorize transactions
    categories = parser.categorize_transactions(transactions)
    print(f"\n📈 Spending by Category:")
    for category, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"   {category}: ${amount:,.2f}")
    
    return transactions, categories

def demo_integrated_analysis():
    """Show complete integration: parsing + AI analysis + recommendations"""
    print(f"\n" + "=" * 70)
    print("🤖 INTEGRATED AI ANALYSIS")
    print("=" * 70)
    
    # Parse statement (from previous demo)
    parsed_statement = demo_statement_parsing()
    
    # Parse transactions 
    transactions, categories = demo_csv_transaction_parsing()
    
    # Add parsed transaction categories to statement
    parsed_statement['spending_categories'] = categories
    parsed_statement['total_rewards'] = 107234  # Sample rewards balance
    parsed_statement['rewards_earned'] = 21804  # Points from spending
    
    # Initialize AI assistant
    assistant = PersonalFinanceAssistant()
    
    print(f"\n🧠 Generating AI-Powered Insights...")
    
    # Generate complete analysis
    report = assistant.generate_financial_report(parsed_statement, sample_user_goals)
    
    print(f"\n📖 AI EXPLANATION:")
    print("-" * 50)
    print(report['statement_explanation'])
    
    print(f"\n💡 SMART NUDGES:")
    print("-" * 50)
    for i, nudge in enumerate(report['personalized_nudges'], 1):
        print(f"{i}. {nudge}")
    
    print(f"\n🔮 SCENARIO PLANNING:")
    print("-" * 50)
    for scenario, analysis in report['scenario_analysis'].items():
        print(f"\n{scenario}:")
        print(f"   {analysis['summary']}")
    
    return report

def demo_rag_financial_advice():
    """Demonstrate RAG-powered financial advice"""
    print(f"\n" + "=" * 70)
    print("📚 RAG-POWERED FINANCIAL ADVICE")
    print("=" * 70)
    
    assistant = PersonalFinanceAssistant()
    
    # Sample user questions
    questions = [
        "How can I reduce my credit card interest payments?",
        "What's the best strategy for paying off debt?", 
        "How do I optimize my credit card rewards?",
        "Should I focus on building an emergency fund or paying off debt?"
    ]
    
    print("🤔 User Questions & AI Responses:")
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. Q: {question}")
        
        # Use retrieval to find relevant docs
        relevant_docs = assistant._retrieve_relevant_docs(question, top_k=2)
        
        # Create context for AI response
        context = "\n".join([f"- {doc['title']}: {doc['content'][:100]}..." for doc in relevant_docs])
        
        if assistant.bedrock_runtime:
            prompt = f"""
            Answer this personal finance question using the provided context:
            
            Question: {question}
            
            Context: {context}
            
            Provide a helpful, practical answer in 1-2 sentences:
            """
            response = assistant._invoke_claude(prompt, max_tokens=150)
        else:
            # Fallback responses
            fallback_responses = {
                0: "Focus on paying more than the minimum payment to reduce interest charges. Every extra dollar goes directly toward principal.",
                1: "Use the debt avalanche method: pay minimums on all cards, then put extra money toward the highest interest rate debt first.", 
                2: "Always pay your full balance to avoid interest, which negates reward value. Focus on bonus categories and sign-up bonuses.",
                3: "If credit card interest is above 15%, prioritize debt payoff. Build a small emergency fund ($1,000) first, then tackle debt aggressively."
            }
            response = fallback_responses.get(i-1, "Consult with a financial advisor for personalized advice.")
        
        print(f"   A: {response}")

def demo_spending_scenario_simulator():
    """Advanced spending change simulation"""
    print(f"\n" + "=" * 70)
    print("📊 ADVANCED SCENARIO SIMULATOR")
    print("=" * 70)
    
    assistant = PersonalFinanceAssistant()
    
    # Current financial state
    current_state = {
        'current_balance': 4681.15,
        'minimum_payment': 140.44,
        'interest_rate': 0.1899,
        'monthly_income': 6500.00,
        'monthly_expenses': 4800.00
    }
    
    # Various scenarios
    scenarios = [
        {
            "name": "🏠 Save for house down payment",
            "monthly_change": -800,
            "duration_months": 24,
            "goal": "Save $19,200 for 20% down payment"
        },
        {
            "name": "✈️ Plan Europe vacation",
            "monthly_change": -300,
            "duration_months": 18,
            "goal": "Save $5,400 for trip"
        },
        {
            "name": "🚗 Buy a new car",
            "monthly_change": 450,
            "duration_months": 60,
            "goal": "Finance $350/month + insurance $100"
        },
        {
            "name": "💼 Career break preparation",
            "monthly_change": -1000,
            "duration_months": 12,
            "goal": "Build 6-month emergency fund"
        }
    ]
    
    print("🎯 Scenario Analysis Results:")
    
    for scenario in scenarios:
        analysis = assistant.simulate_spending_changes(current_state, [scenario])
        result = analysis[scenario['name']]
        
        print(f"\n{scenario['name']}:")
        print(f"   Goal: {scenario['goal']}")
        print(f"   {result['summary']}")
        
        if 'interest_saved' in result:
            print(f"   💰 Bonus: ${result['interest_saved']:,.0f} saved in interest!")

def main():
    """Run the complete integrated demo"""
    print("🏦 PERSONAL FINANCE ASSISTANT - COMPLETE DEMO")
    print("=" * 70)
    print("This demo shows real-world integration with:")
    print("• Statement parsing from text/OCR")
    print("• Transaction CSV import")
    print("• AI-powered analysis with RAG")
    print("• Personalized recommendations")
    print("• Scenario planning and simulation")
    
    try:
        # Run all demo components
        demo_integrated_analysis()
        demo_rag_financial_advice()  
        demo_spending_scenario_simulator()
        
        print(f"\n" + "=" * 70)
        print("✅ COMPLETE INTEGRATION DEMO FINISHED")
        print("=" * 70)
        print("🎉 The Personal Finance Assistant successfully:")
        print("   • Parsed real statement formats")
        print("   • Analyzed spending patterns")
        print("   • Generated personalized advice") 
        print("   • Simulated financial scenarios")
        print("   • Provided actionable recommendations")
        print("\n💡 Ready for production with AWS Bedrock integration!")
        
    except Exception as e:
        print(f"Demo error: {e}")
        print("Note: Full functionality requires AWS Bedrock access")

if __name__ == "__main__":
    main()
