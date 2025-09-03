import os
import json
import boto3
import numpy as np
from typing import List, Dict, Any, Optional

class DisputeResolutionAgent:
    """
    Dispute Resolution Agent using AWS Bedrock for:
    - Classification (fraud / billing / service)
    - RAG-style retrieval over policies
    - Generative draft responses and suggested actions
    """
    
    def __init__(self, policies: List[Dict[str, Any]], aws_region: str = "us-east-1"):
        """
        Initialize with policies and AWS Bedrock client
        
        Args:
            policies: List of policy dictionaries with 'id', 'title', and 'text' keys
            aws_region: AWS region for Bedrock service
        """
        self.policies = policies
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
        
        # Model IDs for different Bedrock models
        self.claude_model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        self.titan_embed_model_id = "amazon.titan-embed-text-v1"
        
        # Precompute embeddings for policies (for RAG)
        self.policy_embeddings = self._precompute_policy_embeddings()

    def _precompute_policy_embeddings(self) -> List[Dict[str, Any]]:
        """Precompute embeddings for all policies for RAG retrieval"""
        embeddings = []
        for policy in self.policies:
            try:
                embedding = self._get_embedding(policy.get('text', ''))
                embeddings.append({
                    'id': policy.get('id'),
                    'title': policy.get('title'),
                    'text': policy.get('text'),
                    'embedding': embedding
                })
            except Exception as e:
                print(f"Warning: Could not embed policy {policy.get('id')}: {e}")
                embeddings.append({
                    'id': policy.get('id'),
                    'title': policy.get('title'),
                    'text': policy.get('text'),
                    'embedding': None
                })
        return embeddings

    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding vector for text using Bedrock Titan embedding model"""
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
        """Calculate cosine similarity between two vectors"""
        if a is None or b is None:
            return 0.0
        
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)

    def _retrieve_relevant_policies(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve most relevant policies using semantic search"""
        query_embedding = self._get_embedding(query)
        if query_embedding is None:
            return self.policy_embeddings[:top_k]  # Fallback to first k policies
        
        similarities = []
        for policy_data in self.policy_embeddings:
            if policy_data['embedding'] is not None:
                similarity = self._cosine_similarity(query_embedding, policy_data['embedding'])
                similarities.append((similarity, policy_data))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [policy_data for _, policy_data in similarities[:top_k]]

    def _invoke_claude(self, prompt: str, max_tokens: int = 1000) -> str:
        """Invoke Claude model on Bedrock"""
        if not self.bedrock_runtime:
            return "Bedrock client not available"
        
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
            return f"Error: {str(e)}"

    def classify_dispute(self, transaction_history: str, customer_interactions: str) -> str:
        """
        Classify the dispute type using AWS Bedrock Claude model
        
        Args:
            transaction_history: String containing transaction details
            customer_interactions: String containing customer communication
            
        Returns:
            Dispute classification: 'fraud', 'billing', or 'service'
        """
        prompt = f"""
        You are a customer service AI assistant. Analyze the following dispute information and classify it into one of these categories: fraud, billing, or service.

        Transaction History:
        {transaction_history}

        Customer Interactions:
        {customer_interactions}

        Based on this information, classify the dispute type. Respond with only one word: fraud, billing, or service.

        Classification:"""
        
        response = self._invoke_claude(prompt, max_tokens=10)
        
        # Extract and normalize the classification
        classification = response.strip().lower()
        if 'fraud' in classification:
            return 'fraud'
        elif 'billing' in classification:
            return 'billing'
        elif 'service' in classification:
            return 'service'
        else:
            return 'billing'  # Default fallback

    def suggest_next_action(self, dispute_type: str, transaction_history: str = "", customer_interactions: str = "") -> str:
        """
        Suggest next best action using RAG with policies and Bedrock
        
        Args:
            dispute_type: The classified dispute type
            transaction_history: Transaction details for context
            customer_interactions: Customer communication for context
            
        Returns:
            Suggested next action steps
        """
        # Create query for policy retrieval
        query = f"Dispute type: {dispute_type}. Transaction: {transaction_history}. Customer: {customer_interactions}"
        
        # Retrieve relevant policies
        relevant_policies = self._retrieve_relevant_policies(query, top_k=3)
        policy_context = "\n\n".join([
            f"Policy: {policy['title']}\nContent: {policy['text']}" 
            for policy in relevant_policies
        ])
        
        prompt = f"""
        You are a customer service supervisor providing guidance to an agent handling a {dispute_type} dispute.

        Relevant Company Policies:
        {policy_context}

        Case Details:
        Transaction History: {transaction_history}
        Customer Interactions: {customer_interactions}

        Based on the policies and case details, provide clear, actionable next steps for the customer service agent. Be specific and practical.

        Next Action Steps:"""
        
        return self._invoke_claude(prompt, max_tokens=500)

    def generate_draft_response(self, dispute_type: str, next_action: str, customer_name: str = "Valued Customer") -> str:
        """
        Generate a draft customer response using Bedrock
        
        Args:
            dispute_type: The type of dispute
            next_action: The suggested next action
            customer_name: Customer's name for personalization
            
        Returns:
            Draft response for the customer
        """
        prompt = f"""
        You are a professional customer service representative. Write a courteous and helpful response to a customer about their {dispute_type} dispute.

        Next Action Plan:
        {next_action}

        Write a professional email response to {customer_name} that:
        1. Acknowledges their concern
        2. Explains what steps will be taken
        3. Sets appropriate expectations
        4. Maintains a helpful and empathetic tone

        Email Response:"""
        
        return self._invoke_claude(prompt, max_tokens=600)
