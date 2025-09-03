"""
Demo script for Personal Finance Assistant
Shows how to analyze statements, generate nudges, and simulate scenarios
"""

import sys
import os
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from finance_assistant.personal_finance_ai import PersonalFinanceAssistant
from finance_assistant.sample_financial_data import (
    sample_statement_september, sample_user_goals, common_scenarios, user_persona_debt_focused
)

def demo_statement_analysis():
    """Demonstrate statement analysis and explanation"""
    print("=" * 70)
    print("💰 PERSONAL FINANCE ASSISTANT DEMO")
    print("=" * 70)
    
    # Initialize the assistant
    assistant = PersonalFinanceAssistant(aws_region="us-east-1")
    
    print(f"\n📊 Analyzing September 2025 Statement...")
    print(f"Customer: {user_persona_debt_focused['name']}")
    print(f"Primary Goal: {user_persona_debt_focused['primary_goal'].replace('_', ' ').title()}")
    
    # Display key statement metrics
    statement = sample_statement_september
    print(f"\n📋 Statement Overview:")
    print(f"   Previous Balance: ${statement['previous_balance']:,.2f}")
    print(f"   New Charges: ${statement['new_charges']:,.2f}")
    print(f"   Payments Made: ${statement['payments']:,.2f}")
    print(f"   Current Balance: ${statement['current_balance']:,.2f}")
    print(f"   Interest Charged: ${statement['interest_charged']:,.2f}")
    print(f"   Available Credit: ${statement['available_credit']:,.2f}")
    
    # Generate complete financial report
    print(f"\n" + "="*70)
    print("🤖 AI ANALYSIS IN PROGRESS...")
    print("="*70)
    
    report = assistant.generate_financial_report(statement, sample_user_goals)
    
    # Display results
    print(f"\n📖 PLAIN ENGLISH EXPLANATION:")
    print("-" * 50)
    print(report['statement_explanation'])
    
    print(f"\n💡 PERSONALIZED NUDGES:")
    print("-" * 50)
    for i, nudge in enumerate(report['personalized_nudges'], 1):
        print(f"{i}. {nudge}")
    
    print(f"\n🔮 SCENARIO ANALYSIS:")
    print("-" * 50)
    for scenario_name, analysis in report['scenario_analysis'].items():
        print(f"\n📈 {scenario_name}:")
        print(f"   {analysis['summary']}")
        if 'interest_saved' in analysis:
            print(f"   💰 Interest Savings: ${analysis['interest_saved']:,.2f}")
        if 'new_balance' in analysis:
            print(f"   💳 New Balance: ${analysis['new_balance']:,.2f}")

def demo_spending_categories():
    """Demonstrate spending category analysis"""
    print(f"\n" + "="*70)
    print("📊 SPENDING BREAKDOWN ANALYSIS")
    print("="*70)
    
    statement = sample_statement_september
    categories = statement['spending_categories']
    total_spending = sum(categories.values())
    
    print(f"\nTotal Monthly Spending: ${total_spending:,.2f}")
    print(f"\nCategory Breakdown:")
    
    # Sort categories by amount
    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    
    for category, amount in sorted_categories:
        percentage = (amount / total_spending) * 100
        print(f"   {category:.<25} ${amount:>8,.2f} ({percentage:4.1f}%)")
    
    # Identify insights
    print(f"\n💡 Spending Insights:")
    highest_category, highest_amount = sorted_categories[0]
    if highest_amount > total_spending * 0.25:
        print(f"   • {highest_category} is your largest expense at {(highest_amount/total_spending)*100:.0f}% of spending")
    
    dining_amount = categories.get('Dining & Restaurants', 0)
    if dining_amount > 400:
        monthly_savings = dining_amount * 0.3  # 30% reduction
        annual_savings = monthly_savings * 12
        print(f"   • Reducing dining out by 30% could save ${monthly_savings:.0f}/month (${annual_savings:,.0f}/year)")

