#!/usr/bin/env python3
"""
Setup script for the Dispute Resolution Agent
"""
import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing requirements: {e}")
        return False
    return True

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    print("\nChecking AWS credentials...")
    
    # Check environment variables
    if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
        print("✓ AWS credentials found in environment variables")
        return True
    
    # Check AWS CLI configuration
    try:
        result = subprocess.run(['aws', 'configure', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and 'access_key' in result.stdout:
            print("✓ AWS credentials found in AWS CLI configuration")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("⚠ AWS credentials not found. Please configure using one of these methods:")
    print("  1. Set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
    print("  2. Run: aws configure")
    print("  3. Use IAM roles (if running on EC2)")
    return False

def check_bedrock_access():
    """Check if Bedrock models are accessible"""
    print("\nChecking AWS Bedrock access...")
    try:
        import boto3
        client = boto3.client('bedrock', region_name='us-east-1')
        
        # Try to list foundation models (this requires bedrock:ListFoundationModels permission)
        models = client.list_foundation_models()
        print(f"✓ Bedrock access confirmed. Found {len(models.get('modelSummaries', []))} models")
        
        # Check if our specific models are available
        model_ids = [model['modelId'] for model in models.get('modelSummaries', [])]
        claude_available = any('claude-3' in model_id for model_id in model_ids)
        titan_available = any('titan-embed' in model_id for model_id in model_ids)
        
        if claude_available:
            print("✓ Claude models available")
        else:
            print("⚠ Claude models not found - you may need to enable them in Bedrock console")
            
        if titan_available:
            print("✓ Titan embedding models available")
        else:
            print("⚠ Titan embedding models not found - you may need to enable them in Bedrock console")
            
        return True
        
    except Exception as e:
        print(f"✗ Bedrock access check failed: {e}")
        print("  Make sure you have:")
        print("  1. Proper AWS credentials configured")
        print("  2. Bedrock service access in your AWS region")
        print("  3. Model access enabled in Bedrock console")
        return False

def main():
    """Main setup function"""
    print("=== Dispute Resolution Agent Setup ===\n")
    
    # Install requirements
    if not install_requirements():
        print("Setup failed at requirements installation")
        return False
    
    # Check AWS credentials
    aws_creds_ok = check_aws_credentials()
    
    # Check Bedrock access
    bedrock_ok = check_bedrock_access()
    
    print(f"\n=== Setup Summary ===")
    print(f"Requirements: ✓ Installed")
    print(f"AWS Credentials: {'✓ Found' if aws_creds_ok else '⚠ Not found'}")
    print(f"Bedrock Access: {'✓ Available' if bedrock_ok else '⚠ Not available'}")
    
    if aws_creds_ok and bedrock_ok:
        print(f"\n🎉 Setup complete! You can now run: python main.py")
    else:
        print(f"\n⚠ Setup completed with warnings. The agent will run with limited functionality.")
        print(f"To fix issues, see the messages above.")
    
    return True

if __name__ == "__main__":
    main()
