#!/usr/bin/env python3
"""
Test Suite for Runaway Monitor
=============================

Comprehensive tests for the API burn rate detection system.
"""

import os
import sys
import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitor import RunawayMonitor
from detectors.api_detector import APIUsageDetector, OpenAIDetector
from notifications.telegram_notifier import TelegramNotifier


class TestRunawayMonitor:
    """Test the main RunawayMonitor class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.config_data = {
            "monitoring_interval": 60,
            "cost_thresholds": {
                "openai": {"hourly": 5.0, "daily": 50.0}
            },
            "usage_spike_multiplier": 2.0,
            "circuit_breaker": {"enabled": True, "threshold_multiplier": 3.0}
        }
    
    @patch('monitor.json.load')
    @patch('builtins.open')
    def test_monitor_initialization(self, mock_open, mock_json_load):
        """Test monitor initialization"""
        mock_json_load.return_value = self.config_data
        
        monitor = RunawayMonitor("test_config.json")
        
        assert monitor.config_path == "test_config.json"
        assert monitor.config == self.config_data
        assert not monitor.monitoring_active
    
    @patch('monitor.json.load')
    @patch('builtins.open')
    def test_cost_threshold_detection(self, mock_open, mock_json_load):
        """Test cost threshold anomaly detection"""
        mock_json_load.return_value = self.config_data
        monitor = RunawayMonitor()
        
        # Test usage data that exceeds threshold
        usage_data = {"estimated_cost": 10.0}
        anomaly = monitor._check_cost_thresholds("openai", usage_data)
        
        assert anomaly is not None
        assert anomaly["type"] == "cost_threshold"
        assert anomaly["service"] == "openai"
        assert anomaly["current_cost"] == 10.0
    
    @patch('monitor.json.load')
    @patch('builtins.open')
    def test_usage_spike_detection(self, mock_open, mock_json_load):
        """Test usage spike anomaly detection"""
        mock_json_load.return_value = self.config_data
        monitor = RunawayMonitor()
        
        # Setup baseline
        monitor.baseline_usage = {
            "openai": {"requests_per_hour": 10}
        }
        
        # Test usage spike
        usage_data = {"requests_per_hour": 30}  # 3x baseline
        anomaly = monitor._check_usage_spikes("openai", usage_data)
        
        assert anomaly is not None
        assert anomaly["type"] == "usage_spike"
        assert anomaly["multiplier"] == 3.0
    
    @patch('monitor.json.load')
    @patch('builtins.open')
    def test_circuit_breaker_trigger(self, mock_open, mock_json_load):
        """Test circuit breaker triggering logic"""
        mock_json_load.return_value = self.config_data
        monitor = RunawayMonitor()
        
        # Test high severity anomaly
        high_severity_anomaly = {"severity": "high", "service": "openai"}
        assert monitor._should_trigger_circuit_breaker(high_severity_anomaly)
        
        # Test multiple medium severity anomalies
        monitor.anomalies_detected = [
            {"service": "openai", "severity": "medium"},
            {"service": "openai", "severity": "medium"},
            {"service": "openai", "severity": "medium"}
        ]
        medium_anomaly = {"severity": "medium", "service": "openai"}
        assert monitor._should_trigger_circuit_breaker(medium_anomaly)


class TestAPIUsageDetector:
    """Test the API usage detection system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.credentials = {
            "OPENAI_API_KEY": "test_key",
            "GITHUB_TOKEN": "test_token"
        }
    
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test_key",
        "GITHUB_TOKEN": "test_token"
    })
    def test_detector_initialization(self):
        """Test detector initialization with environment variables"""
        detector = APIUsageDetector()
        
        assert "OPENAI_API_KEY" in detector.credentials
        assert "GITHUB_TOKEN" in detector.credentials
    
    def test_openai_detector_configuration(self):
        """Test OpenAI detector configuration"""
        detector = OpenAIDetector()
        
        assert detector.get_required_credentials() == ["OPENAI_API_KEY"]
        assert detector.is_configured(self.credentials)
        assert not detector.is_configured({})
    
    @pytest.mark.asyncio
    async def test_openai_usage_detection(self):
        """Test OpenAI usage data collection"""
        detector = OpenAIDetector()
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = {"usage": "data"}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            session = Mock()
            usage_data = await detector.get_usage(session, self.credentials)
            
            assert "service" in usage_data
            assert usage_data["service"] == "openai"
            assert "timestamp" in usage_data


