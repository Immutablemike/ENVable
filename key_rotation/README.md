# ENVThing Key Rotation System

## 🔄 Modular Credential Rotation Protocol

### **Architecture Overview**
```
key_rotation/
├── rotation_scheduler.py      # Main orchestration engine
├── rotation_config.json       # Policies, schedules, providers
├── rotation_audit.log         # Compliance audit trail
└── provider_rotators/          # Modular provider integrations
    ├── __init__.py            # Base rotator classes
    ├── openai_rotator.py      # OpenAI API rotation
    ├── stripe_rotator.py      # Stripe key rotation
    ├── github_rotator.py      # GitHub PAT rotation
    └── custom_rotator.py      # Template for new providers
```

### **Rotation Policies**

#### **High Security (30 days)**
- `*_SECRET_KEY`, `*_PRIVATE_KEY`, `JWT_*`
- Manual approval required
- 7-day advance notification
- Emergency rotation capability

#### **Standard Security (90 days)**  
- `*_API_KEY`, `*_TOKEN`
- Automatic rotation
- 14-day advance notification
- Team notifications

#### **Low Security (180 days)**
- `*_PUBLIC_*`, `*_ANALYTICS_*`
- Automatic rotation
- 30-day advance notification
- Audit logging only

### **Technical Implementation - Three-Tier Approach**

#### **Tier 1: API-Based Rotation (Preferred) 🚀**

For providers with key management APIs:

```python
# OpenAI Example - Organization admin key rotates working keys
class OpenAIRotator(ProviderRotator):
    def rotate_credential(self, credential_name: str) -> Tuple[str, str]:
        # Use admin/organization key to create new key
        client = openai.OpenAI(api_key=self.admin_key)
        new_key = client.organization.api_keys.create(
            name=f"envable-automated-{datetime.now().strftime('%Y%m%d')}"
        )
        
        # Update all systems with new key
        self.update_env_file(credential_name, new_key.key)
        self.sync_to_github_secrets(credential_name, new_key.key)
        
        # Validate new key works
        if self.validate_key(new_key.key):
            # Revoke old key after validation
            client.organization.api_keys.delete(self.old_key_id)
            return (self.old_key_hash, self.hash_key(new_key.key))
        else:
            raise RotationError("New key validation failed")

# Stripe Example - Account admin manages API keys
class StripeRotator(ProviderRotator):
    def rotate_credential(self, credential_name: str) -> Tuple[str, str]:
        stripe.api_key = self.admin_key
        
        # Create new restricted key
        new_key = stripe.ApiKey.create(
            name=f"envable-{datetime.now().isoformat()}",
            permissions=['charges:write', 'customers:read']  # Scoped permissions
        )
        
        # Standard rotation flow
        return self.complete_rotation(credential_name, new_key.secret)
```

**Supported Providers (API-based):**
- OpenAI (Organization admin → Working keys)
- Stripe (Account admin → Restricted keys)  
- GitHub (PAT with repo scope → Repository secrets)
- AWS (IAM user with key rotation permissions)
- Azure (Service principal with key management)

#### **Tier 2: Browser Automation (Fallback) 🌐**

For providers without key rotation APIs:

```python
from playwright.sync_api import sync_playwright

class PlaywrightRotator(ProviderRotator):
    def rotate_credential(self, credential_name: str) -> Tuple[str, str]:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Login with stored credentials
            page.goto(self.provider_config.login_url)
            page.fill("[name=email]", self.encrypted_email)
            page.fill("[name=password]", self.encrypted_password)
            
            # Handle 2FA if configured
            if self.provider_config.has_2fa:
                totp_code = self.generate_totp()
                page.fill("[name=totp]", totp_code)
            
            page.click("button[type=submit]")
            page.wait_for_url("**/dashboard")
            
            # Navigate to API settings
            page.goto(self.provider_config.api_settings_url)
            
            # Generate new key
            page.click("button:has-text('Generate New Key')")
            page.wait_for_selector("[data-testid=new-api-key]")
            new_key = page.locator("[data-testid=new-api-key]").text_content()
            
            # Update systems
            self.update_env_file(credential_name, new_key)
            self.sync_to_github_secrets(credential_name, new_key)
            
            # Revoke old key
            page.click(f"button:has-text('Revoke'):near([data-key-id='{self.old_key_id}'])")
            page.wait_for_selector(".revoked-indicator")
            
            browser.close()
            return (self.old_key_hash, self.hash_key(new_key))

# Provider-specific browser automation
class DiscordRotator(PlaywrightRotator):
    provider_config = ProviderConfig(
        login_url="https://discord.com/login",
        api_settings_url="https://discord.com/developers/applications/{app_id}/bot",
        selectors={
            "regenerate_button": "button:has-text('Regenerate')",
            "token_display": "[data-testid=bot-token]",
            "confirm_button": "button:has-text('Yes, do it!')"
        }
    )
```

**Supported Providers (Browser-based):**
- Discord (No API for bot token rotation)
- Many SaaS tools with web-only key management
- Legacy systems without modern APIs

#### **Tier 3: Notification-Based (Manual Intervention) 📧**

For complex or high-security providers:

```python
class ManualRotator(ProviderRotator):
    def rotate_credential(self, credential_name: str) -> Tuple[str, str]:
        # Generate detailed rotation instructions
        notification = {
            "service": self.provider_name,
            "credential": credential_name,
            "last_rotated": self.get_last_rotation_date(),
            "urgency": "medium",
            "instructions": self.get_rotation_steps(),
            "compliance_deadline": self.calculate_compliance_deadline()
        }
        
        # Multi-channel notifications
        self.send_slack_notification(notification)
        self.send_email_alert(notification)
        self.create_github_issue(notification)
        self.schedule_calendar_reminder(notification)
        
        # Track manual rotation request
        return self.log_manual_rotation_request(credential_name)
    
    def verify_manual_rotation(self, credential_name: str, new_value: str):
        # Called when user provides new credential
        old_hash = self.get_current_hash(credential_name)
        self.update_env_file(credential_name, new_value)
        self.sync_to_github_secrets(credential_name, new_value)
        
        # Close tracking issue
        self.close_github_issue(f"Manual rotation: {credential_name}")
        return (old_hash, self.hash_key(new_value))
```

