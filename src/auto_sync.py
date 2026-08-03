#!/usr/bin/env python3
"""
Auto-Sync for ENVThing
======================

Simple file watcher that syncs .env changes to GitHub repo secrets.
KISS principle: Watch file → Sync to configured repos → Done.

Usage: python3 auto_sync.py
"""

import fnmatch
import json
import os
import threading
import time

from github_secrets_manager import GitHubSecretsManager
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from env_processor import ENVProcessor


class ENVSyncHandler(FileSystemEventHandler):
    def __init__(self, config_path: str = "sync_config.json"):
        self.config_path = config_path
        self.last_sync = 0
        self.sync_timer = None
        self.load_config()

        # Initialize processors
        self.env_processor = ENVProcessor()
        self.github_manager = GitHubSecretsManager(
            self.env_processor.get_credential("ENVTHING_GITHUB_PAT")
        )

        print("🔄 ENVThing Auto-Sync initialized")
        print(f"📁 Watching repos: {', '.join(self.config['repos'])}")
        print(f"🎯 Sync patterns: {', '.join(self.config['sync_patterns'])}")

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path) as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Default config if file doesn't exist
            self.config = {
                "repos": ["ENVThing"],
                "sync_patterns": ["*_API_KEY", "*_TOKEN", "*_SECRET"],
                "exclude_patterns": ["*PASSWORD*", "*_PAT"],
                "debounce_seconds": 3,
            }
            print("⚠️  Config not found, using defaults")

    def on_modified(self, event):
        """Handle .env file modifications"""
        if event.is_directory or not event.src_path.endswith(".env"):
            return

        print(f"📝 .env file changed: {event.src_path}")

        # Cancel existing timer
        if self.sync_timer:
            self.sync_timer.cancel()

        # Start new debounced sync
        self.sync_timer = threading.Timer(
            self.config["debounce_seconds"], self.sync_secrets
        )
        self.sync_timer.start()

    def should_sync_credential(self, key: str) -> bool:
        """Check if credential should be synced based on patterns"""
        # Check exclude patterns first
        for exclude_pattern in self.config["exclude_patterns"]:
            if fnmatch.fnmatch(key, exclude_pattern):
                return False

        # Check include patterns
        for sync_pattern in self.config["sync_patterns"]:
            if fnmatch.fnmatch(key, sync_pattern):
                return True

        return False

    def sync_secrets(self):
        """Sync filtered credentials to configured repos"""
        print("🚀 Starting credential sync...")

        # Get current credentials
        all_creds = self.env_processor.available_credentials

        # Filter credentials to sync
        creds_to_sync = {
            key: value
            for key, value in all_creds.items()
            if self.should_sync_credential(key)
        }

        if not creds_to_sync:
            print("📭 No credentials match sync patterns")
            return

        print(
            f"🎯 Syncing {len(creds_to_sync)} credentials: {list(creds_to_sync.keys())}"
        )

        # Sync to each configured repo
        for repo_name in self.config["repos"]:
            print(f"📤 Syncing to repo: {repo_name}")

            try:
                # Use GitHub CLI for simple, direct sync
                for key, value in creds_to_sync.items():
                    owner = os.getenv("GITHUB_OWNER", "your-username")
                    os.system(
                        f'gh secret set {key} --body "{value}" --repo {owner}/{repo_name}'
                    )

                print(f"✅ Synced {len(creds_to_sync)} secrets to {repo_name}")

            except Exception as e:
                print(f"❌ Error syncing to {repo_name}: {e}")

        print("🎉 Sync complete!")
        self.last_sync = time.time()


def main():
    """Main auto-sync function"""
    # Create sync handler
    handler = ENVSyncHandler()

    # Setup file watcher
    observer = Observer()
    observer.schedule(handler, path=".", recursive=False)

    # Start watching
    observer.start()
    print("👀 Watching .env for changes... (Ctrl+C to stop)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Auto-sync stopped")

    observer.join()


if __name__ == "__main__":
    main()
