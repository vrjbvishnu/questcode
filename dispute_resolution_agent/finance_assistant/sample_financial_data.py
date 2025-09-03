"""
Sample financial data for testing the Personal Finance Assistant
Includes realistic monthly statements and user scenarios
"""

# Sample monthly statement data
sample_statement_august = {
    "statement_month": "August 2025",
    "previous_balance": 2150.00,
    "new_charges": 1850.75,
    "payments": 500.00,
    "current_balance": 3500.75,
    "minimum_payment": 105.00,
    "due_date": "2025-09-15",
    "interest_charged": 42.35,
    "interest_rate": 0.1899,  # 18.99% APR
    "available_credit": 6499.25,
    "credit_limit": 10000.00,
    "rewards_earned": 18507,  # Points earned this month
    "total_rewards": 85430,   # Total points available
    "spending_categories": {
        "Dining & Restaurants": 485.20,
        "Gas & Auto": 240.15,
        "Groceries": 320.40,
        "Shopping & Retail": 650.00,
        "Travel": 155.00
    }
}

sample_statement_september = {
    "statement_month": "September 2025",
    "previous_balance": 3500.75,
    "new_charges": 2180.40,
    "payments": 1000.00,
    "current_balance": 4681.15,
    "minimum_payment": 140.44,
    "due_date": "2025-10-15",
    "interest_charged": 68.92,
    "interest_rate": 0.1899,
    "available_credit": 5318.85,
    "credit_limit": 10000.00,
    "rewards_earned": 21804,
    "total_rewards": 107234,
    "spending_categories": {
        "Dining & Restaurants": 520.80,
        "Gas & Auto": 195.60,
        "Groceries": 380.75,
        "Shopping & Retail": 450.25,
        "Travel": 633.00
    }
}

# Sample user goals and preferences
sample_user_goals = {
    "primary_goal": "pay_off_debt",
    "target_payoff_months": 18,
    "monthly_budget": 4500.00,
    "savings_goal": 200.00,  # per month
    "travel_goal": "Europe trip next summer",
    "spending_alerts": ["dining", "shopping"],
    "preferred_communication": "encouraging"
}

# Different user personas for testing
user_persona_debt_focused = {
    "name": "Sarah",
    "primary_goal": "eliminate_debt",
    "monthly_income": 6500.00,
    "target_payoff_months": 12,
    "risk_tolerance": "conservative",
    "priorities": ["debt_payoff", "emergency_fund", "credit_score"]
}

user_persona_rewards_optimizer = {
    "name": "Mike",
    "primary_goal": "maximize_rewards",
    "monthly_income": 8500.00,
    "travel_frequency": "monthly",
    "risk_tolerance": "moderate",
    "priorities": ["travel_rewards", "cashback", "credit_optimization"]
}

user_persona_budget_conscious = {
    "name": "Jessica",
    "primary_goal": "budget_optimization",
    "monthly_income": 4200.00,
    "family_size": 3,
    "risk_tolerance": "conservative",
    "priorities": ["expense_tracking", "savings", "family_budget"]
}

# Sample financial scenarios for testing
common_scenarios = [
    {
        "name": "Emergency fund building",
        "monthly_change": -300,  # Save $300 more
        "duration_months": 12,
        "description": "Build emergency fund by saving $300/month"
    },
    {
        "name": "Vacation fund",
        "monthly_change": -200,
        "duration_months": 18,
        "description": "Save for Europe trip"
    },
    {
        "name": "Increased dining out",
        "monthly_change": 250,
        "duration_months": 6,
        "description": "What if I eat out more often?"
    },
    {
        "name": "Debt avalanche plan",
        "monthly_change": -500,
        "duration_months": 24,
        "description": "Aggressive debt payoff strategy"
    }
]

# Sample transaction details for context
sample_transactions = [
    {"date": "2025-09-01", "merchant": "Whole Foods", "amount": 78.45, "category": "Groceries"},
    {"date": "2025-09-02", "merchant": "Shell Gas Station", "amount": 52.30, "category": "Gas & Auto"},
    {"date": "2025-09-03", "merchant": "Amazon", "amount": 156.78, "category": "Shopping & Retail"},
    {"date": "2025-09-05", "merchant": "Starbucks", "amount": 12.85, "category": "Dining & Restaurants"},
    {"date": "2025-09-07", "merchant": "Delta Airlines", "amount": 485.00, "category": "Travel"},
    {"date": "2025-09-10", "merchant": "Target", "amount": 134.22, "category": "Shopping & Retail"},
    {"date": "2025-09-12", "merchant": "Olive Garden", "amount": 67.90, "category": "Dining & Restaurants"},
    {"date": "2025-09-15", "merchant": "Chevron", "amount": 48.75, "category": "Gas & Auto"},
    {"date": "2025-09-18", "merchant": "Apple Store", "amount": 299.99, "category": "Shopping & Retail"},
    {"date": "2025-09-22", "merchant": "Marriott Hotel", "amount": 148.00, "category": "Travel"}
]

# Sample financial tips and insights
financial_insights = {
    "credit_utilization": {
        "optimal_range": "Under 30%",
        "excellent_range": "Under 10%",
        "tip": "Keeping utilization low improves credit scores"
    },
    "interest_savings": {
        "rule": "Pay more than minimum",
        "impact": "Every extra $100 saves ~$20 in annual interest",
        "strategy": "Target highest interest debts first"
    },
    "rewards_optimization": {
        "travel_threshold": 25000,  # points for travel reward
        "cash_back_threshold": 2500,  # points for $25 cash back
        "quarterly_bonus": "Check for rotating 5% categories"
    }
}
