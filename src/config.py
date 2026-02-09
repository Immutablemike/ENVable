"""
Configuration management for ENVable
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

# Base configuration
BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "sync_config.json"
ENV_EXAMPLE = BASE_DIR / ".env.example"

# Default configuration
DEFAULT_CONFIG = {
    "sync_interval": 300,  # 5 minutes
    "max_retries": 3,
    "timeout": 30,
    "encryption_enabled": True,
    "auto_backup": True,
    "validation_rules": {
        "required_env_vars": [],
        "forbidden_patterns": ["password", "secret", "key", "token"],
    },
}


class Config:
    """Configuration manager for ENVable"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or CONFIG_FILE
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        if self.config_path.exists():
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    file_config = json.load(f)
                # Merge with defaults
                merged = DEFAULT_CONFIG.copy()
                merged.update(file_config)
                return merged
            except (OSError, json.JSONDecodeError) as e:
                print(f"⚠️ Config load failed: {e}, using defaults")

        return DEFAULT_CONFIG.copy()

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config[key] = value

    def save(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)
        except OSError as e:
            print(f"⚠️ Config save failed: {e}")

    @property
    def github_token(self) -> Optional[str]:
        """Get GitHub token from environment"""
        return os.getenv("GITHUB_TOKEN")

    @property
    def sync_interval(self) -> int:
        """Get sync interval in seconds"""
        return self.get("sync_interval", 300)

    @property
    def max_retries(self) -> int:
        """Get maximum retry attempts"""
        return self.get("max_retries", 3)


# Global config instance
config = Config()
