"""
Network Service Dispute Data Integration
Connects BGP logs with dispute resolution for service-related issues
"""

import sys
import os
import json
import datetime
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network_logs.bgp_log_generator import BGPLogGenerator

class NetworkServiceDispute:
    """Integration class for network service disputes"""
    
    def __init__(self):
        self.bgp_generator = BGPLogGenerator("CORE-RTR-01", 65001)
    
    def analyze_service_outage(self, start_time: str, end_time: str) -> Dict[str, Any]:
        """
        Analyze BGP logs for service outage periods
        Used when customers report service disruptions
        """
        outage_logs = self.bgp_generator.simulate_network_outage(45)
        
        # Parse time strings (handle both with and without timezone)
        try:
            start_dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        except:
            start_dt = datetime.datetime.fromisoformat(start_time.replace('Z', ''))
            
        try:
            end_dt = datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        except:
            end_dt = datetime.datetime.fromisoformat(end_time.replace('Z', ''))
        
        relevant_logs = []
        for log in outage_logs:
            try:
                log_time = datetime.datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
            except:
                log_time = datetime.datetime.fromisoformat(log['timestamp'].replace('Z', ''))
                
            # Make all datetime objects timezone-naive for comparison
            if start_dt.tzinfo:
                start_dt = start_dt.replace(tzinfo=None)
            if end_dt.tzinfo:
                end_dt = end_dt.replace(tzinfo=None)
            if log_time.tzinfo:
                log_time = log_time.replace(tzinfo=None)
                
            if start_dt <= log_time <= end_dt:
                relevant_logs.append(log)
        
        # Analyze the outage
        peer_down_events = [log for log in relevant_logs if log['event_type'] == 'PEER_DOWN']
        route_withdrawals = [log for log in relevant_logs if log['event_type'] == 'ROUTE_WITHDRAW']
        
        analysis = {
            "outage_detected": len(peer_down_events) > 0,
            "affected_peers": len(set(log['peer_ip'] for log in peer_down_events)),
            "routes_lost": len(route_withdrawals),
            "outage_start": start_time,
            "outage_end": end_time,
            "root_cause": self._determine_root_cause(relevant_logs),
            "customer_impact": self._assess_customer_impact(relevant_logs),
            "raw_logs": relevant_logs[:10]  # Include first 10 logs for evidence
        }
        
        return analysis
    
    def _determine_root_cause(self, logs: List[Dict[str, Any]]) -> str:
        """Analyze logs to determine likely root cause"""
        reasons = [log.get('reason', '') for log in logs if log.get('reason')]
        
        if any('Network unreachable' in reason for reason in reasons):
            return "Upstream provider network failure"
        elif any('TCP connection lost' in reason for reason in reasons):
            return "Network connectivity issues"
        elif any('Hold timer expired' in reason for reason in reasons):
            return "BGP session timeout - possible high latency"
        else:
            return "Undetermined - requires further investigation"
    
    def _assess_customer_impact(self, logs: List[Dict[str, Any]]) -> str:
        """Assess the level of customer impact from the outage"""
        error_events = [log for log in logs if log['severity'] in ['ERROR', 'CRITICAL']]
        warning_events = [log for log in logs if log['severity'] == 'WARNING']
        
        if len(error_events) > 5:
            return "HIGH - Multiple critical failures, likely widespread service disruption"
        elif len(error_events) > 2:
            return "MEDIUM - Some service degradation, partial connectivity loss"
        elif len(warning_events) > 3:
            return "LOW - Minor service issues, most customers unaffected"
        else:
            return "MINIMAL - Brief disruption, service quickly restored"

def create_service_dispute_sample():
    """Create sample data for a service-related dispute"""
    dispute_handler = NetworkServiceDispute()
    
    # Simulate a customer reporting service issues
    customer_report_time = "2025-09-02T15:45:00Z"
    service_restored_time = "2025-09-02T16:30:00Z"
    
    # Analyze the network during that period
    network_analysis = dispute_handler.analyze_service_outage(
        customer_report_time, 
        service_restored_time
    )
    
    # Create dispute context
    service_dispute = {
        "dispute_type": "service",
        "customer_id": "CUST-789123",
        "customer_name": "TechCorp Industries",
        "service_plan": "Enterprise Internet - 1Gbps",
        "reported_issue": "Complete internet connectivity loss from 3:45 PM to 4:30 PM",
        "customer_impact": "Business operations disrupted, unable to access cloud services",
        "network_analysis": network_analysis,
        "transaction_history": f"""
        Customer: TechCorp Industries (Account: CUST-789123)
        Service: Enterprise Internet - 1Gbps Dedicated
        Monthly Charge: $2,999.99
        SLA: 99.9% uptime guarantee
        Reported Outage: {customer_report_time} - {service_restored_time}
        Duration: 45 minutes
        SLA Breach: Yes (exceeded 99.9% threshold)
        """,
        "customer_interactions": f"""
        15:50 - Customer called reporting complete internet outage
        15:52 - Verified customer identity and service details
        15:55 - Confirmed outage affecting their circuit
        16:00 - Escalated to network operations center
        16:30 - Service restored, customer notified
        16:35 - Customer confirmed connectivity restored
        Post-outage: Customer requesting SLA credit for downtime
        """
    }
    
    return service_dispute

if __name__ == "__main__":
    # Generate sample service dispute with network evidence
    sample_dispute = create_service_dispute_sample()
    
    print("Network Service Dispute Analysis")
    print("=" * 40)
    print(f"Customer: {sample_dispute['customer_name']}")
    print(f"Issue: {sample_dispute['reported_issue']}")
    print(f"Impact: {sample_dispute['customer_impact']}")
    print()
    
    analysis = sample_dispute['network_analysis']
    print("Network Analysis Results:")
    print(f"- Outage Detected: {analysis['outage_detected']}")
    print(f"- Affected Network Peers: {analysis['affected_peers']}")
    print(f"- Routes Lost: {analysis['routes_lost']}")
    print(f"- Root Cause: {analysis['root_cause']}")
    print(f"- Customer Impact Level: {analysis['customer_impact']}")
    print()
    
    print("Sample BGP Log Events:")
    for i, log in enumerate(analysis['raw_logs'][:3], 1):
        print(f"{i}. {log['timestamp']} - {log['event_type']} - {log.get('reason', 'N/A')}")
    
    # Save the dispute data for use in the main agent
    with open('network_logs/service_dispute_sample.json', 'w') as f:
        json.dump(sample_dispute, f, indent=2)
    
    print(f"\nSample dispute saved to: network_logs/service_dispute_sample.json")
