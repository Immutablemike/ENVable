"""
Basic tests for ENVable components
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_config_import():
    """Test that config module imports successfully"""
    try:
        import config
        assert hasattr(config, 'Config')
        assert hasattr(config, 'config')
        print("✅ Config module imports successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import config: {e}")


def test_agent_import():
    """Test that agent module imports successfully"""
    try:
        import agent
        assert hasattr(agent, 'ENVAgent')
        assert hasattr(agent, 'agent')
        print("✅ Agent module imports successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import agent: {e}")


def test_env_processor_import():
    """Test that env_processor module imports successfully"""
    try:
        from env_processor import ENVProcessor
        processor = ENVProcessor()
        assert processor is not None
        print("✅ ENVProcessor imports and instantiates successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import ENVProcessor: {e}")


def test_github_secrets_manager_import():
    """Test that github_secrets_manager module imports successfully"""
    try:
        from github_secrets_manager import GitHubSecretsManager
        manager = GitHubSecretsManager()
        assert manager is not None
        print("✅ GitHubSecretsManager imports and instantiates successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import GitHubSecretsManager: {e}")


def test_auto_sync_import():
    """Test that auto_sync module imports successfully"""
    try:
        from auto_sync import ENVSyncHandler
        handler = ENVSyncHandler()
        assert handler is not None
        print("✅ ENVSyncHandler imports and instantiates successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import ENVSyncHandler: {e}")


def test_package_import():
    """Test that the main package imports successfully"""
    try:
        import src
        assert hasattr(src, '__version__')
        print(f"✅ ENVable package v{src.__version__} imports successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import src package: {e}")


if __name__ == "__main__":
    # Run tests directly
    print("🧪 Running basic import tests...")
    test_config_import()
    test_agent_import()
    test_env_processor_import()
    test_github_secrets_manager_import()
    test_auto_sync_import()
    test_package_import()
    print("✅ All basic tests passed!")