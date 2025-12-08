"""Tests for network automation features"""

import pytest

from src.services.network_automation import NetworkAutomationService, NetworkDeviceManager


def test_network_device_manager():
    """Test network device manager"""
    manager = NetworkDeviceManager()

    # Test metric validation
    assert manager.validate_network_metric("device-001", "interface_throughput", 50.0, {})
    assert not manager.validate_network_metric("device-001", "interface_throughput", 150.0, {})

    # Test device summary
    metrics = [
        {
            "metric_type": "interface_throughput",
            "value": 75.0,
            "metadata": {"interface": "GigabitEthernet0/1"},
        },
        {"metric_type": "packet_loss", "value": 0.5, "metadata": {}},
    ]

    summary = manager.get_network_device_summary("device-001", metrics)
    assert summary["device_id"] == "device-001"
    assert "network_health" in summary
    assert "interfaces" in summary


def test_network_automation_service():
    """Test network automation service"""
    manager = NetworkDeviceManager()
    service = NetworkAutomationService(manager)

    issue = {"type": "high_packet_loss", "interface": "GigabitEthernet0/1", "value": 10.0}

    remediation = service.generate_network_remediation("device-001", issue)
    assert remediation["device_id"] == "device-001"
    assert "steps" in remediation
    assert "automation_script" in remediation
    assert len(remediation["steps"]) > 0
