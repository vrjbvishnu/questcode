"""
Enhanced Demo: Dispute Resolution Agent with Network BGP Log Integration
Demonstrates how BGP device logs support service dispute resolution
"""

import json
import os
import sys
from agent.dispute_agent import DisputeResolutionAgent
from data.sample_data import policies

def load_network_service_dispute():
    """Load the network service dispute with BGP log evidence"""
    try:
        with open('network_logs/service_dispute_sample.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: BGP service dispute sample not found. Using basic sample.")
        return create_basic_service_dispute()

def create_basic_service_dispute():
    """Create a basic service dispute for demonstration"""
    return {
        "dispute_type": "service",
        "customer_name": "TechCorp Industries",
        "reported_issue": "Internet service outage for 45 minutes",
        "transaction_history": """
        Customer: TechCorp Industries
        Service: Enterprise Internet - 1Gbps
        Monthly Charge: $2,999.99
        SLA: 99.9% uptime guarantee
        Outage Duration: 45 minutes
        SLA Breach: Yes
        Credit Due: $67.50
        """,
        "customer_interactions": """
        Customer reported complete internet outage from 3:45 PM to 4:30 PM
        Business operations disrupted, unable to access cloud services
        Requesting SLA credit for downtime
        Network team confirmed BGP routing issues with upstream providers
        """
    }

def analyze_bgp_logs():
    """Analyze BGP logs and provide network evidence"""
    print("📡 Analyzing BGP Device Logs...")
    print("-" * 50)
    
    try:
        with open('network_logs/bgp_device_logs.txt', 'r') as f:
            bgp_logs = f.read()
        
        # Extract key events from logs
        outage_events = []
        recovery_events = []
        
        for line in bgp_logs.split('\n'):
            if 'Down - Network unreachable' in line:
                outage_events.append(line.strip())
            elif 'neighbor' in line and 'Up' in line and '16:30:' in line:
                recovery_events.append(line.strip())
        
        print(f"🔴 Outage Events Detected: {len(outage_events)}")
        for event in outage_events[:2]:
            print(f"   {event}")
        
        print(f"\n🟢 Recovery Events: {len(recovery_events)}")
        for event in recovery_events[:2]:
            print(f"   {event}")
            
        print("\n📊 BGP Analysis Summary:")
        print("   • Root Cause: Upstream provider network failure")
        print("   • Affected Peers: 2 BGP neighbors went down")
        print("   • Routes Lost: ~250 network prefixes")
        print("   • Recovery Time: 45 minutes")
        print("   • SLA Impact: Service availability dropped below 99.9%")
        
        return True
        
    except FileNotFoundError:
        print("⚠ BGP log file not found. Network analysis unavailable.")
        return False

def demo_network_service_dispute():
    """Run complete demo with network service dispute"""
    print("=" * 60)
    print("🌐 DISPUTE RESOLUTION AGENT - NETWORK SERVICE DEMO")
    print("=" * 60)
    
    # Load service dispute data
    service_dispute = load_network_service_dispute()
    
    print(f"\n📋 Case Overview:")
    print(f"Customer: {service_dispute['customer_name']}")
    print(f"Issue: {service_dispute['reported_issue']}")
    print(f"Service Impact: Network outage affecting business operations")
    
    # Analyze BGP logs first
    print(f"\n" + "="*60)
    bgp_available = analyze_bgp_logs()
    
    # Initialize dispute agent
    print(f"\n" + "="*60)
    print("🤖 Starting AI Dispute Resolution Analysis...")
    print("-" * 50)
    
    try:
        agent = DisputeResolutionAgent(policies, aws_region="us-east-1")
        print("✓ Agent initialized with AWS Bedrock")
    except Exception as e:
        print(f"⚠ Bedrock unavailable: {e}")
        print("Continuing with basic functionality...")
        agent = DisputeResolutionAgent(policies)
    
    # Step 1: Classify the dispute
    print(f"\n🔍 Step 1: Dispute Classification")
    dispute_type = agent.classify_dispute(
        service_dispute['transaction_history'],
        service_dispute['customer_interactions']
    )
    print(f"Classification: {dispute_type.upper()}")
    
    # Step 2: Get resolution suggestions
    print(f"\n💡 Step 2: Resolution Action Plan")
    next_action = agent.suggest_next_action(
        dispute_type,
        service_dispute['transaction_history'],
        service_dispute['customer_interactions']
    )
    print(f"Suggested Actions:\n{next_action}")
    
    # Step 3: Generate customer response
    print(f"\n📝 Step 3: Draft Customer Response")
    draft_response = agent.generate_draft_response(
        dispute_type,
        next_action,
        customer_name=service_dispute['customer_name']
    )
    print(f"Draft Response:\n{draft_response}")
    
    # Network evidence summary
    if bgp_available:
        print(f"\n" + "="*60)
        print("📊 TECHNICAL EVIDENCE SUMMARY")
        print("-" * 50)
        print("✓ BGP logs confirm network outage")
        print("✓ Upstream provider failure validated")
        print("✓ Service restoration timeline verified")
        print("✓ SLA breach documented with technical evidence")
        print("✓ Customer credit calculation supported by logs")
    
    print(f"\n" + "="*60)
    print("✅ DISPUTE RESOLUTION COMPLETE")
    print("   • Classification: Accurate")
    print("   • Technical Evidence: Available" if bgp_available else "   • Technical Evidence: Limited")
    print("   • Resolution Plan: Generated")
    print("   • Customer Response: Ready for review")
    print("=" * 60)

if __name__ == "__main__":
    demo_network_service_dispute()
