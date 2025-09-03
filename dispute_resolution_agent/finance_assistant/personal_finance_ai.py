"""
Personal Finance Assistant using AWS Bedrock
Reads monthly statements, explains in plain English, and provides personalized nudges
"""

import json
import datetime
from typing import Dict, List, Any, Optional
import boto3
import numpy as np

class PersonalFinanceAssistant:
    """
    AI-powered personal finance assistant that:
    - Analyzes monthly statements in plain English
    - Provides personalized financial nudges
    - Simulates spending scenarios
    - Uses RAG with financial documents
    """
    
    def __init__(self, aws_region: str = "us-east-1"):
        self.aws_region = aws_region
        
        # Initialize Bedrock client
        try:
            self.bedrock_runtime = boto3.client(
                service_name='bedrock-runtime',
                region_name=aws_region
            )
        except Exception as e:
            print(f"Warning: Could not initialize Bedrock client: {e}")
            self.bedrock_runtime = None
        
        # Model configurations
        self.claude_model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        self.titan_embed_model_id = "amazon.titan-embed-text-v1"
        
        # Financial knowledge base (in production, load from external source)
        self.financial_docs = [
            {
                "id": "interest_basics",
                "title": "Credit Card Interest Calculations",
                "content": "Credit card interest is calculated daily based on your average daily balance. If you carry a balance, you'll pay interest on new purchases immediately. To avoid interest, pay your full statement balance by the due date."
            },
            {
                "id": "rewards_optimization",
                "title": "Maximizing Credit Card Rewards",
                "content": "Most rewards cards have bonus categories that change quarterly. Travel cards often offer 2-3x points on travel and dining. Cash back cards typically offer 1-5% on rotating categories. Always pay in full to avoid interest charges that exceed reward value."
            },
            {
                "id": "budget_strategies",
                "title": "Effective Budgeting Strategies",
                "content": "The 50/30/20 rule suggests 50% for needs, 30% for wants, 20% for savings. Track spending for a month to understand patterns. Small changes like reducing dining out by $100/month can save $1,200 annually."
            },
            {
                "id": "emergency_fund",
                "title": "Emergency Fund Guidelines",
                "content": "Aim for 3-6 months of expenses in an emergency fund. Keep this in a high-yield savings account for easy access. Start with $1,000 if you're building from zero, then gradually increase to the full amount."
            }
        ]
        
        # Precompute embeddings for RAG
        self.doc_embeddings = self._precompute_embeddings()
    
    def _precompute_embeddings(self) -> List[Dict[str, Any]]:
        """Precompute embeddings for financial documents"""
        embeddings = []
        for doc in self.financial_docs:
            try:
                embedding = self._get_embedding(doc['content'])
                embeddings.append({
                    'id': doc['id'],
                    'title': doc['title'],
                    'content': doc['content'],
                    'embedding': embedding
                })
            except Exception as e:
                print(f"Warning: Could not embed document {doc['id']}: {e}")
                embeddings.append({
                    'id': doc['id'],
                    'title': doc['title'],
                    'content': doc['content'],
                    'embedding': None
                })
        return embeddings
    
    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding vector for text using Bedrock Titan"""
        if not self.bedrock_runtime:
            return None
            
        try:
            body = json.dumps({"inputText": text})
            response = self.bedrock_runtime.invoke_model(
                modelId=self.titan_embed_model_id,
                contentType="application/json",
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            embedding = np.array(response_body['embedding'])
            return embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return None
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between vectors"""
        if a is None or b is None:
            return 0.0
        
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)
    
    def _retrieve_relevant_docs(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """Retrieve relevant financial documents using semantic search"""
        query_embedding = self._get_embedding(query)
        if query_embedding is None:
            return self.doc_embeddings[:top_k]  # Fallback
        
        similarities = []
        for doc_data in self.doc_embeddings:
            if doc_data['embedding'] is not None:
                similarity = self._cosine_similarity(query_embedding, doc_data['embedding'])
                similarities.append((similarity, doc_data))
        
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [doc_data for _, doc_data in similarities[:top_k]]
    
    def _invoke_claude(self, prompt: str, max_tokens: int = 1000) -> str:
        """Invoke Claude model on Bedrock"""
        if not self.bedrock_runtime:
            return "Bedrock client not available - using fallback response"
        
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
            
            response = self.bedrock_runtime.invoke_model(
                modelId=self.claude_model_id,
                contentType="application/json",
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
        except Exception as e:
            print(f"Error invoking Claude: {e}")
            return f"Error generating response: {str(e)}"
    
    def explain_statement(self, statement_data: Dict[str, Any]) -> str:
        """
        Explain monthly statement in plain English
        
        Args:
            statement_data: Dictionary containing statement information
            
        Returns:
            Plain English explanation of the statement
        """
        # Retrieve relevant financial docs
        query = f"credit card statement balance interest charges spending categories"
        relevant_docs = self._retrieve_relevant_docs(query, top_k=2)
        context = "\n\n".join([f"{doc['title']}: {doc['content']}" for doc in relevant_docs])
        
        prompt = f"""
        You are a helpful personal finance assistant. Explain this monthly statement in simple, plain English. 
        Focus on what the customer needs to know and any important insights.

        Financial Education Context:
        {context}

        Statement Details:
        - Previous Balance: ${statement_data.get('previous_balance', 0):,.2f}
        - New Charges: ${statement_data.get('new_charges', 0):,.2f}
        - Payments: ${statement_data.get('payments', 0):,.2f}
        - Current Balance: ${statement_data.get('current_balance', 0):,.2f}
        - Minimum Payment: ${statement_data.get('minimum_payment', 0):,.2f}
        - Due Date: {statement_data.get('due_date', 'Not specified')}
        - Interest Charged: ${statement_data.get('interest_charged', 0):,.2f}
        - Available Credit: ${statement_data.get('available_credit', 0):,.2f}
        - Spending Categories: {statement_data.get('spending_categories', {})}

        Provide a clear, conversational explanation of what happened this month and what it means for the customer.

        Statement Explanation:"""
        
        if not self.bedrock_runtime:
            # Fallback explanation without AI
            return self._fallback_statement_explanation(statement_data)
        
        return self._invoke_claude(prompt, max_tokens=600)
    
    def _fallback_statement_explanation(self, statement_data: Dict[str, Any]) -> str:
        """Fallback explanation when Bedrock is unavailable"""
        current_balance = statement_data.get('current_balance', 0)
        new_charges = statement_data.get('new_charges', 0)
        payments = statement_data.get('payments', 0)
        interest = statement_data.get('interest_charged', 0)
        
        explanation = f"""
This month's statement breakdown:

💰 You spent ${new_charges:,.2f} in new charges
💳 You made ${payments:,.2f} in payments
📊 Your current balance is ${current_balance:,.2f}

"""
        if interest > 0:
            explanation += f"⚠️ You were charged ${interest:,.2f} in interest this month.\n"
        
        if current_balance > statement_data.get('minimum_payment', 0):
            explanation += "💡 Pay more than the minimum to save on interest charges.\n"
            
        return explanation
    
    def generate_nudges(self, statement_data: Dict[str, Any], user_goals: Dict[str, Any] = None) -> List[str]:
        """
        Generate personalized financial nudges based on statement analysis
        
        Args:
            statement_data: Monthly statement information
            user_goals: User's financial goals and preferences
            
        Returns:
            List of personalized nudge messages
        """
        nudges = []
        
        current_balance = statement_data.get('current_balance', 0)
        minimum_payment = statement_data.get('minimum_payment', 0)
        available_credit = statement_data.get('available_credit', 0)
        new_charges = statement_data.get('new_charges', 0)
        interest_rate = statement_data.get('interest_rate', 0.1899)  # Default APR
        
        # Interest avoidance nudge
        if current_balance > 0:
            daily_rate = interest_rate / 365
            monthly_interest = current_balance * daily_rate * 30
            nudges.append(f"💰 Pay ${current_balance:,.2f} more to avoid ~${monthly_interest:,.2f} in interest next month")
        
        # Minimum payment warning
        if current_balance > minimum_payment * 2:
            extra_payment = current_balance - minimum_payment
            months_to_payoff = self._calculate_payoff_time(current_balance, minimum_payment, interest_rate)
            nudges.append(f"⏰ Paying only the minimum? It'll take {months_to_payoff:.0f} months to pay off. Consider paying ${extra_payment/2:,.2f} more.")
        
        # Credit utilization nudge
        total_credit_limit = current_balance + available_credit
        utilization = (current_balance / total_credit_limit) * 100 if total_credit_limit > 0 else 0
        
        if utilization > 30:
            target_balance = total_credit_limit * 0.30
            reduction_needed = current_balance - target_balance
            nudges.append(f"📉 Your credit utilization is {utilization:.0f}%. Pay down ${reduction_needed:,.2f} to get under 30% for better credit scores.")
        
        # Spending category insights
        spending_categories = statement_data.get('spending_categories', {})
        if spending_categories:
            highest_category = max(spending_categories.items(), key=lambda x: x[1])
            if highest_category[1] > new_charges * 0.3:  # If one category is >30% of spending
                nudges.append(f"🛍️ {highest_category[0]} was your biggest expense at ${highest_category[1]:,.2f}. Consider setting a budget for this category.")
        
        # Rewards opportunities
        rewards_earned = statement_data.get('rewards_earned', 0)
        if rewards_earned > 0:
            if rewards_earned >= 25000:  # Assuming points system
                nudges.append(f"✈️ You've earned {rewards_earned:,} points! That's enough for a travel reward - check your redemption options.")
            else:
                points_to_reward = 25000 - rewards_earned
                nudges.append(f"🎯 You're {points_to_reward:,} points away from a travel reward. Keep using your card for everyday purchases!")
        
        return nudges
    
    def _calculate_payoff_time(self, balance: float, monthly_payment: float, annual_rate: float) -> float:
        """Calculate months to pay off balance"""
        if monthly_payment <= balance * (annual_rate / 12):
            return float('inf')  # Payment doesn't cover interest
        
        monthly_rate = annual_rate / 12
        months = -np.log(1 - (balance * monthly_rate) / monthly_payment) / np.log(1 + monthly_rate)
        return months
    
    def simulate_spending_changes(self, current_statement: Dict[str, Any], scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Simulate different spending scenarios and their financial impact
        
        Args:
            current_statement: Current financial situation
            scenarios: List of scenario changes to simulate
            
        Returns:
            Analysis of each scenario's impact
        """
        results = {}
        
        for scenario in scenarios:
            scenario_name = scenario.get('name', 'Unnamed Scenario')
            monthly_change = scenario.get('monthly_change', 0)  # Positive = spend more, Negative = save more
            duration_months = scenario.get('duration_months', 12)
            
            # Calculate impact
            current_balance = current_statement.get('current_balance', 0)
            current_payment = current_statement.get('minimum_payment', 0)
            interest_rate = current_statement.get('interest_rate', 0.1899)
            
            # Scenario 1: Additional spending (increases balance)
            if monthly_change > 0:
                new_balance = current_balance + (monthly_change * duration_months)
                new_interest_cost = self._calculate_total_interest(new_balance, current_payment, interest_rate, duration_months)
            # Scenario 2: Additional savings (reduces spending/increases payments)
            else:
                additional_payment = abs(monthly_change)
                total_saved = additional_payment * duration_months
                new_balance = max(0, current_balance - total_saved)
                interest_saved = self._calculate_interest_saved(current_balance, additional_payment, interest_rate, duration_months)
                
                results[scenario_name] = {
                    'monthly_change': monthly_change,
                    'total_impact': total_saved,
                    'new_balance': new_balance,
                    'interest_saved': interest_saved,
                    'summary': f"Saving ${abs(monthly_change):,.2f}/month for {duration_months} months would save ${total_saved:,.2f} total and ${interest_saved:,.2f} in interest"
                }
                continue
            
            results[scenario_name] = {
                'monthly_change': monthly_change,
                'new_balance': new_balance,
                'additional_interest': new_interest_cost,
                'summary': f"Spending ${monthly_change:,.2f} more per month would add ${monthly_change * duration_months:,.2f} to debt and ~${new_interest_cost:,.2f} in extra interest"
            }
        
        return results
    
    def _calculate_total_interest(self, balance: float, payment: float, annual_rate: float, months: int) -> float:
        """Calculate total interest over a period"""
        monthly_rate = annual_rate / 12
        total_interest = 0
        current_balance = balance
        
        for _ in range(months):
            interest_charge = current_balance * monthly_rate
            total_interest += interest_charge
            current_balance = current_balance + interest_charge - payment
            if current_balance <= 0:
                break
                
        return total_interest
    
    def _calculate_interest_saved(self, balance: float, extra_payment: float, annual_rate: float, months: int) -> float:
        """Calculate interest saved by making extra payments"""
        # Interest with minimum payments
        minimum_payment = balance * 0.02  # Assume 2% minimum
        interest_normal = self._calculate_total_interest(balance, minimum_payment, annual_rate, months)
        
        # Interest with extra payments
        enhanced_payment = minimum_payment + extra_payment
        interest_with_extra = self._calculate_total_interest(balance, enhanced_payment, annual_rate, months)
        
        return max(0, interest_normal - interest_with_extra)
    
    def generate_financial_report(self, statement_data: Dict[str, Any], user_goals: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate comprehensive financial report with explanations, nudges, and scenarios
        
        Args:
            statement_data: Monthly statement data
            user_goals: User's financial goals
            
        Returns:
            Complete financial analysis report
        """
        # Get statement explanation
        explanation = self.explain_statement(statement_data)
        
        # Generate personalized nudges
        nudges = self.generate_nudges(statement_data, user_goals)
        
        # Run common scenarios
        scenarios = [
            {"name": "Save $200 more per month", "monthly_change": -200, "duration_months": 12},
            {"name": "Save $100 more per month", "monthly_change": -100, "duration_months": 12},
            {"name": "Spend $150 more per month", "monthly_change": 150, "duration_months": 12}
        ]
        
        scenario_analysis = self.simulate_spending_changes(statement_data, scenarios)
        
        return {
            "statement_explanation": explanation,
            "personalized_nudges": nudges,
            "scenario_analysis": scenario_analysis,
            "generated_at": datetime.datetime.now().isoformat(),
            "summary": {
                "current_balance": statement_data.get('current_balance', 0),
                "monthly_spending": statement_data.get('new_charges', 0),
                "interest_charged": statement_data.get('interest_charged', 0),
                "available_credit": statement_data.get('available_credit', 0)
            }
        }
