#!/usr/bin/env python3
"""
Environment Processor
=====================

Core environment variable processing for ENVThing 2.0.
Provides direct access to all credentials and environment variables
with intelligent caching and real-time updates.

Features:
- Direct credential access via .available_credentials
- Environment variable processing and validation
- Automatic reloading on file changes
- Integration with AdvancedCredentialMatcher

Author: ENVThing 2.0 System
Date: July 21, 2025
"""

import os
import json
import time
from typing import Dict, Any, Optional
from pathlib import Path
import threading

class ENVProcessor:
    def __init__(self, env_file_path: Optional[str] = None):
        """Initialize the environment processor"""
        self.env_file_path = env_file_path or os.path.join(os.getcwd(), '.env')
        self._available_credentials = {}
        self._last_modified = 0
        self._lock = threading.Lock()
        
        # Load credentials initially
        self.refresh_credentials()
    
    @property
    def available_credentials(self) -> Dict[str, str]:
        """
        Access to all available credentials with automatic refresh
        
        Returns:
            Dictionary of all environment variables/credentials
        """
        # Check if file has been modified
        if os.path.exists(self.env_file_path):
            current_modified = os.path.getmtime(self.env_file_path)
            if current_modified > self._last_modified:
                self.refresh_credentials()
        
        return self._available_credentials
    
    def refresh_credentials(self):
        """Reload credentials from the environment file"""
        with self._lock:
            self._available_credentials = {}
            
            # Load from .env file
            if os.path.exists(self.env_file_path):
                try:
                    with open(self.env_file_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                self._available_credentials[key.strip()] = value.strip()
                    
                    self._last_modified = os.path.getmtime(self.env_file_path)
                    
                except Exception as e:
                    print(f"Warning: Could not load credentials from {self.env_file_path}: {e}")
            
            # Also load from actual environment variables
            for key, value in os.environ.items():
                if key not in self._available_credentials:
                    self._available_credentials[key] = value
    
    def get_credential(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a specific credential by key
        
        Args:
            key: The credential key to retrieve
            default: Default value if key not found
            
        Returns:
            The credential value or default
        """
        return self.available_credentials.get(key, default)
    
    def set_credential(self, key: str, value: str, persist: bool = True):
        """
        Set a credential value
        
        Args:
            key: The credential key
            value: The credential value
            persist: Whether to save to the .env file
        """
        with self._lock:
            self._available_credentials[key] = value
            
            if persist:
                self._append_to_env_file(key, value)
    
    def _append_to_env_file(self, key: str, value: str):
        """Append a new credential to the .env file"""
        try:
            # Check if key already exists
            existing_lines = []
            key_exists = False
            
            if os.path.exists(self.env_file_path):
                with open(self.env_file_path, 'r') as f:
                    existing_lines = f.readlines()
                
                # Update existing key or mark for addition
                for i, line in enumerate(existing_lines):
                    if line.strip().startswith(f"{key}="):
                        existing_lines[i] = f"{key}={value}\n"
                        key_exists = True
                        break
            
            # Write back the file
            with open(self.env_file_path, 'w') as f:
                f.writelines(existing_lines)
                
                # Add new key if it didn't exist
                if not key_exists:
                    f.write(f"\n# Added by ENVProcessor\n{key}={value}\n")
                    
        except Exception as e:
            print(f"Warning: Could not persist credential {key}: {e}")
    
    def remove_credential(self, key: str, persist: bool = True):
        """
        Remove a credential
        
        Args:
            key: The credential key to remove
            persist: Whether to remove from the .env file
        """
        with self._lock:
            if key in self._available_credentials:
                del self._available_credentials[key]
            
            if persist:
                self._remove_from_env_file(key)
    
    def _remove_from_env_file(self, key: str):
        """Remove a credential from the .env file"""
        try:
            if not os.path.exists(self.env_file_path):
                return
            
            with open(self.env_file_path, 'r') as f:
                lines = f.readlines()
            
            # Filter out the key
            filtered_lines = [
                line for line in lines 
                if not line.strip().startswith(f"{key}=")
            ]
            
            with open(self.env_file_path, 'w') as f:
                f.writelines(filtered_lines)
                
        except Exception as e:
            print(f"Warning: Could not remove credential {key}: {e}")
    
    def get_credentials_by_prefix(self, prefix: str) -> Dict[str, str]:
        """
        Get all credentials starting with a prefix
        
        Args:
            prefix: The prefix to search for
            
        Returns:
            Dictionary of matching credentials
        """
        return {
            key: value for key, value in self.available_credentials.items()
            if key.startswith(prefix)
        }
    
    def validate_required_credentials(self, required_keys: list) -> Dict[str, Any]:
        """
        Validate that all required credentials are present
        
        Args:
            required_keys: List of required credential keys
            
        Returns:
            Dictionary with validation results
        """
        missing = []
        present = []
        
        for key in required_keys:
            if key in self.available_credentials and self.available_credentials[key].strip():
                present.append(key)
            else:
                missing.append(key)
        
        return {
            'valid': len(missing) == 0,
            'missing': missing,
            'present': present,
            'total_required': len(required_keys),
            'found': len(present)
        }
    
    def export_credentials(self, keys: Optional[list] = None, format: str = 'env') -> str:
        """
        Export credentials in various formats
        
        Args:
            keys: Specific keys to export (None for all)
            format: Export format ('env', 'json', 'yaml')
            
        Returns:
            Formatted credential string
        """
        creds_to_export = self.available_credentials
        
        if keys:
            creds_to_export = {
                key: value for key, value in self.available_credentials.items()
                if key in keys
            }
        
        if format == 'json':
            return json.dumps(creds_to_export, indent=2)
        elif format == 'yaml':
            import yaml
            return yaml.dump(creds_to_export, default_flow_style=False)
        else:  # env format
            lines = []
            for key, value in sorted(creds_to_export.items()):
                lines.append(f"{key}={value}")
            return '\n'.join(lines)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about loaded credentials
        
        Returns:
            Dictionary with statistics
        """
        creds = self.available_credentials
        
        stats = {
            'total_credentials': len(creds),
            'file_path': self.env_file_path,
            'file_exists': os.path.exists(self.env_file_path),
            'last_modified': time.ctime(self._last_modified) if self._last_modified else 'Never',
            'categories': {}
        }
        
        # Categorize credentials
        categories = {
            'api_keys': 0,
            'tokens': 0,
            'passwords': 0,
            'urls': 0,
            'other': 0
        }
        
        for key in creds.keys():
            key_upper = key.upper()
            if 'API_KEY' in key_upper or 'APIKEY' in key_upper:
                categories['api_keys'] += 1
            elif 'TOKEN' in key_upper:
                categories['tokens'] += 1
            elif 'PASSWORD' in key_upper or 'PWD' in key_upper or 'PASS' in key_upper:
                categories['passwords'] += 1
            elif 'URL' in key_upper or 'URI' in key_upper or 'HOST' in key_upper:
                categories['urls'] += 1
            else:
                categories['other'] += 1
        
        stats['categories'] = categories
        return stats

# Global instance for convenience
_default_processor = None

def get_default_processor() -> ENVProcessor:
    """Get the default global processor instance"""
    global _default_processor
    if _default_processor is None:
        _default_processor = ENVProcessor()
    return _default_processor

# Convenience functions
def get_credential(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a credential using the default processor"""
    return get_default_processor().get_credential(key, default)

def get_all_credentials() -> Dict[str, str]:
    """Get all credentials using the default processor"""
    return get_default_processor().available_credentials