def demo_interest_calculations():
    """Demonstrate interest and payoff calculations"""
    print(f"\n" + "="*70)
    print("💰 DEBT PAYOFF & INTEREST ANALYSIS")
    print("="*70)
    
    assistant = PersonalFinanceAssistant()
    statement = sample_statement_september
    
    current_balance = statement['current_balance']
    minimum_payment = statement['minimum_payment']
    interest_rate = statement['interest_rate']
    
    print(f"\nCurrent Situation:")
    print(f"   Balance: ${current_balance:,.2f}")
    print(f"   Minimum Payment: ${minimum_payment:,.2f}")
    print(f"   Interest Rate: {interest_rate*100:.2f}% APR")
    
    # Calculate payoff scenarios
    scenarios = [
        {"payment": minimum_payment, "label": "Minimum Payment Only"},
        {"payment": minimum_payment + 100, "label": "Minimum + $100"},
        {"payment": minimum_payment + 300, "label": "Minimum + $300"},
        {"payment": minimum_payment + 500, "label": "Minimum + $500"}
    ]
    
    print(f"\n📊 Payoff Scenarios:")
    print(f"{'Strategy':<20} {'Months':<8} {'Total Interest':<15} {'Total Paid'}")
    print("-" * 60)
    
    for scenario in scenarios:
        payment = scenario['payment']
        months = assistant._calculate_payoff_time(current_balance, payment, interest_rate)
        total_interest = assistant._calculate_total_interest(current_balance, payment, interest_rate, int(months))
        total_paid = current_balance + total_interest
        
        if months < 100:  # Reasonable timeframe
            print(f"{scenario['label']:<20} {months:>6.0f}   ${total_interest:>10,.0f}     ${total_paid:>10,.0f}")
        else:
            print(f"{scenario['label']:<20} {'Never':>6}   ${'∞':>10}        ${'∞':>10}")

def demo_rewards_analysis():
    """Demonstrate rewards and benefits analysis"""
    print(f"\n" + "="*70)
    print("🎁 REWARDS & BENEFITS ANALYSIS") 
    print("="*70)
    
    statement = sample_statement_september
    total_points = statement['total_rewards']
    monthly_points = statement['rewards_earned']
    
    print(f"\n🏆 Rewards Status:")
    print(f"   Points Earned This Month: {monthly_points:,}")
    print(f"   Total Points Available: {total_points:,}")
    
    # Redemption options
    redemptions = [
        {"option": "Travel Reward (Domestic)", "points": 25000, "value": "$300"},
        {"option": "Travel Reward (International)", "points": 50000, "value": "$600"},
        {"option": "Cash Back", "points": 2500, "value": "$25"},
        {"option": "Gift Cards", "points": 2000, "value": "$25"},
    ]
    
    print(f"\n🎯 Available Redemptions:")
    for redemption in redemptions:
        points_needed = redemption['points']
        if total_points >= points_needed:
            available = total_points // points_needed
            print(f"   ✅ {redemption['option']}: {available}x available ({redemption['value']} each)")
        else:
            needed = points_needed - total_points
            months_needed = needed / monthly_points if monthly_points > 0 else float('inf')
            if months_needed < 12:
                print(f"   ⏳ {redemption['option']}: {needed:,} more points needed (~{months_needed:.0f} months)")
            else:
                print(f"   ❌ {redemption['option']}: {needed:,} more points needed")

def main():
    """Run the complete personal finance assistant demo"""
    try:
        demo_statement_analysis()
        demo_spending_categories()
        demo_interest_calculations()
        demo_rewards_analysis()
        
        print(f"\n" + "="*70)
        print("✅ DEMO COMPLETE")
        print("="*70)
        print("The Personal Finance Assistant can help users:")
        print("• Understand their monthly statements in plain English")
        print("• Get personalized nudges to improve their finances")
        print("• Simulate different spending and saving scenarios")
        print("• Optimize rewards and benefits")
        print("• Plan debt payoff strategies")
        print("• Track progress toward financial goals")
        
    except Exception as e:
        print(f"Demo error: {e}")
        print("Note: Some features require AWS Bedrock access")

if __name__ == "__main__":
    main()