class TestTelegramNotifier:
    """Test the Telegram notification system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_bot_token",
            "TELEGRAM_CHANNEL_ID": "test_channel_id"
        }
    
    @patch.dict(os.environ, {
        "TELEGRAM_BOT_TOKEN": "test_token",
        "TELEGRAM_CHANNEL_ID": "test_channel"
    })
    def test_notifier_initialization(self):
        """Test notifier initialization"""
        notifier = TelegramNotifier()
        
        assert notifier.bot_token == "test_token"
        assert notifier.chat_id == "test_channel"
        assert notifier.is_configured()
    
    def test_notifier_not_configured(self):
        """Test behavior when not configured"""
        with patch.dict(os.environ, {}, clear=True):
            notifier = TelegramNotifier()
            assert not notifier.is_configured()
    
    @patch.dict(os.environ, {
        "TELEGRAM_BOT_TOKEN": "test_token",
        "TELEGRAM_CHANNEL_ID": "test_channel"
    })
    def test_message_formatting(self):
        """Test anomaly message formatting"""
        notifier = TelegramNotifier()
        
        anomaly = {
            "service": "openai",
            "type": "cost_threshold",
            "severity": "high",
            "message": "Cost exceeded threshold",
            "current_cost": 15.0,
            "threshold": 10.0,
            "timestamp": "2023-01-01T00:00:00"
        }
        
        message = notifier._format_anomaly_message(anomaly)
        
        assert "🚨 RUNAWAY DETECTED" in message
        assert "OPENAI" in message
        assert "$15.00" in message
        assert "$10.00" in message
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {
        "TELEGRAM_BOT_TOKEN": "test_token",
        "TELEGRAM_CHANNEL_ID": "test_channel"
    })
    async def test_send_message(self):
        """Test message sending functionality"""
        notifier = TelegramNotifier()
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_post.return_value.__aenter__.return_value = mock_response
            
            anomaly = {
                "service": "test",
                "type": "test",
                "severity": "medium",
                "message": "Test anomaly"
            }
            
            result = await notifier.send_anomaly_alert(anomaly)
            assert result is True


def run_integration_tests():
    """Run integration tests with real environment"""
    print("🧪 Running Runaway Monitor Integration Tests...")
    
    # Test 1: Environment variable loading
    print("\n📋 Test 1: Environment Variable Loading")
    detector = APIUsageDetector()
    loaded_vars = len(detector.credentials)
    print(f"   ✓ Loaded {loaded_vars} environment variables")
    
    # Test 2: Service detector configuration
    print("\n📋 Test 2: Service Detector Configuration")
    from detectors.api_detector import OpenAIDetector, GitHubDetector
    
    openai_detector = OpenAIDetector()
    github_detector = GitHubDetector()
    
    openai_configured = openai_detector.is_configured(detector.credentials)
    github_configured = github_detector.is_configured(detector.credentials)
    
    print(f"   ✓ OpenAI Detector: {'Configured' if openai_configured else 'Not Configured'}")
    print(f"   ✓ GitHub Detector: {'Configured' if github_configured else 'Not Configured'}")
    
    # Test 3: Telegram notifier configuration
    print("\n📋 Test 3: Telegram Notifier Configuration")
    notifier = TelegramNotifier()
    telegram_configured = notifier.is_configured()
    print(f"   ✓ Telegram Notifier: {'Configured' if telegram_configured else 'Not Configured'}")
    
    # Test 4: Monitor initialization
    print("\n📋 Test 4: Monitor Initialization")
    try:
        monitor = RunawayMonitor()
        print("   ✅ Monitor initialized successfully")
        
        status = monitor.get_status()
        print(f"   ✓ Status: {status['active']}")
        print(f"   ✓ Services: {status['services_monitored']}")
        
    except Exception as e:
        print(f"   ❌ Monitor initialization failed: {e}")
    
    print("\n🎉 Integration tests completed!")


async def run_async_tests():
    """Run async integration tests"""
    print("\n🔄 Running Async Integration Tests...")
    
    # Test API detector
    detector = APIUsageDetector()
    
    try:
        print("📡 Testing API usage detection...")
        usage_data = await detector.get_all_usage()
        print(f"   ✓ Retrieved data for {len(usage_data)} services")
        
        for service, data in usage_data.items():
            if "error" in data:
                print(f"   ⚠️  {service}: {data['error']}")
            else:
                print(f"   ✅ {service}: Active")
        
    except Exception as e:
        print(f"   ❌ API detection failed: {e}")
    
    finally:
        await detector.close()
    
    # Test Telegram notifications
    notifier = TelegramNotifier()
    if notifier.is_configured():
        print("\n📱 Testing Telegram notifications...")
        try:
            test_result = await notifier.test_connection()
            if test_result:
                print("   ✅ Telegram test message sent successfully")
            else:
                print("   ❌ Telegram test message failed")
        except Exception as e:
            print(f"   ❌ Telegram test error: {e}")


def main():
    """Main test runner"""
    print("🚀 Runaway Monitor Test Suite")
    print("=" * 50)
    
    # Run unit tests
    print("\n📋 Running Unit Tests...")
    try:
        pytest.main([__file__, "-v"])
    except SystemExit:
        pass  # pytest calls sys.exit
    
    # Run integration tests
    run_integration_tests()
    
    # Run async tests
    print("\n⚡ Running Async Tests...")
    asyncio.run(run_async_tests())
    
    print("\n✨ All tests completed!")


if __name__ == "__main__":
    main()