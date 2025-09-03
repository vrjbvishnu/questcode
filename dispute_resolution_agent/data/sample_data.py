transaction_history = """
Transaction ID: TXN-12345
Date: 2025-08-25
Amount: $199.99
Description: Premium Subscription - Annual Plan
Payment Method: Credit Card ending in 4567
Status: Completed
Previous transactions: Monthly plan $19.99 (cancelled on 2025-08-20)
"""

customer_interactions = """
Customer Call Log:
- Customer John Doe called on 2025-08-26 at 2:30 PM
- Issue: Claims he was charged $199.99 for annual plan but only wanted to cancel monthly plan
- Customer states: "I called to cancel my $19.99 monthly subscription but somehow got charged $199.99 for a full year"
- Customer provided verification: Last 4 digits of card, billing address
- Customer tone: Frustrated but polite
- Previous interaction: Email on 2025-08-20 requesting cancellation help
"""

policies = [
    {
        "id": "billing_001",
        "title": "Billing Dispute Resolution",
        "text": "For billing disputes, first verify the customer's identity and transaction details. Check if the charge was authorized through our system. If customer claims unauthorized upgrade, review account activity logs. Refunds for accidental upgrades can be processed within 48 hours if no services were used."
    },
    {
        "id": "fraud_001", 
        "title": "Fraud Investigation Protocol",
        "text": "For suspected fraud, immediately flag the account and contact our fraud prevention team. Do not process refunds until investigation is complete. Gather all transaction details, IP addresses, and customer verification information. Escalate to security team within 2 hours."
    },
    {
        "id": "service_001",
        "title": "Service Issue Resolution", 
        "text": "For service-related complaints, check system status and customer's service history. If service was unavailable, offer appropriate compensation or service credits. Document the issue in our system and provide estimated resolution timeline to customer."
    },
    {
        "id": "refund_001",
        "title": "Refund Policy",
        "text": "Refunds are available within 30 days of purchase for unused services. For subscription upgrades made in error, refunds can be processed immediately if downgrade is requested within 72 hours. All refunds require supervisor approval for amounts over $100."
    },
    {
        "id": "network_sla_001",
        "title": "Network SLA and Service Credits",
        "text": "Enterprise customers are entitled to service credits when network uptime falls below 99.9% monthly SLA. Credits are calculated as: (downtime minutes / total monthly minutes) * monthly service fee. BGP logs and network monitoring data serve as authoritative evidence for outage duration. Credits are automatically applied to next bill unless customer requests refund."
    },
    {
        "id": "network_outage_001", 
        "title": "Network Outage Response Protocol",
        "text": "For network service outages: 1) Verify outage through BGP logs and monitoring systems 2) Identify root cause (BGP peer failures, routing issues, upstream problems) 3) Provide customer with incident timeline and technical details 4) Calculate SLA credits based on actual downtime 5) Escalate to network engineering if customer disputes technical findings."
    },
    {
        "id": "bgp_evidence_001",
        "title": "BGP Log Evidence Standards", 
        "text": "BGP device logs are considered authoritative evidence for network outages. Key indicators include: PEER_DOWN events (network failures), ROUTE_WITHDRAW events (connectivity loss), and timestamp correlation with customer reports. BGP logs must be preserved for 90 days for dispute resolution. Network engineers can provide technical analysis upon request."
    }
]
