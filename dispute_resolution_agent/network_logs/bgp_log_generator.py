"""
BGP Log Generator for Network Device Simulation
Used for testing service-related dispute scenarios involving network issues
"""

import datetime
import random
import json
from typing import List, Dict, Any

class BGPLogGenerator:
    """Generate realistic BGP logs for network device simulation"""
    
    def __init__(self, device_id: str = "RTR-01", asn: int = 65001):
        self.device_id = device_id
        self.asn = asn
        self.peers = [
            {"ip": "192.168.1.1", "asn": 65002, "state": "Established"},
            {"ip": "192.168.1.2", "asn": 65003, "state": "Established"},
            {"ip": "10.0.1.1", "asn": 65004, "state": "Established"},
            {"ip": "172.16.1.1", "asn": 65005, "state": "Connect"}
        ]
        self.route_prefixes = [
            "192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12",
            "203.0.113.0/24", "198.51.100.0/24", "203.0.114.0/24"
        ]
    
    def generate_bgp_event(self, event_type: str = None) -> Dict[str, Any]:
        """Generate a single BGP log event"""
        if not event_type:
            event_type = random.choice([
                "PEER_UP", "PEER_DOWN", "ROUTE_UPDATE", "ROUTE_WITHDRAW",
                "KEEPALIVE", "NOTIFICATION", "OPEN_SENT"
            ])
        
        timestamp = datetime.datetime.now()
        peer = random.choice(self.peers)
        
        base_event = {
            "timestamp": timestamp.isoformat(),
            "device_id": self.device_id,
            "local_asn": self.asn,
            "event_type": event_type,
            "peer_ip": peer["ip"],
            "peer_asn": peer["asn"],
            "severity": self._get_severity(event_type)
        }
        
        # Add event-specific details
        if event_type == "PEER_DOWN":
            base_event.update({
                "reason": random.choice([
                    "TCP connection lost", "Hold timer expired", 
                    "BGP Notification received", "Administrative shutdown"
                ]),
                "previous_state": "Established",
                "new_state": "Idle"
            })
        elif event_type == "PEER_UP":
            base_event.update({
                "previous_state": "Connect",
                "new_state": "Established",
                "hold_time": 180,
                "keepalive_time": 60
            })
        elif event_type in ["ROUTE_UPDATE", "ROUTE_WITHDRAW"]:
            base_event.update({
                "prefix": random.choice(self.route_prefixes),
                "next_hop": peer["ip"],
                "as_path": self._generate_as_path(peer["asn"]),
                "origin": random.choice(["IGP", "EGP", "INCOMPLETE"])
            })
        elif event_type == "NOTIFICATION":
            base_event.update({
                "error_code": random.choice([1, 2, 3, 4, 5, 6]),
                "error_subcode": random.randint(1, 10),
                "error_description": random.choice([
                    "Message Header Error", "OPEN Message Error",
                    "UPDATE Message Error", "Hold Timer Expired",
                    "Finite State Machine Error", "Cease"
                ])
            })
        
        return base_event
    
    def _get_severity(self, event_type: str) -> str:
        """Determine log severity based on event type"""
        severity_map = {
            "PEER_DOWN": "ERROR",
            "NOTIFICATION": "WARNING", 
            "PEER_UP": "INFO",
            "ROUTE_UPDATE": "DEBUG",
            "ROUTE_WITHDRAW": "INFO",
            "KEEPALIVE": "DEBUG",
            "OPEN_SENT": "DEBUG"
        }
        return severity_map.get(event_type, "INFO")
    
    def _generate_as_path(self, peer_asn: int) -> str:
        """Generate a realistic AS path"""
        path_length = random.randint(1, 4)
        as_path = [str(peer_asn)]
        
        for _ in range(path_length - 1):
            as_path.append(str(random.randint(64512, 65535)))
        
        return " ".join(as_path)
    
    def generate_log_batch(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate a batch of BGP log events"""
        events = []
        for _ in range(count):
            events.append(self.generate_bgp_event())
        return events
    
    def simulate_network_outage(self, duration_minutes: int = 30) -> List[Dict[str, Any]]:
        """Simulate a network outage scenario"""
        events = []
        start_time = datetime.datetime.now()
        
        # Outage begins - peers go down
        for peer in self.peers[:2]:  # Simulate 2 peers going down
            event = self.generate_bgp_event("PEER_DOWN")
            event["peer_ip"] = peer["ip"]
            event["peer_asn"] = peer["asn"]
            event["reason"] = "Network unreachable"
            events.append(event)
        
        # Routes withdrawn
        for _ in range(10):
            event = self.generate_bgp_event("ROUTE_WITHDRAW")
            events.append(event)
        
        # Recovery - peers come back up
        recovery_time = start_time + datetime.timedelta(minutes=duration_minutes)
        for peer in self.peers[:2]:
            event = self.generate_bgp_event("PEER_UP")
            event["peer_ip"] = peer["ip"]
            event["peer_asn"] = peer["asn"]
            event["timestamp"] = recovery_time.isoformat()
            events.append(event)
        
        # Routes re-advertised
        for _ in range(10):
            event = self.generate_bgp_event("ROUTE_UPDATE")
            event["timestamp"] = (recovery_time + datetime.timedelta(seconds=random.randint(1, 300))).isoformat()
            events.append(event)
        
        return events

def generate_sample_bgp_logs():
    """Generate sample BGP logs for the dispute resolution system"""
    generator = BGPLogGenerator("CORE-RTR-01", 65001)
    
    # Generate normal operation logs
    normal_logs = generator.generate_log_batch(30)
    
    # Generate network outage scenario
    outage_logs = generator.simulate_network_outage(45)
    
    return {
        "normal_operation": normal_logs,
        "network_outage": outage_logs,
        "device_info": {
            "device_id": generator.device_id,
            "asn": generator.asn,
            "peers": generator.peers,
            "log_generated": datetime.datetime.now().isoformat()
        }
    }

if __name__ == "__main__":
    # Generate and save sample logs
    logs = generate_sample_bgp_logs()
    
    print("BGP Log Generator - Sample Output")
    print("=" * 40)
    print(f"Device: {logs['device_info']['device_id']}")
    print(f"ASN: {logs['device_info']['asn']}")
    print(f"Normal logs: {len(logs['normal_operation'])} events")
    print(f"Outage logs: {len(logs['network_outage'])} events")
    print()
    
    # Show sample events
    print("Sample BGP Events:")
    print("-" * 20)
    for i, event in enumerate(logs['normal_operation'][:3]):
        print(f"{i+1}. {event['timestamp']} - {event['event_type']} - {event['peer_ip']} ({event['severity']})")
    
    print("\nOutage Events:")
    print("-" * 20)
    for i, event in enumerate(logs['network_outage'][:3]):
        print(f"{i+1}. {event['timestamp']} - {event['event_type']} - {event['peer_ip']} ({event['severity']})")
