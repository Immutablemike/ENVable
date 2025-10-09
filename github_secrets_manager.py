#!/usr/bin/env python3
"""
GitHub Secrets Integration for ENVThing 2.0
Automatically inserts secrets into GitHub repositories based on project names
"""

import os
import requests
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

logger = logging.getLogger(__name__)

class GitHubSecretsManager:
    """
    Manages GitHub repository secrets automatically
    Maps project names to repositories and syncs secrets
    """
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.getenv('ENVTHING_GITHUB_PAT')
        self.base_url = "https://api.github.com"
        self.owner = os.getenv('GITHUB_OWNER', 'your-username')  # Repository owner
        
        if not self.github_token:
            raise ValueError("GitHub PAT required: Set ENVTHING_GITHUB_PAT or pass github_token")
        
        self.headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        logger.info("GitHub Secrets Manager initialized")
    
    def process_project_secrets(self, project_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process project and sync secrets to corresponding GitHub repository
        
        Args:
            project_result: Complete project analysis from ENVThing core
            
        Returns:
            Dict containing sync results and repository information
        """
        project_name = project_result['project_name']
        logger.info(f"🔄 Processing GitHub secrets for project: {project_name}")
        
        # Map project name to repository
        repo_name = self._map_project_to_repo(project_name)
        
        if not repo_name:
            logger.warning(f"❌ No GitHub repository mapped for project: {project_name}")
            return {
                'project_name': project_name,
                'repo_name': None,
                'status': 'no_repo_mapped',
                'secrets_synced': 0,
                'errors': ['No repository mapping found']
            }
        
        # Get repository information
        repo_info = self._get_repository_info(repo_name)
        if not repo_info:
            logger.error(f"❌ Repository not found or no access: {repo_name}")
            return {
                'project_name': project_name,
                'repo_name': repo_name,
                'status': 'repo_not_found',
                'secrets_synced': 0,
                'errors': ['Repository not found or no access']
            }
        
        # Prepare secrets for sync
        secrets_to_sync = self._prepare_secrets_for_sync(project_result)
        
        # Sync secrets to repository
        sync_results = self._sync_secrets_to_repo(repo_name, secrets_to_sync)
        
        logger.info(f"✅ Synced {sync_results['synced_count']} secrets to {repo_name}")
        
        return {
            'project_name': project_name,
            'repo_name': repo_name,
            'repo_info': repo_info,
            'status': 'success',
            'secrets_synced': sync_results['synced_count'],
            'secrets_failed': sync_results['failed_count'],
            'sync_details': sync_results,
            'timestamp': datetime.now().isoformat()
        }
    
    def _map_project_to_repo(self, project_name: str) -> Optional[str]:
        """
        Map ENVThing project names to GitHub repository names
        
        Mapping logic:
        1. Direct match: project_name == repo_name
        2. ENV file pattern: "ProjectName_env" → "ProjectName"  
        3. Custom mappings for special cases
        """
        # Remove common suffixes
        clean_name = project_name.replace('_env', '').replace('_ENV', '')
        
        # Custom mappings for special cases
        # Add your project name mappings here
        project_mappings = {
            # Example mappings:
            # 'my_project_env': 'my-project',
            # 'ProjectName_env': 'ProjectName',
            # 'trading_bot': 'trading-bot-template'
        }
        
        # Check direct mapping first
        if project_name in project_mappings:
            return project_mappings[project_name]
        
        # Check cleaned name
        if clean_name in project_mappings:
            return project_mappings[clean_name]
        
        # Default: use cleaned project name
        return clean_name
    
    def _get_repository_info(self, repo_name: str) -> Optional[Dict]:
        """Get repository information and verify access"""
        try:
            url = f"{self.base_url}/repos/{self.owner}/{repo_name}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                repo_info = response.json()
                
                # CRITICAL SECURITY CHECK: Only allow private repositories
                if not repo_info.get('private', False):
                    logger.error(f"🚨 SECURITY BLOCK: Repository '{repo_name}' is PUBLIC - secrets injection DENIED")
                    logger.error(f"🚨 PUBLIC repositories expose secrets! Only PRIVATE repositories allowed.")
                    return None
                
                logger.info(f"✅ Repository '{repo_name}' is PRIVATE - secrets injection allowed")
                return repo_info
            elif response.status_code == 404:
                logger.warning(f"Repository not found: {repo_name}")
                return None
            else:
                logger.error(f"Failed to access repository {repo_name}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting repository info for {repo_name}: {e}")
            return None
    
    def _prepare_secrets_for_sync(self, project_result: Dict[str, Any]) -> Dict[str, str]:
        """
        Prepare secrets from project result for GitHub sync
        Only sync actual credential values, not configuration settings
        """
        secrets_to_sync = {}
        credentials = project_result.get('credentials', {})
        
        # Include resolved credentials (existing)
        if 'resolved' in credentials:
            for key, value in credentials['resolved'].items():
                if self._is_secret_not_setting(key, value):
                    secrets_to_sync[key] = str(value)
        
        # Include generated credentials (new)
        if 'generated' in credentials:
            for key, value in credentials['generated'].items():
                if self._is_secret_not_setting(key, value):
                    secrets_to_sync[key] = str(value)
        
        logger.info(f"Prepared {len(secrets_to_sync)} secrets for sync")
        return secrets_to_sync
    
    def _is_secret_not_setting(self, key: str, value: str) -> bool:
        """
        Determine if a variable is a secret (should be in GitHub Secrets)
        vs a setting (should be in code or environment)
        """
        # Skip if empty or placeholder
        if not value or value in ['', 'YOUR_VALUE_HERE', 'needed', 'required']:
            return False
        
        key_upper = key.upper()
        
        # Definitely secrets
        secret_indicators = [
            'API_KEY', 'SECRET', 'TOKEN', 'PASSWORD', 'PRIVATE_KEY',
            'AUTH', 'WEBHOOK_SECRET', 'JWT_SECRET', 'ENCRYPTION_KEY',
            'SESSION_SECRET', 'DATABASE_URL', 'MONGO_URI', 'REDIS_URL',
            'CONNECTION_STRING', 'DSN', 'CREDENTIALS', 'LICENSE_KEY'
        ]
        
        # Definitely NOT secrets (settings)
        setting_indicators = [
            'PORT', 'HOST', 'DEBUG', 'NODE_ENV', 'ENVIRONMENT', 'ENV',
            'TIMEOUT', 'LIMIT', 'VERSION', 'NAME', 'TITLE', 'DESCRIPTION',
            'REGION', 'ZONE', 'LOCALE', 'LANG', 'TZ', 'LOG_LEVEL'
        ]
        
        # Check if it's definitely a secret
        for indicator in secret_indicators:
            if indicator in key_upper:
                return True
        
        # Check if it's definitely a setting
        for indicator in setting_indicators:
            if indicator in key_upper:
                return False
        
        # Default: if it looks like a complex value, treat as secret
        if len(value) > 20 and any(c in value for c in ['sk-', 'pk_', 'https://', 'mongodb://', 'postgresql://']):
            return True
        
        return False
    
    def _sync_secrets_to_repo(self, repo_name: str, secrets: Dict[str, str]) -> Dict[str, Any]:
        """
        Sync secrets to GitHub repository
        Uses GitHub's repository secrets API with proper encryption
        """
        synced_count = 0
        failed_count = 0
        details = []
        
        # Get repository public key for encryption
        public_key_info = self._get_repo_public_key(repo_name)
        if not public_key_info:
            return {
                'synced_count': 0,
                'failed_count': len(secrets),
                'details': ['Failed to get repository public key'],
                'errors': ['Cannot encrypt secrets without public key']
            }
        
        # Sync each secret
        for secret_name, secret_value in secrets.items():
            try:
                encrypted_value = self._encrypt_secret(secret_value, public_key_info['key'])
                
                result = self._create_or_update_secret(
                    repo_name, 
                    secret_name, 
                    encrypted_value, 
                    public_key_info['key_id']
                )
                
                if result:
                    synced_count += 1
                    details.append(f"✅ {secret_name}")
                    logger.debug(f"Synced secret: {secret_name}")
                else:
                    failed_count += 1
                    details.append(f"❌ {secret_name}")
                    logger.warning(f"Failed to sync secret: {secret_name}")
                    
            except Exception as e:
                failed_count += 1
                details.append(f"❌ {secret_name}: {str(e)}")
                logger.error(f"Error syncing secret {secret_name}: {e}")
        
        return {
            'synced_count': synced_count,
            'failed_count': failed_count,
            'details': details,
            'total_secrets': len(secrets)
        }
    
    def _get_repo_public_key(self, repo_name: str) -> Optional[Dict]:
        """Get repository's public key for secret encryption"""
        try:
            url = f"{self.base_url}/repos/{self.owner}/{repo_name}/actions/secrets/public-key"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get public key for {repo_name}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting public key for {repo_name}: {e}")
            return None
    
    def _encrypt_secret(self, secret_value: str, public_key_base64: str) -> str:
        """Encrypt secret value using repository's public key (GitHub format)"""
        try:
            from nacl import encoding, public
            
            # Decode the public key (GitHub uses base64-encoded X25519 public keys)
            public_key_bytes = base64.b64decode(public_key_base64)
            public_key = public.PublicKey(public_key_bytes)
            
            # Create a sealed box and encrypt the secret
            sealed_box = public.SealedBox(public_key)
            encrypted = sealed_box.encrypt(secret_value.encode('utf-8'))
            
            # Return base64 encoded encrypted value
            return base64.b64encode(encrypted).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error encrypting secret: {e}")
            raise
    
    def _create_or_update_secret(self, repo_name: str, secret_name: str, encrypted_value: str, key_id: str) -> bool:
        """Create or update a repository secret"""
        try:
            url = f"{self.base_url}/repos/{self.owner}/{repo_name}/actions/secrets/{secret_name}"
            
            payload = {
                "encrypted_value": encrypted_value,
                "key_id": key_id
            }
            
            response = requests.put(url, headers=self.headers, json=payload)
            
            if response.status_code in [201, 204]:  # Created or Updated
                return True
            else:
                logger.error(f"Failed to create/update secret {secret_name}: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating/updating secret {secret_name}: {e}")
            return False
    
    def list_repository_secrets(self, repo_name: str) -> Dict[str, Any]:
        """List all secrets in a repository (for verification)"""
        try:
            url = f"{self.base_url}/repos/{self.owner}/{repo_name}/actions/secrets"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to list secrets for {repo_name}: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error listing secrets for {repo_name}: {e}")
            return {}
    
    def batch_sync_projects(self, project_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Batch sync multiple projects to their respective repositories
        """
        logger.info(f"🔄 Starting batch sync for {len(project_results)} projects")
        
        results = []
        total_synced = 0
        total_failed = 0
        
        for project_result in project_results:
            try:
                sync_result = self.process_project_secrets(project_result)
                results.append(sync_result)
                
                total_synced += sync_result.get('secrets_synced', 0)
                total_failed += sync_result.get('secrets_failed', 0)
                
            except Exception as e:
                error_result = {
                    'project_name': project_result.get('project_name', 'unknown'),
                    'status': 'error',
                    'error': str(e)
                }
                results.append(error_result)
                logger.error(f"Error processing project {project_result.get('project_name')}: {e}")
        
        logger.info(f"✅ Batch sync complete: {total_synced} secrets synced, {total_failed} failed")
        
        return {
            'total_projects': len(project_results),
            'successful_projects': len([r for r in results if r.get('status') == 'success']),
            'total_secrets_synced': total_synced,
            'total_secrets_failed': total_failed,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Test the GitHub Secrets Manager"""
    import sys
    
    # Test project result
    test_project = {
        'project_name': 'Copilot_Coder',
        'credentials': {
            'resolved': {
                'OPENAI_API_KEY': 'sk-test-key-123',
                'TELEGRAM_BOT_TOKEN': '123456:ABC-DEF',
                'PORT': '3000'  # This should be filtered out
            },
            'generated': {
                'JWT_SECRET': 'generated-jwt-secret-456',
                'DEBUG': 'true'  # This should be filtered out
            }
        }
    }
    
    try:
        # Initialize manager
        manager = GitHubSecretsManager()
        
        # Process single project
        result = manager.process_project_secrets(test_project)
        print("Sync Result:", json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