### **Provider Integration Interface**

Each provider rotator implements the base interface:

```python
from abc import ABC, abstractmethod
from typing import Tuple

class ProviderRotator(ABC):
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.admin_credentials = self.load_admin_credentials()
    
    @abstractmethod
    def rotate_credential(self, credential_name: str) -> Tuple[str, str]:
        """
        Rotate a credential and return (old_hash, new_hash) for audit.
        
        Must implement:
        1. Validate current credential
        2. Generate new credential (API/Browser/Manual)
        3. Update ENVThing .env file
        4. Sync to GitHub secrets
        5. Return audit hashes
        """
        pass
    
    def validate_key(self, key: str) -> bool:
        """Test that new key works before revoking old key"""
        pass
    
    def update_env_file(self, name: str, value: str):
        """Update local .env with new credential"""
        pass
    
    def sync_to_github_secrets(self, name: str, value: str):
        """Push new credential to GitHub secrets"""
        pass
```

### **Permission Model & Bootstrap Security**

#### **Admin Credential Requirements**

```yaml
# rotation_config.json - Admin permissions needed
providers:
  openai:
    rotation_method: "api"
    admin_permission: "organization:admin"
    bootstrap_credential: "OPENAI_ORG_ADMIN_KEY"
    scopes: ["api_key:create", "api_key:delete"]
    
  stripe:
    rotation_method: "api" 
    admin_permission: "account:admin"
    bootstrap_credential: "STRIPE_ADMIN_KEY"
    scopes: ["api_key:write"]
    
  discord:
    rotation_method: "browser"
    admin_permission: "application:owner"
    bootstrap_credentials: ["DISCORD_EMAIL", "DISCORD_PASSWORD", "DISCORD_2FA_SECRET"]
    
  banking_api:
    rotation_method: "manual"
    admin_permission: "human_verification_required"
    notification_channels: ["slack", "email", "github_issues"]
```

#### **Bootstrap Credential Security**

```python
# Secure storage of admin/master credentials
import keyring
from cryptography.fernet import Fernet

class SecureCredentialStore:
    def __init__(self):
        # Use system keychain for master key
        self.master_key = keyring.get_password("envable", "master_encryption_key")
        if not self.master_key:
            self.master_key = Fernet.generate_key()
            keyring.set_password("envable", "master_encryption_key", self.master_key)
        
        self.cipher = Fernet(self.master_key)
    
    def store_admin_credential(self, provider: str, credential_name: str, value: str):
        """Encrypt and store admin credentials securely"""
        encrypted_value = self.cipher.encrypt(value.encode())
        keyring.set_password(f"envable-admin-{provider}", credential_name, encrypted_value)
    
    def get_admin_credential(self, provider: str, credential_name: str) -> str:
        """Decrypt and retrieve admin credentials"""
        encrypted_value = keyring.get_password(f"envable-admin-{provider}", credential_name)
        return self.cipher.decrypt(encrypted_value).decode()
```

**Security Features:**
- Admin credentials stored in system keychain (macOS Keychain, Windows Credential Manager)
- Additional encryption layer with master key
- Master keys themselves rotate quarterly
- Hardware token support for ultra-high security
- Audit trail of all admin credential access

### **Compliance Features**

- **SOC2 Compliance**: Automated rotation schedules with audit trails
- **GDPR Compliance**: Secure key disposal and data retention policies  
- **PCI Compliance**: Payment credential rotation and monitoring
- **Audit Logging**: Complete rotation history with timestamps
- **Emergency Protocols**: Immediate rotation on compromise detection

### **Usage Examples**

```bash
# Check rotation schedule
python rotation_scheduler.py

# Emergency rotation
python -c "
from rotation_scheduler import RotationScheduler
scheduler = RotationScheduler()
scheduler.emergency_rotation('OPENAI_API_KEY', 'Suspected compromise')
"

# Generate compliance report
python -c "
from rotation_scheduler import RotationScheduler  
scheduler = RotationScheduler()
report = scheduler.generate_compliance_report('SOC2')
print(report)
"
```

### **Integration with ENVThing**

1. **Automatic Detection**: Rotation system reads from ENVThing `.env`
2. **Seamless Updates**: New keys automatically sync to GitHub secrets
3. **Zero Downtime**: Rolling rotation with validation checks
4. **Team Notifications**: Slack/email alerts for rotation events

### **Roadmap**

- **Phase 1**: Core rotation framework with major providers (OpenAI, Stripe, GitHub)
- **Phase 2**: Advanced scheduling, approval workflows, Slack integration
- **Phase 3**: ML-based compromise detection, automated rollback
- **Phase 4**: Enterprise features, multi-team approval chains, compliance dashboards

### **Security Benefits**

- **Reduced Attack Surface**: Regular credential refresh limits exposure window
- **Compromise Recovery**: Emergency rotation minimizes breach impact
- **Audit Compliance**: Complete rotation history for regulatory requirements
- **Team Awareness**: Proactive notifications prevent service disruptions
- **Automated Enforcement**: Policy-based rotation removes human error

---

*The ENVThing rotation system transforms credential security from reactive to proactive, ensuring your secrets stay secret.*