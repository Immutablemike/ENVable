"""
Agent orchestration for ENVable deployment
"""

from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime

try:
    from .config import config
    from .env_processor import ENVProcessor
    from .github_secrets_manager import GitHubSecretsManager
    from .auto_sync import ENVSyncHandler
except ImportError:
    # Fallback for direct execution
    import config
    from env_processor import ENVProcessor
    from github_secrets_manager import GitHubSecretsManager
    from auto_sync import ENVSyncHandler
    config = config.config

logger = logging.getLogger(__name__)


class ENVAgent:
    """
    Intelligent agent for environment variable deployment and synchronization
    """
    
    def __init__(self):
        self.config = config
        self.processor = ENVProcessor()
        self.github_manager = GitHubSecretsManager()
        self.sync_handler = ENVSyncHandler()
        self.status = "initialized"
        self.last_sync = None
        
    async def initialize(self) -> bool:
        """Initialize all agent components"""
        try:
            logger.info("🤖 ENVAgent initializing...")
            
            # Validate configuration
            if not self.config.github_token:
                logger.warning("⚠️ No GitHub token found")
                return False
            
            # Initialize components
            self.processor.validate_environment()
            logger.info("✅ ENVProcessor ready")
            
            self.status = "ready"
            logger.info("🚀 ENVAgent ready for deployment!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Agent initialization failed: {e}")
            self.status = "error"
            return False
    
    async def deploy_environment(
        self, 
        repository: str,
        environment_vars: Optional[Dict[str, str]] = None
    ) -> bool:
        """Deploy environment variables to GitHub repository"""
        try:
            logger.info(f"🚀 Deploying environment to {repository}")
            
            # Use provided vars or load from processor
            env_vars = environment_vars or self.processor.available_credentials
            
            if not env_vars:
                logger.warning("⚠️ No environment variables to deploy")
                return False
            
            # Deploy to GitHub Secrets
            success = await self.github_manager.sync_secrets(
                repository=repository,
                secrets=env_vars
            )
            
            if success:
                self.last_sync = datetime.now()
                logger.info(f"✅ Environment deployed to {repository}")
                return True
            else:
                logger.error(f"❌ Deployment failed for {repository}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Deployment error: {e}")
            return False
    
    async def start_monitoring(self) -> None:
        """Start continuous monitoring and auto-sync"""
        try:
            logger.info("🔄 Starting environment monitoring...")
            
            while self.status == "ready":
                await asyncio.sleep(self.config.sync_interval)
                await self._check_and_sync()
                
        except asyncio.CancelledError:
            logger.info("🛑 Monitoring stopped")
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")
            self.status = "error"
    
    async def _check_and_sync(self) -> None:
        """Check for changes and sync if needed"""
        try:
            # Check for file changes
            if self.sync_handler.has_changes():
                logger.info("📝 Changes detected, triggering sync...")
                # Trigger sync for configured repositories
                # This would be implemented based on sync_config.json
                pass
                
        except Exception as e:
            logger.error(f"❌ Sync check failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "status": self.status,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "available_credentials": len(self.processor.available_credentials),
            "github_token_configured": bool(self.config.github_token),
            "sync_interval": self.config.sync_interval
        }
    
    async def health_check(self) -> bool:
        """Perform health check on all components"""
        try:
            # Check processor
            self.processor.validate_environment()
            
            # Check GitHub connection
            if not self.config.github_token:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False


# Global agent instance
agent = ENVAgent()


async def main():
    """Main entry point for agent execution"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize agent
        if await agent.initialize():
            logger.info("🤖 ENVAgent started successfully")
            
            # Start monitoring (runs indefinitely)
            await agent.start_monitoring()
        else:
            logger.error("❌ Agent initialization failed")
            
    except KeyboardInterrupt:
        logger.info("🛑 Agent stopped by user")
    except Exception as e:
        logger.error(f"❌ Agent error: {e}")


if __name__ == "__main__":
    asyncio.run(main())