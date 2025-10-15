#!/usr/bin/env python3
"""
Runaway Monitor - API Burn Rate Detection System
==============================================

Main monitoring engine that detects runaway processes burning through
API tokens, credits, and cloud resources.

Public version - uses environment variables for credential management.
"""

import os
import sys
import time
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

from detectors.api_detector import APIUsageDetector
from notifications.telegram_notifier import TelegramNotifier

class RunawayMonitor:
    """Main monitoring engine for detecting API burn rate anomalies"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/monitor_config.json"
        
        # Initialize components
        self.api_detector = APIUsageDetector()
        self.telegram_notifier = TelegramNotifier()
        
        # Load configuration
        self.config = self._load_config()
        
        # Monitoring state
        self.monitoring_active = False
        self.last_check = None
        self.anomalies_detected = []
        self.baseline_usage = {}
        
        # Setup logging
        self._setup_logging()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file {self.config_path} not found, using defaults")
            return self._default_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default monitoring configuration"""
        return {
            "monitoring_interval": 300,  # 5 minutes
            "cost_thresholds": {
                "openai": {"hourly": 10.0, "daily": 100.0},
                "github_actions": {"hourly": 5.0, "daily": 50.0},
                "stripe": {"hourly": 50.0, "daily": 500.0},
                "supabase": {"hourly": 5.0, "daily": 25.0}
            },
            "usage_spike_multiplier": 3.0,
            "circuit_breaker": {
                "enabled": True,
                "threshold_multiplier": 5.0
            },
            "alert_cooldown": 1800  # 30 minutes
        }
    
    def _setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    async def start_monitoring(self):
        """Start the continuous monitoring process"""
        self.logger.info("🚀 Starting Runaway Monitor...")
        self.monitoring_active = True
        
        # Initialize baseline usage
        await self._establish_baseline()
        
        # Start monitoring loop
        while self.monitoring_active:
            try:
                await self._monitoring_cycle()
                await asyncio.sleep(self.config["monitoring_interval"])
            except KeyboardInterrupt:
                self.logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _establish_baseline(self):
        """Establish baseline usage patterns"""
        self.logger.info("📊 Establishing baseline usage patterns...")
        
        try:
            current_usage = await self.api_detector.get_all_usage()
            self.baseline_usage = current_usage
            self.logger.info(f"✅ Baseline established for {len(current_usage)} services")
        except Exception as e:
            self.logger.error(f"❌ Failed to establish baseline: {e}")
    
    async def _monitoring_cycle(self):
        """Single monitoring cycle"""
        cycle_start = datetime.now()
        self.logger.debug(f"🔍 Starting monitoring cycle at {cycle_start}")
        
        try:
            # Get current usage for all services
            current_usage = await self.api_detector.get_all_usage()
            
            # Analyze for anomalies
            anomalies = await self._detect_anomalies(current_usage)
            
            # Send alerts if needed
            if anomalies:
                await self._handle_anomalies(anomalies)
            
            # Update tracking
            self.last_check = cycle_start
            
        except Exception as e:
            self.logger.error(f"❌ Error in monitoring cycle: {e}")
    
    async def _detect_anomalies(self, current_usage: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect usage anomalies based on thresholds and patterns"""
        anomalies = []
        
        for service, usage_data in current_usage.items():
            try:
                # Check cost thresholds
                cost_anomaly = self._check_cost_thresholds(service, usage_data)
                if cost_anomaly:
                    anomalies.append(cost_anomaly)
                
                # Check usage spikes
                spike_anomaly = self._check_usage_spikes(service, usage_data)
                if spike_anomaly:
                    anomalies.append(spike_anomaly)
                
            except Exception as e:
                self.logger.error(f"❌ Error checking {service}: {e}")
        
        return anomalies
    
    def _check_cost_thresholds(self, service: str, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if service costs exceed thresholds"""
        service_config = self.config["cost_thresholds"].get(service, {})
        
        if not service_config:
            return None
        
        current_cost = usage_data.get("estimated_cost", 0)
        hourly_threshold = service_config.get("hourly", float('inf'))
        daily_threshold = service_config.get("daily", float('inf'))
        
        if current_cost > hourly_threshold:
            return {
                "type": "cost_threshold",
                "service": service,
                "severity": "high" if current_cost > hourly_threshold * 2 else "medium",
                "current_cost": current_cost,
                "threshold": hourly_threshold,
                "message": f"{service} hourly cost ${current_cost:.2f} exceeds threshold ${hourly_threshold:.2f}"
            }
        
        return None
    
    def _check_usage_spikes(self, service: str, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for unusual usage spikes"""
        if service not in self.baseline_usage:
            return None
        
        baseline = self.baseline_usage[service]
        current_requests = usage_data.get("requests_per_hour", 0)
        baseline_requests = baseline.get("requests_per_hour", 0)
        
        if baseline_requests == 0:
            return None
        
        multiplier = current_requests / baseline_requests
        spike_threshold = self.config["usage_spike_multiplier"]
        
        if multiplier > spike_threshold:
            return {
                "type": "usage_spike",
                "service": service,
                "severity": "high" if multiplier > spike_threshold * 2 else "medium",
                "current_requests": current_requests,
                "baseline_requests": baseline_requests,
                "multiplier": multiplier,
                "message": f"{service} usage spike: {multiplier:.1f}x baseline ({current_requests} vs {baseline_requests} req/hour)"
            }
        
        return None
    
    async def _handle_anomalies(self, anomalies: List[Dict[str, Any]]):
        """Handle detected anomalies"""
        for anomaly in anomalies:
            self.logger.warning(f"🚨 ANOMALY DETECTED: {anomaly['message']}")
            
            # Send Telegram alert
            await self.telegram_notifier.send_anomaly_alert(anomaly)
            
            # Check if circuit breaker should trigger
            if self._should_trigger_circuit_breaker(anomaly):
                await self._trigger_circuit_breaker(anomaly)
            
            # Add to anomaly history
            anomaly["timestamp"] = datetime.now().isoformat()
            self.anomalies_detected.append(anomaly)
    
    def _should_trigger_circuit_breaker(self, anomaly: Dict[str, Any]) -> bool:
        """Determine if circuit breaker should be triggered"""
        if not self.config["circuit_breaker"]["enabled"]:
            return False
        
        if anomaly["severity"] == "high":
            return True
        
        # Check for multiple medium severity anomalies
        recent_anomalies = [
            a for a in self.anomalies_detected[-10:]  # Last 10 anomalies
            if a.get("service") == anomaly["service"]
        ]
        
        return len(recent_anomalies) >= 3
    
    async def _trigger_circuit_breaker(self, anomaly: Dict[str, Any]):
        """Trigger emergency circuit breaker"""
        self.logger.critical(f"🚨 CIRCUIT BREAKER TRIGGERED for {anomaly['service']}")
        
        # Send critical alert
        await self.telegram_notifier.send_critical_alert(
            f"🚨 CIRCUIT BREAKER ACTIVATED\n"
            f"Service: {anomaly['service']}\n"
            f"Reason: {anomaly['message']}\n"
            f"Monitoring paused for this service."
        )
        
        # Could implement actual service shutdown here
        # For now, just log and alert
    
    def stop_monitoring(self):
        """Stop the monitoring process"""
        self.logger.info("🛑 Stopping monitoring...")
        self.monitoring_active = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "active": self.monitoring_active,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "anomalies_detected": len(self.anomalies_detected),
            "services_monitored": len(self.baseline_usage),
            "config": self.config
        }

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Runaway Monitor - API Burn Rate Detection')
    parser.add_argument('--start', action='store_true', help='Start monitoring')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--config', type=str, help='Config file path')
    
    args = parser.parse_args()
    
    monitor = RunawayMonitor(config_path=args.config)
    
    if args.start:
        await monitor.start_monitoring()
    elif args.status:
        status = monitor.get_status()
        print(json.dumps(status, indent=2))
    else:
        print("Use --start to begin monitoring or --status to check current state")

if __name__ == "__main__":
    asyncio.run(main())