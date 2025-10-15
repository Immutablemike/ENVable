#!/usr/bin/env python3
"""
API Usage Detector for Runaway Monitor
====================================

Detects usage patterns across multiple API services.
Public version - uses environment variables for credentials.
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import aiohttp


class APIUsageDetector:
    """Detect API usage patterns across multiple services"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = None
        
        # Load API credentials from environment
        self.credentials = self._load_credentials()
        
        # Service configurations
        self.services = {
            "openai": OpenAIDetector(),
            "github": GitHubDetector(),
            "stripe": StripeDetector(),
            "supabase": SupabaseDetector(),
            "cloudflare": CloudflareDetector()
        }
    
    def _load_credentials(self) -> Dict[str, str]:
        """Load API credentials from environment variables"""
        credentials = {}
        
        # Define expected environment variables
        env_vars = [
            "OPENAI_API_KEY",
            "GITHUB_TOKEN", 
            "STRIPE_API_KEY",
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "CLOUDFLARE_API_TOKEN",
            "CLOUDFLARE_ACCOUNT_ID"
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                credentials[var] = value
            else:
                self.logger.warning(f"Missing environment variable: {var}")
        
        return credentials
    
    async def get_all_usage(self) -> Dict[str, Any]:
        """Get usage data for all configured services"""
        usage_data = {}
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Check each service in parallel
            tasks = []
            for service_name, detector in self.services.items():
                if detector.is_configured(self.credentials):
                    task = self._get_service_usage(service_name, detector)
                    tasks.append(task)
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(results):
                    service_name = list(self.services.keys())[i]
                    if isinstance(result, Exception):
                        self.logger.error(f"Error getting {service_name} usage: {result}")
                    else:
                        usage_data[service_name] = result
        
        except Exception as e:
            self.logger.error(f"Error in get_all_usage: {e}")
        
        return usage_data
    
    async def _get_service_usage(self, service_name: str, detector) -> Dict[str, Any]:
        """Get usage data for a specific service"""
        try:
            return await detector.get_usage(self.session, self.credentials)
        except Exception as e:
            self.logger.error(f"Error getting {service_name} usage: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()


class BaseServiceDetector:
    """Base class for service-specific usage detectors"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def is_configured(self, credentials: Dict[str, str]) -> bool:
        """Check if required credentials are available"""
        required_creds = self.get_required_credentials()
        return all(cred in credentials for cred in required_creds)
    
    def get_required_credentials(self) -> List[str]:
        """Get list of required credential keys"""
        raise NotImplementedError
    
    async def get_usage(self, session: aiohttp.ClientSession, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Get usage data for this service"""
        raise NotImplementedError


class OpenAIDetector(BaseServiceDetector):
    """Detect OpenAI API usage and costs"""
    
    def get_required_credentials(self) -> List[str]:
        return ["OPENAI_API_KEY"]
    
    async def get_usage(self, session: aiohttp.ClientSession, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Get OpenAI usage data"""
        api_key = credentials["OPENAI_API_KEY"]
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Get usage data from OpenAI API
            # Note: This is a simplified example - actual implementation would need
            # to handle OpenAI's billing API properly
            
            usage_data = {
                "service": "openai",
                "timestamp": datetime.now().isoformat(),
                "requests_per_hour": 0,  # Would be calculated from actual API
                "estimated_cost": 0.0,   # Would be calculated from token usage
                "tokens_used": 0,
                "status": "active",
                "last_activity": datetime.now().isoformat()
            }
            
            return usage_data
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return {"error": str(e), "service": "openai"}


class GitHubDetector(BaseServiceDetector):
    """Detect GitHub Actions usage and costs"""
    
    def get_required_credentials(self) -> List[str]:
        return ["GITHUB_TOKEN"]
    
    async def get_usage(self, session: aiohttp.ClientSession, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Get GitHub Actions usage data"""
        token = credentials["GITHUB_TOKEN"]
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            # Get GitHub Actions usage
            # This would connect to GitHub's billing API
            
            usage_data = {
                "service": "github",
                "timestamp": datetime.now().isoformat(),
                "requests_per_hour": 0,
                "estimated_cost": 0.0,
                "minutes_used": 0,
                "status": "active",
                "last_activity": datetime.now().isoformat()
            }
            
            return usage_data
            
        except Exception as e:
            self.logger.error(f"GitHub API error: {e}")
            return {"error": str(e), "service": "github"}


class StripeDetector(BaseServiceDetector):
    """Detect Stripe payment processing usage"""
    
    def get_required_credentials(self) -> List[str]:
        return ["STRIPE_API_KEY"]
    
    async def get_usage(self, session: aiohttp.ClientSession, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Get Stripe usage data"""
        api_key = credentials["STRIPE_API_KEY"]
        
        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        
        try:
            # Get Stripe transaction data
            usage_data = {
                "service": "stripe",
                "timestamp": datetime.now().isoformat(),
                "requests_per_hour": 0,
                "estimated_cost": 0.0,
                "transactions": 0,
                "status": "active",
                "last_activity": datetime.now().isoformat()
            }
            
            return usage_data
            
        except Exception as e:
            self.logger.error(f"Stripe API error: {e}")
            return {"error": str(e), "service": "stripe"}


class SupabaseDetector(BaseServiceDetector):
    """Detect Supabase database usage"""
    
    def get_required_credentials(self) -> List[str]:
        return ["SUPABASE_URL", "SUPABASE_ANON_KEY"]
    
    async def get_usage(self, session: aiohttp.ClientSession, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Get Supabase usage data"""
        url = credentials["SUPABASE_URL"]
        key = credentials["SUPABASE_ANON_KEY"]
        
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
        }
        
        try:
            # Get Supabase usage data
            usage_data = {
                "service": "supabase",
                "timestamp": datetime.now().isoformat(),
                "requests_per_hour": 0,
                "estimated_cost": 0.0,
                "database_operations": 0,
                "status": "active",
                "last_activity": datetime.now().isoformat()
            }
            
            return usage_data
            
        except Exception as e:
            self.logger.error(f"Supabase API error: {e}")
            return {"error": str(e), "service": "supabase"}


class CloudflareDetector(BaseServiceDetector):
    """Detect Cloudflare R2 storage usage"""
    
    def get_required_credentials(self) -> List[str]:
        return ["CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID"]
    
    async def get_usage(self, session: aiohttp.ClientSession, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Get Cloudflare usage data"""
        token = credentials["CLOUDFLARE_API_TOKEN"]
        account_id = credentials["CLOUDFLARE_ACCOUNT_ID"]
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Get Cloudflare usage data
            usage_data = {
                "service": "cloudflare",
                "timestamp": datetime.now().isoformat(),
                "requests_per_hour": 0,
                "estimated_cost": 0.0,
                "storage_operations": 0,
                "status": "active",
                "last_activity": datetime.now().isoformat()
            }
            
            return usage_data
            
        except Exception as e:
            self.logger.error(f"Cloudflare API error: {e}")
            return {"error": str(e), "service": "cloudflare"}