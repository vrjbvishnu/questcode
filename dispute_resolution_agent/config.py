"""
Configuration settings for the Dispute Resolution Agent
"""
import os

# AWS Bedrock Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# Bedrock Model IDs (update these based on your available models)
CLAUDE_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
TITAN_EMBED_MODEL_ID = "amazon.titan-embed-text-v1"

# Alternative model IDs you might want to use:
# CLAUDE_HAIKU_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0" 
# CLAUDE_OPUS_MODEL_ID = "anthropic.claude-3-opus-20240229-v1:0"
# TITAN_EMBED_G1_MODEL_ID = "amazon.titan-embed-text-v2:0"

# RAG Configuration
MAX_POLICY_RETRIEVALS = 3
EMBEDDING_DIMENSION = 1536  # Titan embedding dimension

# Response Generation Settings
MAX_TOKENS_CLASSIFICATION = 10
MAX_TOKENS_ACTION = 500
MAX_TOKENS_RESPONSE = 600

# Error Handling
FALLBACK_RESPONSES = {
    'classification_error': 'billing',
    'action_error': 'Please review the case details and consult with a supervisor.',
    'response_error': 'We apologize for the inconvenience. A supervisor will contact you shortly to resolve this matter.'
}
