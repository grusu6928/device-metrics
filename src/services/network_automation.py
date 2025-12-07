"""Network automation and device management"""
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NetworkDeviceManager:
    """Manages network device metrics and automation"""
    
    # Network-specific metric types
    NETWORK_METRICS = [
        "interface_throughput",
        "interface_errors",
        "interface_drops",
        "packet_loss",
        "latency",
        "bandwidth_utilization",
        "routing_table_size",
        "bgp_peer_status",
        "ospf_neighbor_status",
        "cpu_utilization",
        "memory_utilization",
        "temperature"
    ]
    
    # Network device types
    DEVICE_TYPES = [
        "router",
        "switch",
        "firewall",
        "load_balancer",
        "wireless_controller"
    ]
    
    def __init__(self):
        """Initialize network device manager"""
        self.device_configs = {}
    
    def validate_network_metric(self, device_id: str, metric_type: str, 
                                value: float, metadata: Dict) -> bool:
        """Validate network-specific metrics"""
        if metric_type not in self.NETWORK_METRICS:
            logger.warning(f"Unknown network metric type: {metric_type}")
            return False
        
        # Network-specific validations
        if metric_type == "interface_throughput":
            if value < 0 or value > 100:
                logger.warning(f"Invalid throughput value: {value}")
                return False
        
        if metric_type == "packet_loss":
            if value < 0 or value > 100:
                logger.warning(f"Invalid packet loss value: {value}")
                return False
        
        if metric_type == "latency":
            if value < 0:
                logger.warning(f"Invalid latency value: {value}")
                return False
        
        return True
    
    def get_network_device_summary(self, device_id: str, metrics: List[Dict]) -> Dict:
        """Generate network device summary"""
        summary = {
            "device_id": device_id,
            "device_type": self._infer_device_type(metrics),
            "interfaces": self._extract_interfaces(metrics),
            "network_health": self._calculate_network_health(metrics),
            "critical_alerts": self._identify_critical_network_issues(metrics)
        }
        return summary
    
    def _infer_device_type(self, metrics: List[Dict]) -> Optional[str]:
        """Infer device type from metrics"""
        metric_types = {m.get("metric_type") for m in metrics}
        
        if "bgp_peer_status" in metric_types or "routing_table_size" in metric_types:
            return "router"
        elif "interface_throughput" in metric_types and "switch" in str(metrics[0].get("metadata", {})):
            return "switch"
        elif "packet_loss" in metric_types and "firewall" in str(metrics[0].get("metadata", {})):
            return "firewall"
        
        return "unknown"
    
    def _extract_interfaces(self, metrics: List[Dict]) -> List[str]:
        """Extract network interfaces from metrics"""
        interfaces = set()
        for metric in metrics:
            metadata = metric.get("metadata", {})
            if "interface" in metadata:
                interfaces.add(metadata["interface"])
            if "interface_name" in metadata:
                interfaces.add(metadata["interface_name"])
        return list(interfaces)
    
    def _calculate_network_health(self, metrics: List[Dict]) -> str:
        """Calculate overall network health"""
        critical_count = 0
        warning_count = 0
        
        for metric in metrics:
            metric_type = metric.get("metric_type")
            value = metric.get("value", 0)
            
            if metric_type == "packet_loss" and value > 5:
                critical_count += 1
            elif metric_type == "packet_loss" and value > 1:
                warning_count += 1
            
            if metric_type == "interface_errors" and value > 1000:
                critical_count += 1
            elif metric_type == "interface_errors" and value > 100:
                warning_count += 1
            
            if metric_type == "latency" and value > 500:
                critical_count += 1
            elif metric_type == "latency" and value > 200:
                warning_count += 1
        
        if critical_count > 0:
            return "critical"
        elif warning_count > 2:
            return "degraded"
        else:
            return "healthy"
    
    def _identify_critical_network_issues(self, metrics: List[Dict]) -> List[Dict]:
        """Identify critical network issues"""
        issues = []
        
        for metric in metrics:
            metric_type = metric.get("metric_type")
            value = metric.get("value", 0)
            
            if metric_type == "packet_loss" and value > 5:
                issues.append({
                    "type": "high_packet_loss",
                    "severity": "critical",
                    "value": value,
                    "interface": metric.get("metadata", {}).get("interface", "unknown")
                })
            
            if metric_type == "interface_errors" and value > 1000:
                issues.append({
                    "type": "interface_errors",
                    "severity": "critical",
                    "value": value,
                    "interface": metric.get("metadata", {}).get("interface", "unknown")
                })
            
            if metric_type == "bgp_peer_status" and value == 0:
                issues.append({
                    "type": "bgp_peer_down",
                    "severity": "critical",
                    "peer": metric.get("metadata", {}).get("peer_ip", "unknown")
                })
        
        return issues


class NetworkAutomationService:
    """Service for network automation tasks"""
    
    def __init__(self, device_manager: NetworkDeviceManager):
        """Initialize network automation service"""
        self.device_manager = device_manager
    
    def generate_network_remediation(self, device_id: str, issue: Dict) -> Dict:
        """Generate network-specific remediation steps"""
        remediation = {
            "device_id": device_id,
            "issue_type": issue.get("type"),
            "steps": [],
            "automation_script": None
        }
        
        issue_type = issue.get("type")
        
        if issue_type == "high_packet_loss":
            remediation["steps"] = [
                "Check interface statistics: show interfaces",
                "Verify physical layer connectivity",
                "Check for interface errors or CRC mismatches",
                "Review QoS configuration and bandwidth limits",
                "Consider interface replacement if errors persist"
            ]
            remediation["automation_script"] = self._generate_interface_check_script(
                issue.get("interface")
            )
        
        elif issue_type == "interface_errors":
            remediation["steps"] = [
                "Check interface error counters",
                "Verify cable integrity and connections",
                "Check for duplex mismatches",
                "Review interface configuration",
                "Consider interface reset if errors continue"
            ]
            remediation["automation_script"] = self._generate_interface_reset_script(
                issue.get("interface")
            )
        
        elif issue_type == "bgp_peer_down":
            remediation["steps"] = [
                "Check BGP neighbor status",
                "Verify network reachability to peer",
                "Review BGP configuration and authentication",
                "Check routing table for peer routes",
                "Verify ASN and peering configuration"
            ]
            remediation["automation_script"] = self._generate_bgp_check_script(
                issue.get("peer")
            )
        
        return remediation
    
    def _generate_interface_check_script(self, interface: str) -> str:
        """Generate network device command script for interface check"""
        return f"""# Network automation script for interface check
# Interface: {interface}

show interfaces {interface} statistics
show interfaces {interface} status
show interfaces {interface} errors
show interfaces {interface} counters detailed"""
    
    def _generate_interface_reset_script(self, interface: str) -> str:
        """Generate network device command script for interface reset"""
        return f"""# Network automation script for interface reset
# Interface: {interface}
# WARNING: This will cause brief service interruption

configure terminal
interface {interface}
shutdown
no shutdown
end
show interfaces {interface} status"""
    
    def _generate_bgp_check_script(self, peer: str) -> str:
        """Generate network device command script for BGP check"""
        return f"""# Network automation script for BGP peer check
# Peer: {peer}

show ip bgp neighbors {peer}
show ip bgp summary
show ip route {peer}
ping {peer}"""

