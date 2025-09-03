# Dispute Resolution Agent (Customer Service AI)

An intelligent customer service agent that uses AWS Bedrock to classify disputes, suggest resolution actions, and generate draft responses using Retrieval Augmented Generation (RAG).

## Features

- **🤖 Intelligent Classification**: Automatically categorizes disputes as fraud, billing, or service issues using Claude 3
- **📚 RAG-Powered Suggestions**: Retrieves relevant policies using semantic search with Titan embeddings
- **✍️ Draft Response Generation**: Creates professional customer responses using generative AI
- **🔍 Context-Aware**: Analyzes transaction history and customer interactions for accurate recommendations

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Customer      │    │  Dispute         │    │   AWS Bedrock   │
│   Interaction   │───▶│  Resolution      │◄──▶│                 │
│                 │    │  Agent           │    │ • Claude 3      │
└─────────────────┘    │                  │    │ • Titan Embed   │
                       │ • Classification │    └─────────────────┘
                       │ • RAG Retrieval  │    
                       │ • Response Gen   │    ┌─────────────────┐
                       └──────────────────┘    │   Policy        │
                                              │   Knowledge     │
                                              │   Base          │
                                              └─────────────────┘
```

## Quick Start

### 1. Installation

```bash
# Clone or download the project
cd dispute_resolution_agent

# Run setup script
python setup.py
```

### 2. AWS Configuration

Set up your AWS credentials using one of these methods:

**Option A: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

**Option B: AWS CLI**
```bash
aws configure
```

**Option C: IAM Roles** (if running on EC2)

### 3. Enable Bedrock Models

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to "Model access" in the left sidebar
3. Enable access to:
   - **Claude 3 Sonnet** (for text generation)
   - **Titan Text Embeddings** (for RAG)

### 4. Run the Demo

```bash
python main.py
```

## Usage

### Basic Example

```python
from agent.dispute_agent import DisputeResolutionAgent

# Initialize with your policies
policies = [
    {
        "id": "refund_policy",
        "title": "Refund Guidelines", 
        "text": "Customers can receive refunds within 30 days..."
    }
]

agent = DisputeResolutionAgent(policies)

# Classify a dispute
dispute_type = agent.classify_dispute(
    transaction_history="Charge of $99.99 on 2025-08-25...",
    customer_interactions="Customer reports unauthorized charge..."
)

# Get suggested actions (uses RAG)
next_action = agent.suggest_next_action(
    dispute_type=dispute_type,
    transaction_history="...",
    customer_interactions="..."
)

# Generate draft response
draft = agent.generate_draft_response(
    dispute_type=dispute_type,
    next_action=next_action,
    customer_name="John Doe"
)
```

### Advanced Configuration

```python
# Custom AWS region and models
agent = DisputeResolutionAgent(
    policies=policies,
    aws_region="us-west-2"
)

# Override model IDs in config.py for different models
```

## Project Structure

```
dispute_resolution_agent/
├── agent/
│   └── dispute_agent.py      # Main agent logic with Bedrock integration
├── data/
│   └── sample_data.py        # Sample transaction data and policies
├── config.py                 # Configuration settings
├── main.py                   # Demo script
├── setup.py                  # Setup and installation script
├── test_agent.py            # Unit and integration tests
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Configuration

Key settings in `config.py`:

- **Model IDs**: Configure which Bedrock models to use
- **RAG Settings**: Number of policies to retrieve, embedding dimensions
- **Token Limits**: Max tokens for different response types
- **Fallback Responses**: Default responses when AI is unavailable

## Testing

```bash
# Run unit tests
python test_agent.py

# Run integration tests (requires AWS credentials)
python test_agent.py --integration
```

## Production Considerations

### Security
- Store AWS credentials securely (use IAM roles when possible)
- Enable CloudTrail logging for Bedrock API calls
- Implement rate limiting and cost monitoring

### Monitoring
- Log all classifications and responses for audit trail
- Monitor Bedrock usage and costs
- Set up alerts for high error rates

### Scaling
- Consider caching embeddings for large policy sets
- Implement batch processing for high volumes
- Use Amazon OpenSearch for larger knowledge bases

### Error Handling
- The agent includes fallback responses when Bedrock is unavailable
- Graceful degradation ensures basic functionality without AI

## Cost Optimization

- **Claude 3 Haiku**: Use for simpler classifications (lower cost)
- **Embedding Caching**: Pre-compute and store policy embeddings
- **Batch Processing**: Process multiple disputes together
- **Token Optimization**: Tune prompt lengths and max_tokens

## Troubleshooting

### Common Issues

**"Could not initialize Bedrock client"**
- Check AWS credentials configuration
- Verify region supports Bedrock
- Ensure proper IAM permissions

**"Model access denied"**
- Enable model access in Bedrock console
- Check IAM policies include Bedrock permissions
- Verify model IDs are correct for your region

**"Import errors"**
- Run `python setup.py` to install dependencies
- Check Python version (3.8+ recommended)

### IAM Permissions

Required permissions for the agent:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run tests: `python test_agent.py`
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review AWS Bedrock documentation
3. Open an issue with detailed error messages and configuration
