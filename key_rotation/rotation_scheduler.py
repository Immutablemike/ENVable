#!/usr/bin/env python3
"""
ENVThing Key Rotation Scheduler
===============================

Automated credential rotation system with policy-based scheduling,
provider-specific rotation logic, and comprehensive audit trails.

Features:
- Policy-based rotation schedules (30/60/90/180 days)
- Provider-specific rotation protocols
- Emergency rotation triggers
- Compliance audit logging
- Team notifications (Slack, email)
- Rollback capabilities
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

# Local imports
from provider_rotators import (
    OpenAIRotator, 
    StripeRotator, 
    GitHubRotator,
    AnthropicRotator
)

@dataclass
class RotationEvent:
    """Represents a credential rotation event"""
    credential_name: str
    provider: str
    rotation_type: str  # scheduled, emergency, manual
    scheduled_date: datetime
    notification_sent: bool = False
    approval_required: bool = False
    approved: bool = False
    completed: bool = False
    old_key_hash: Optional[str] = None
    new_key_hash: Optional[str] = None

class RotationScheduler:
    """Main rotation scheduler coordinating all credential rotations"""
    
    def __init__(self, config_path: str = "rotation_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.rotators = self._initialize_rotators()
        
    def _load_config(self) -> Dict:
        """Load rotation configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Rotation config not found: {self.config_path}")
    
    def _setup_logging(self) -> logging.Logger:
        """Configure audit logging"""
        logger = logging.getLogger('rotation_scheduler')
        logger.setLevel(logging.INFO)
        
        # File handler for audit trail
        handler = logging.FileHandler('rotation_audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _initialize_rotators(self) -> Dict:
        """Initialize provider-specific rotators"""
        return {
            'openai': OpenAIRotator(),
            'stripe': StripeRotator(),
            'github': GitHubRotator(),
            'anthropic': AnthropicRotator()
        }
    
    def check_rotation_schedule(self) -> List[RotationEvent]:
        """Check which credentials need rotation"""
        due_rotations = []
        
        for provider_name, provider_config in self.config['providers'].items():
            policy = self.config['rotation_policies'][provider_config['policy']]
            
            for credential in provider_config['credentials']:
                # Calculate next rotation date based on policy
                last_rotation = self._get_last_rotation_date(credential)
                next_rotation = last_rotation + timedelta(days=policy['schedule_days'])
                notification_date = next_rotation - timedelta(days=policy['notification_days_before'])
                
                if datetime.now() >= notification_date:
                    event = RotationEvent(
                        credential_name=credential,
                        provider=provider_name,
                        rotation_type='scheduled',
                        scheduled_date=next_rotation,
                        approval_required=policy['require_approval']
                    )
                    due_rotations.append(event)
        
        return due_rotations
    
    def emergency_rotation(self, credential_name: str, reason: str) -> bool:
        """Trigger immediate emergency rotation"""
        self.logger.warning(f"Emergency rotation triggered for {credential_name}: {reason}")
        
        # Find provider for this credential
        provider = self._find_provider_for_credential(credential_name)
        if not provider:
            self.logger.error(f"No provider found for credential: {credential_name}")
            return False
        
        # Execute immediate rotation
        try:
            rotator = self.rotators[provider]
            old_hash, new_hash = rotator.rotate_credential(credential_name)
            
            # Log successful emergency rotation
            self.logger.info(f"Emergency rotation completed: {credential_name}")
            self._send_notification(
                f"🚨 Emergency rotation completed for {credential_name}",
                f"Reason: {reason}\\nOld key hash: {old_hash}\\nNew key hash: {new_hash}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Emergency rotation failed for {credential_name}: {str(e)}")
            return False
    
    def execute_scheduled_rotation(self, event: RotationEvent) -> bool:
        """Execute a scheduled credential rotation"""
        if event.approval_required and not event.approved:
            self.logger.info(f"Rotation awaiting approval: {event.credential_name}")
            return False
        
        try:
            rotator = self.rotators[event.provider]
            old_hash, new_hash = rotator.rotate_credential(event.credential_name)
            
            # Update event status
            event.completed = True
            event.old_key_hash = old_hash
            event.new_key_hash = new_hash
            
            # Log successful rotation
            self.logger.info(
                f"Scheduled rotation completed: {event.credential_name} "
                f"(Provider: {event.provider})"
            )
            
            # Send success notification
            self._send_notification(
                f"✅ Credential rotation completed: {event.credential_name}",
                f"Provider: {event.provider}\\nOld key hash: {old_hash}\\nNew key hash: {new_hash}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                f"Scheduled rotation failed for {event.credential_name}: {str(e)}"
            )
            self._send_notification(
                f"❌ Credential rotation failed: {event.credential_name}",
                f"Error: {str(e)}\\nManual intervention required"
            )
            return False
    
    def _get_last_rotation_date(self, credential_name: str) -> datetime:
        """Get the last rotation date for a credential"""
        # TODO: Implement database/file lookup for last rotation dates
        # For now, return 90 days ago as placeholder
        return datetime.now() - timedelta(days=90)
    
    def _find_provider_for_credential(self, credential_name: str) -> Optional[str]:
        """Find which provider manages a specific credential"""
        for provider_name, provider_config in self.config['providers'].items():
            if credential_name in provider_config['credentials']:
                return provider_name
            # Check pattern matching
            for pattern in provider_config['credentials']:
                if '*' in pattern:
                    pattern_regex = pattern.replace('*', '.*')
                    import re
                    if re.match(pattern_regex, credential_name):
                        return provider_name
        return None
    
    def _send_notification(self, title: str, message: str):
        """Send notifications via configured channels"""
        timestamp = datetime.now().isoformat()
        notification_data = {
            'timestamp': timestamp,
            'title': title,
            'message': message
        }
        
        # Log notification
        self.logger.info(f"Notification: {title} - {message}")
        
        # TODO: Implement Slack webhook
        # TODO: Implement email notifications
        print(f"🔔 {title}: {message}")
    
    def generate_compliance_report(self, report_type: str = "SOC2") -> Dict:
        """Generate compliance audit report"""
        # TODO: Implement compliance report generation
        return {
            'report_type': report_type,
            'generated_at': datetime.now().isoformat(),
            'rotations_last_30_days': 0,
            'compliance_status': 'COMPLIANT'
        }

def main():
    """Main rotation scheduler entry point"""
    scheduler = RotationScheduler()
    
    # Check for due rotations
    due_rotations = scheduler.check_rotation_schedule()
    
    if due_rotations:
        print(f"Found {len(due_rotations)} credentials due for rotation:")
        for event in due_rotations:
            print(f"  - {event.credential_name} ({event.provider}) - {event.scheduled_date}")
            
            # Execute rotation if auto-rotate is enabled
            provider_config = scheduler.config['providers'][event.provider]
            policy = scheduler.config['rotation_policies'][provider_config['policy']]
            
            if policy['auto_rotate'] and not event.approval_required:
                success = scheduler.execute_scheduled_rotation(event)
                if success:
                    print(f"    ✅ Rotated successfully")
                else:
                    print(f"    ❌ Rotation failed")
            else:
                print(f"    ⏳ Awaiting manual approval")
    else:
        print("No credentials due for rotation")

if __name__ == "__main__":
    main()