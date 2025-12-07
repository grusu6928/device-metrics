"""AI-assisted remediation suggestions"""
from typing import Dict, Optional
from openai import OpenAI
from src.models.device_metric import DeviceMetric, Anomaly
from src.api.config import settings
import logging

logger = logging.getLogger(__name__)


class RemediationEngine:
    """Generate AI-powered remediation suggestions"""
    
    def __init__(self):
        """Initialize remediation engine"""
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            logger.warning("OpenAI API key not set, remediation suggestions will be rule-based")
        
        # Rule-based remediation knowledge base
        self.remediation_rules = {
            "value_spike": {
                "cpu_usage": [
                    "Check for runaway processes using 'top' or 'htop'",
                    "Review recent deployments or configuration changes",
                    "Consider horizontal scaling or resource limits"
                ],
                "memory_usage": [
                    "Check for memory leaks in applications",
                    "Review cache settings and memory allocation",
                    "Consider increasing available memory or optimizing usage"
                ],
                "disk_usage": [
                    "Check disk space with 'df -h'",
                    "Clean up log files and temporary data",
                    "Consider log rotation or archiving"
                ],
            },
            "value_drop": {
                "network_throughput": [
                    "Check network connectivity and routing",
                    "Review firewall rules and security groups",
                    "Verify service endpoints are reachable"
                ],
                "interface_errors": [
                    "Check interface error counters: show interfaces errors",
                    "Verify physical layer connectivity",
                    "Check for duplex mismatches",
                    "Review interface configuration"
                ],
                "packet_loss": [
                    "Check interface statistics and error counters",
                    "Verify QoS configuration and bandwidth limits",
                    "Review network congestion and utilization",
                    "Check for physical layer issues"
                ],
                "bgp_peer_status": [
                    "Check BGP neighbor status: show ip bgp neighbors",
                    "Verify network reachability to peer",
                    "Review BGP configuration and authentication",
                    "Check routing table for peer routes"
                ],
            },
            "known_pattern": [
                "Review historical incident reports for similar patterns",
                "Check if this matches a known issue with documented resolution",
                "Consider preventative measures based on past incidents"
            ],
            "statistical_outlier": [
                "Validate the metric value with manual verification",
                "Check for sensor or data collection issues",
                "Review recent system changes that might explain the deviation"
            ]
        }
    
    def generate_remediation(self, anomaly: Anomaly, metric: DeviceMetric) -> Dict:
        """
        Generate remediation suggestion for an anomaly
        
        Returns:
            Dict with suggestion, reasoning, and priority
        """
        # Try LLM-based suggestion first
        if self.client:
            suggestion = self._generate_llm_remediation(anomaly, metric)
            if suggestion:
                return suggestion
        
        # Fall back to rule-based
        return self._generate_rule_based_remediation(anomaly, metric)
    
    def _generate_llm_remediation(self, anomaly: Anomaly, metric: DeviceMetric) -> Optional[Dict]:
        """Generate remediation using LLM"""
        try:
            prompt = f"""As a DevOps engineer, provide a remediation suggestion for the following anomaly:

Device ID: {metric.device_id}
Metric Type: {metric.metric_type}
Metric Value: {metric.value} {metric.unit or ''}
Anomaly Classification: {anomaly.classification}
Anomaly Score: {anomaly.anomaly_score:.2f}
Timestamp: {metric.timestamp}

Metadata: {metric.metadata or 'None'}

Provide:
1. A specific, actionable remediation step (1-2 sentences)
2. Brief reasoning for why this remediation is appropriate
3. Priority level (high, medium, low)
4. Estimated impact of applying this remediation

Format your response as:
SUGGESTION: [your suggestion]
REASONING: [your reasoning]
PRIORITY: [high/medium/low]
IMPACT: [estimated impact]"""

            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an experienced DevOps engineer providing actionable remediation suggestions."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            return self._parse_llm_response(content)
        
        except Exception as e:
            logger.error(f"Error generating LLM remediation: {e}")
            return None
    
    def _parse_llm_response(self, content: str) -> Dict:
        """Parse LLM response into structured format"""
        suggestion = ""
        reasoning = ""
        priority = "medium"
        impact = None
        
        lines = content.split("\n")
        for line in lines:
            if line.startswith("SUGGESTION:"):
                suggestion = line.replace("SUGGESTION:", "").strip()
            elif line.startswith("REASONING:"):
                reasoning = line.replace("REASONING:", "").strip()
            elif line.startswith("PRIORITY:"):
                priority = line.replace("PRIORITY:", "").strip().lower()
            elif line.startswith("IMPACT:"):
                impact = line.replace("IMPACT:", "").strip()
        
        # Fallback if parsing fails
        if not suggestion:
            suggestion = content.split("\n")[0]
        
        return {
            "suggestion": suggestion,
            "reasoning": reasoning or "AI-generated suggestion based on anomaly pattern",
            "priority": priority if priority in ["high", "medium", "low"] else "medium",
            "estimated_impact": impact
        }
    
    def _generate_rule_based_remediation(self, anomaly: Anomaly, metric: DeviceMetric) -> Dict:
        """Generate remediation using rule-based approach"""
        classification = anomaly.classification or "unknown_anomaly"
        metric_type = metric.metric_type
        
        # Try classification-specific rules
        suggestions = []
        
        if classification in self.remediation_rules:
            rules = self.remediation_rules[classification]
            
            if isinstance(rules, dict) and metric_type in rules:
                suggestions = rules[metric_type]
            elif isinstance(rules, list):
                suggestions = rules
        
        # Fallback to generic suggestions
        if not suggestions:
            suggestions = [
                f"Investigate {metric_type} anomaly with score {anomaly.anomaly_score:.2f}",
                "Review device logs and recent configuration changes",
                "Monitor for pattern recurrence"
            ]
        
        # Determine priority based on anomaly score
        if anomaly.anomaly_score > 0.9:
            priority = "high"
        elif anomaly.anomaly_score > 0.7:
            priority = "medium"
        else:
            priority = "low"
        
        return {
            "suggestion": suggestions[0] if suggestions else "Review and investigate the anomaly",
            "reasoning": f"Based on {classification} pattern for {metric_type} metric",
            "priority": priority,
            "estimated_impact": "Medium - requires investigation"
        }

