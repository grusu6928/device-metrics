"""AI-powered natural language health summaries"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from openai import OpenAI
from sqlalchemy.orm import Session

from src.api.config import settings
from src.models.device_metric import Anomaly, DeviceMetric

logger = logging.getLogger(__name__)


class HealthSummarizer:
    """Generate natural language summaries of device health using LLM"""

    def __init__(self):
        """Initialize health summarizer"""
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            logger.warning("OpenAI API key not set, health summaries will be rule-based")

    def summarize_device_health(self, device_id: str, db: Session, recent_hours: int = 24) -> Dict:
        """
        Generate a natural language summary of device health

        Returns:
            Dict with summary, health status, and key metrics
        """
        # Fetch recent metrics and anomalies
        from datetime import timedelta

        cutoff_time = datetime.utcnow().replace(microsecond=0) - timedelta(hours=recent_hours)

        metrics = (
            db.query(DeviceMetric)
            .filter(DeviceMetric.device_id == device_id, DeviceMetric.timestamp >= cutoff_time)
            .order_by(DeviceMetric.timestamp.desc())
            .limit(100)
            .all()
        )

        anomalies = (
            db.query(Anomaly)
            .join(DeviceMetric)
            .filter(DeviceMetric.device_id == device_id, Anomaly.detected_at >= cutoff_time)
            .order_by(Anomaly.detected_at.desc())
            .limit(settings.MAX_ANOMALIES_FOR_SUMMARY)
            .all()
        )

        if not metrics:
            return {
                "summary": f"No metrics found for device {device_id} in the last {recent_hours} hours.",
                "overall_health": "unknown",
                "key_metrics": {},
                "anomalies_detected": 0,
            }

        # Extract key metrics
        key_metrics = self._extract_key_metrics(metrics)

        # Determine overall health
        overall_health = self._determine_health_status(metrics, anomalies)

        # Generate summary
        if self.client:
            summary = self._generate_llm_summary(device_id, metrics, anomalies, key_metrics)
        else:
            summary = self._generate_rule_based_summary(device_id, metrics, anomalies, key_metrics)

        return {
            "summary": summary,
            "overall_health": overall_health,
            "key_metrics": key_metrics,
            "anomalies_detected": len(anomalies),
            "generated_at": datetime.utcnow(),
        }

    def _extract_key_metrics(self, metrics: List[DeviceMetric]) -> Dict:
        """Extract key metrics from recent data"""
        key_metrics = {}

        # Group by metric type
        by_type = {}
        for metric in metrics:
            if metric.metric_type not in by_type:
                by_type[metric.metric_type] = []
            by_type[metric.metric_type].append(metric.value)

        # Calculate statistics for each type
        for metric_type, values in by_type.items():
            if values:
                key_metrics[metric_type] = {
                    "current": values[0],
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values),
                }

        return key_metrics

    def _determine_health_status(
        self, metrics: List[DeviceMetric], anomalies: List[Anomaly]
    ) -> str:
        """Determine overall device health status"""
        if not metrics:
            return "unknown"

        # Check for critical anomalies
        critical_count = sum(1 for a in anomalies if a.anomaly_score > 0.9)
        if critical_count > 0:
            return "critical"

        # Check metric values
        recent_metrics = metrics[:10]  # Last 10 metrics
        critical_metrics = 0

        for metric in recent_metrics:
            # Simple thresholds (can be made configurable)
            if metric.metric_type == "cpu_usage" and metric.value > 95:
                critical_metrics += 1
            elif metric.metric_type == "memory_usage" and metric.value > 95:
                critical_metrics += 1

        if critical_metrics >= 3:
            return "critical"
        elif len(anomalies) > 5 or critical_metrics > 0:
            return "degraded"
        else:
            return "healthy"

    def _generate_llm_summary(
        self,
        device_id: str,
        metrics: List[DeviceMetric],
        anomalies: List[Anomaly],
        key_metrics: Dict,
    ) -> str:
        """Generate summary using LLM"""
        try:
            # Prepare context
            metrics_text = "\n".join(
                [
                    f"- {m.metric_type}: {m.value} {m.unit or ''} at {m.timestamp}"
                    for m in metrics[:20]  # Limit context
                ]
            )

            anomalies_text = ""
            if anomalies:
                anomalies_text = "\n".join(
                    [
                        f"- {a.classification} (score: {a.anomaly_score:.2f}) at {a.detected_at}"
                        for a in anomalies[:10]
                    ]
                )

            prompt = f"""Generate a concise, natural-language health summary for device {device_id}.

Recent Metrics:
{metrics_text}

Anomalies Detected:
{anomalies_text if anomalies_text else "None"}

Key Statistics:
{self._format_key_metrics(key_metrics)}

Provide a 2-3 sentence summary that:
1. Describes the overall device health status
2. Highlights any concerning patterns or anomalies
3. Mentions key metrics that stand out

Keep it professional and actionable."""

            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a DevOps engineer providing device health summaries.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=200,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating LLM summary: {e}")
            return self._generate_rule_based_summary(device_id, metrics, anomalies, key_metrics)

    def _generate_rule_based_summary(
        self,
        device_id: str,
        metrics: List[DeviceMetric],
        anomalies: List[Anomaly],
        key_metrics: Dict,
    ) -> str:
        """Generate summary using rule-based approach"""
        parts = [f"Device {device_id} health summary:"]

        if anomalies:
            parts.append(f"{len(anomalies)} anomaly(s) detected in the monitoring period.")
            critical = [a for a in anomalies if a.anomaly_score > 0.9]
            if critical:
                parts.append(f"{len(critical)} critical anomaly(s) require immediate attention.")
        else:
            parts.append("No anomalies detected.")

        # Add key metrics
        if key_metrics:
            metric_parts = []
            for metric_type, stats in list(key_metrics.items())[:3]:
                metric_parts.append(
                    f"{metric_type} at {stats['current']:.1f} " f"(avg: {stats['average']:.1f})"
                )
            if metric_parts:
                parts.append(f"Current metrics: {', '.join(metric_parts)}.")

        return " ".join(parts)

    def _format_key_metrics(self, key_metrics: Dict) -> str:
        """Format key metrics for LLM prompt"""
        lines = []
        for metric_type, stats in key_metrics.items():
            lines.append(
                f"{metric_type}: current={stats['current']:.2f}, "
                f"avg={stats['average']:.2f}, "
                f"range=[{stats['min']:.2f}-{stats['max']:.2f}]"
            )
        return "\n".join(lines)
