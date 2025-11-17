"""
ENVable - Lightning-fast environment variable deployment tool
"""

__version__ = "1.0.0"
__author__ = "ImmutableMike"
__description__ = "Lightning-fast environment variable deployment with GitHub secrets"

from .auto_sync import ENVSyncHandler
from .env_processor import ENVProcessor
from .github_secrets_manager import GitHubSecretsManager

__all__ = ["ENVProcessor", "GitHubSecretsManager", "ENVSyncHandler"]
