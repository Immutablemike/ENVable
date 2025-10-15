# Runaway Monitor Package
"""
Runaway Monitor - API Burn Rate Detection System
==============================================

A comprehensive monitoring system that detects runaway processes burning through
API tokens, credits, and cloud resources across multiple services.
"""

__version__ = "1.0.0"
__author__ = "ENVThing Team"

from .monitor import RunawayMonitor
from .detectors.api_detector import APIUsageDetector
from .notifications.telegram_notifier import TelegramNotifier

__all__ = [
    "RunawayMonitor",
    "APIUsageDetector", 
    "TelegramNotifier"
]