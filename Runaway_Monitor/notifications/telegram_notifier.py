#!/usr/bin/env python3
"""
Telegram Notifier for Runaway Monitor
====================================

Sends real-time alerts via Telegram when runaway processes are detected.
Public version - uses environment variables for credentials.
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any
import aiohttp


class TelegramNotifier:
    """Telegram notification system for runaway process alerts"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Load Telegram credentials from environment
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHANNEL_ID') 
        self.critical_chat_id = os.getenv('TELEGRAM_CRITICAL_CHANNEL_ID', self.chat_id)
        
        # Telegram API endpoint
        if self.bot_token:
            self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        else:
            self.api_url = None
            self.logger.warning("TELEGRAM_BOT_TOKEN not found in environment variables")

    def is_configured(self) -> bool:
        """Check if Telegram notifications are properly configured"""
        return bool(self.bot_token and self.chat_id)

    async def send_anomaly_alert(self, anomaly: Dict[str, Any]) -> bool:
        """Send anomaly alert to Telegram"""
        if not self.is_configured():
            self.logger.warning("Telegram not configured, skipping alert")
            return False
        
        # Format the alert message
        message = self._format_anomaly_message(anomaly)
        
        # Choose chat based on severity
        chat_id = self.critical_chat_id if anomaly.get("severity") == "high" else self.chat_id
        
        return await self._send_message(message, chat_id)

    async def send_critical_alert(self, message: str) -> bool:
        """Send critical alert to high-priority channel"""
        if not self.is_configured():
            self.logger.warning("Telegram not configured, skipping critical alert")
            return False
        
        formatted_message = f"🚨 CRITICAL ALERT 🚨\n\n{message}"
        return await self._send_message(formatted_message, self.critical_chat_id)

    async def send_status_update(self, status: Dict[str, Any]) -> bool:
        """Send monitoring status update"""
        if not self.is_configured():
            return False
        
        message = self._format_status_message(status)
        return await self._send_message(message, self.chat_id)

    async def send_daily_summary(self, summary: Dict[str, Any]) -> bool:
        """Send daily usage summary"""
        if not self.is_configured():
            return False
        
        message = self._format_daily_summary(summary)
        return await self._send_message(message, self.chat_id)

    def _format_anomaly_message(self, anomaly: Dict[str, Any]) -> str:
        """Format anomaly data into readable message"""
        severity_emoji = "🚨" if anomaly.get("severity") == "high" else "⚠️"
        service = anomaly.get("service", "Unknown")
        anomaly_type = anomaly.get("type", "unknown")
        message = anomaly.get("message", "No details available")
        
        formatted = f"{severity_emoji} RUNAWAY DETECTED\n\n"
        formatted += f"Service: {service.upper()}\n"
        formatted += f"Type: {anomaly_type.replace('_', ' ').title()}\n"
        formatted += f"Details: {message}\n"
        
        # Add specific metrics based on anomaly type
        if anomaly_type == "cost_threshold":
            current_cost = anomaly.get("current_cost", 0)
            threshold = anomaly.get("threshold", 0)
            formatted += f"\n💰 Cost: ${current_cost:.2f} (Threshold: ${threshold:.2f})"
        
        elif anomaly_type == "usage_spike":
            multiplier = anomaly.get("multiplier", 0)
            current_requests = anomaly.get("current_requests", 0)
            baseline_requests = anomaly.get("baseline_requests", 0)
            formatted += f"\n📈 Spike: {multiplier:.1f}x baseline"
            formatted += f"\n📊 Current: {current_requests} req/h"
            formatted += f"\n📊 Baseline: {baseline_requests} req/h"
        
        formatted += f"\n⏰ Time: {anomaly.get('timestamp', 'Unknown')}"
        
        return formatted

    def _format_status_message(self, status: Dict[str, Any]) -> str:
        """Format status data into readable message"""
        active = "🟢 ACTIVE" if status.get("active", False) else "🔴 INACTIVE"
        last_check = status.get("last_check", "Never")
        anomalies = status.get("anomalies_detected", 0)
        services = status.get("services_monitored", 0)
        
        message = f"🤖 RUNAWAY MONITOR STATUS\n\n"
        message += f"Status: {active}\n"
        message += f"Last Check: {last_check}\n"
        message += f"Services: {services}\n"
        message += f"Anomalies: {anomalies}\n"
        
        return message

    def _format_daily_summary(self, summary: Dict[str, Any]) -> str:
        """Format daily summary data"""
        total_cost = summary.get("total_estimated_cost", 0)
        total_requests = summary.get("total_requests", 0)
        top_service = summary.get("highest_cost_service", "None")
        anomalies = summary.get("anomalies_today", 0)
        
        message = f"📊 DAILY USAGE SUMMARY\n\n"
        message += f"💰 Total Cost: ${total_cost:.2f}\n"
        message += f"📈 Total Requests: {total_requests:,}\n"
        message += f"🥇 Top Service: {top_service}\n"
        message += f"🚨 Anomalies: {anomalies}\n"
        
        # Add service breakdown
        services = summary.get("service_breakdown", {})
        if services:
            message += "\n📋 Service Breakdown:\n"
            for service, data in services.items():
                cost = data.get("cost", 0)
                requests = data.get("requests", 0)
                message += f"• {service}: ${cost:.2f} ({requests:,} req)\n"
        
        return message

    async def _send_message(self, message: str, chat_id: str) -> bool:
        """Send message to Telegram"""
        if not self.api_url:
            self.logger.error("Telegram API URL not configured")
            return False
        
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        self.logger.debug(f"Message sent successfully to {chat_id}")
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Telegram API error {response.status}: {error_text}")
                        return False
        
        except Exception as e:
            self.logger.error(f"Error sending Telegram message: {e}")
            return False

    async def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        if not self.is_configured():
            self.logger.error("Telegram not configured for testing")
            return False
        
        test_message = "🤖 Runaway Monitor Test - Connection OK!"
        result = await self._send_message(test_message, self.chat_id)
        
        if result:
            self.logger.info("✅ Telegram connection test successful")
        else:
            self.logger.error("❌ Telegram connection test failed")
        
        return result