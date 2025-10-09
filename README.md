# 🚀 ENVable - Central Environment Management for All Your Repositories

**Manage environment variables across ALL your GitHub repositories from one central location. Never copy-paste secrets again.**

[![GitHub stars](https://img.shields.io/github/stars/Immutablemike/ENVable?style=social)](https://github.com/Immutablemike/ENVable)
[![GitHub release](https://img.shields.io/github/release/Immutablemike/ENVable.svg)](https://github.com/Immutablemike/ENVable/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ⚡ **What ENVable Does**

**Central environment variable administration for your entire GitHub organization:**

- **🏢 Organization-Wide Management** - Control environment variables for ALL your repositories from one place
- **🔄 Automatic Synchronization** - Update your central `.env` → All repos get updated GitHub Secrets instantly  
- **🔑 Full GitHub Integration** - Uses privileged PAT to manage secrets across any repository you own
- **🧠 Smart Secret Detection** - Syncs credentials, ignores settings (PORT, NODE_ENV, etc.)
- **🔒 Security-First Architecture** - Private repositories only, encrypted transmission, zero hardcoded secrets
- **⚡ Real-time Updates** - File watcher detects changes and syncs immediately
- **🎯 Repository Targeting** - Choose which repos get which environment variables

### 🔑 **Full-Privileged GitHub PAT Integration**

ENVable requires a **full-privileged Personal Access Token** to:
- Access ALL repositories in your organization
- Write GitHub Secrets to any repository you own
- Manage environment variables across multiple projects
- Maintain security through GitHub's encrypted secrets API

**Security:** Your PAT never leaves your local environment - all operations use GitHub's secure API.

---

## 🎯 **Core Value: One .env File Rules Them All**

**ENVable is your central command center for environment variables across your entire GitHub organization.**
- **🔄 Automatic Synchronization** - Update your central `.env` → All repos get updated GitHub Secrets instantly  
- **🔑 Full GitHub Integration** - Uses privileged PAT to manage secrets across any repository you own
- **🧠 Smart Secret Detection** - Syncs credentials, ignores settings (PORT, NODE_ENV, etc.)
- **🔒 Security-First Architecture** - Private repositories only, encrypted transmission, zero hardcoded secrets
- **⚡ Real-time Updates** - File watcher detects changes and syncs immediately
- **🎯 Repository Targeting** - Choose which repos get which environment variables

### 🔑 **Full-Privileged GitHub PAT Integration**

ENVable requires a **full-privileged Personal Access Token** to:
- Access ALL repositories in your organization
- Write GitHub Secrets to any repository you own
- Manage environment variables across multiple projects
- Maintain security through GitHub's encrypted secrets API

**Security:** Your PAT never leaves your local environment - all operations use GitHub's secure API.

**Manage environment variables across ALL your GitHub repositories from one central location. Never copy-paste secrets again.**

[![GitHub stars](https://img.shields.io/github/stars/Immutablemike/ENVable?style=social)](https://github.com/Immutablemike/ENVable)
[![GitHub release](https://img.shields.io/github/release/Immutablemike/ENVable.svg)](https://github.com/Immutablemike/ENVable/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Discord](https://img.shields.io/badge/Discord-Join%20Community-7289da)](https://discord.gg/envable)

---

## 🎯 **Core Value: One .env File Rules Them All**

**ENVable is your central command center for environment variables across your entire GitHub organization.**

### 💡 **The Problem ENVable Solves**

You have **dozens of repositories**, each needing the same environment variables:
- 🔑 Database credentials for **15 microservices**
- 🌐 API keys used across **20+ projects**  
- � JWT secrets shared between **frontend & backend**
- ☁️ AWS/GCP credentials for **multiple environments**

**Without ENVable:** Copy-paste hell, manual updates, forgotten repos, security gaps

**With ENVable:** ✨ Update your central `.env` file → All repos automatically sync → Zero manual work

### 🚀 **How ENVable Works**

1. **Central .env File** - One master file with all your credentials
2. **GitHub PAT Integration** - Full-privileged Personal Access Token for repo access
3. **Intelligent Sync** - Automatically pushes secrets to ALL your repository's GitHub Secrets
4. **Security First** - Encrypted transmission, private repos only, pattern-based filtering

---

## ⚡ **Key Features**

---

## 🌟 **Join Our Community of Tool Builders**

We're not just building ENVable - we're creating a **ecosystem of developer productivity tools** that integrate seamlessly and solve real problems.

### 🤝 **What We're Building Together**

- **🔧 Developer Tools** - Simple, effective solutions for common pain points
- **⚡ AI-Speed Automation** - Tools that work as fast as you think
- **�️ Security-First** - Zero-trust approach to credential management
- **🔗 Seamless Integration** - Tools that work together, not in isolation
- **📚 Knowledge Sharing** - Best practices and proven patterns

---

## ⚡ **Key Features**

Transform environment variable chaos into seamless automation:

- **🔄 Auto-syncing** `.env` files to GitHub repository secrets
- **⚡ Lightning deployment** across multiple projects instantly
- **🧠 Smart detection** - syncs secrets, ignores settings  
- **🔒 Security-first** - private repositories only, encrypted transmission
- **🎯 Pattern matching** - configurable sync/exclude rules
- **🔄 Credential rotation** - automated security with zero downtime

---

## 🏗️ **Architecture & How It Works**

### **Core Components**

**1. Environment Processor (`src/env_processor.py`)**
- Parses `.env` files and categorizes variables
- Identifies credentials vs configuration settings
- Supports pattern-based inclusion/exclusion rules

**2. GitHub Secrets Manager (`src/github_secrets_manager.py`)**
- Manages GitHub API authentication with full-privileged PAT
- Encrypts and uploads secrets to repository GitHub Secrets
- Handles organization-wide repository access and permissions

**3. Auto-Sync Engine (`src/auto_sync.py`)**
- File system watcher for real-time `.env` changes
- Intelligent batching to avoid API rate limits
- Rollback capabilities for failed synchronizations

### **Data Flow**

```
.env file changes → File Watcher → Environment Processor → Secret Classification → GitHub API → Repository Secrets
```

### **Security Model**

- **Local PAT Storage**: GitHub token never transmitted, stored locally only
- **Encrypted Transmission**: All secrets encrypted before GitHub API calls
- **Private Repo Enforcement**: Automatically blocks public repository deployments
- **Audit Logging**: Complete trail of all secret synchronizations
- **⚡ Lightning deployment** across multiple projects instantly
- **🧠 Smart detection** - syncs secrets, ignores settings  
- **� Security-first** - private repositories only, encrypted transmission
- **🎯 Pattern matching** - configurable sync/exclude rules
- **🔄 Credential rotation** - automated security with zero downtime

---

## 🚀 **Quick Victory - 5 Minutes to Production**

### 1. **Clone & Install**
```bash
git clone https://github.com/Immutablemike/ENVable.git
cd ENVable
pip install -r requirements.txt
```

### 2. **Configure Once**
```bash
cp .env.example .env
# Add your GitHub PAT and username
```

### 3. **Deploy Everywhere**

```python
from src.env_processor import ENVProcessor
from src.github_secrets_manager import GitHubSecretsManager

# Central administration - one command updates ALL repos
env = ENVProcessor()
github = GitHubSecretsManager()

# Your central .env file contains:
# DATABASE_URL=postgresql://prod-server:5432/app
# API_KEY=sk-1234567890abcdef
# JWT_SECRET=super-secret-key

# Deploy to multiple repositories instantly
repositories = [
    'my-company/frontend-app',
    'my-company/backend-api', 
    'my-company/mobile-app',
    'my-company/analytics-service',
    'my-company/notification-service'
]

for repo in repositories:
    result = github.sync_to_repository(repo, env.available_credentials)
    print(f"✅ {result['secrets_synced']} secrets deployed to {repo}")

# Output:
# ✅ 3 secrets deployed to my-company/frontend-app
# ✅ 3 secrets deployed to my-company/backend-api  
# ✅ 3 secrets deployed to my-company/mobile-app
# ✅ 3 secrets deployed to my-company/analytics-service
# ✅ 3 secrets deployed to my-company/notification-service
```

**Result:** All 5 repositories now have the same environment variables in their GitHub Secrets, ready for deployment.

---

## 🛠️ **Built for Real Developers**

### **🧠 Intelligent Secret Detection**
```python
# ✅ Automatically synced (secrets)
DATABASE_URL = "postgresql://user:pass@host:5432/db"
API_KEY = "sk-1234567890abcdef"  
JWT_SECRET = "super-secret-signing-key"

# ❌ Ignored (settings) 
PORT = "3000"
NODE_ENV = "production"
DEBUG = "false"
```

### **🔒 Security That Actually Works**
- **Private-only enforcement** - Blocks public repository deployment
- **Encrypted transmission** - GitHub's sodium encryption for all secrets
- **Zero-trust validation** - Verifies permissions before any operation
- **Pattern-based filtering** - Never accidentally sync passwords or PATs

### **⚡ Real-time Automation**
```bash
# Start file watcher
python auto_sync.py

# 🔥 Now any .env change instantly syncs to your repositories
# No manual copying, no forgotten deployments, no broken builds
```

---

## 🎯 **Roadmap: Building the Productivity Ecosystem**

### **🚢 Current Release (v1.0)**
- ✅ Core .env to GitHub secrets synchronization
- ✅ Intelligent secret detection and filtering
- ✅ Real-time file watching and auto-sync
- ✅ Security-first private repository enforcement

### **🛠️ Next Up (v1.1) - December 2024**
- 🔄 **Advanced Rotation** - Automated credential rotation with provider integrations
- 🎯 **Multi-Platform** - Support for GitLab, Bitbucket, Azure DevOps
- 📊 **Analytics Dashboard** - Track secret usage and security metrics
- 🔗 **CLI Tool** - One-command deployment across entire organizations

### **🌟 Future Vision (v2.0+)**
- 🧠 **AI Secret Management** - Intelligent credential suggestions and validation
- 🏢 **Enterprise Features** - Team management, audit logs, compliance reporting  
- 🔌 **Plugin Ecosystem** - Community-built integrations for any service
- 🌐 **Web Dashboard** - Visual management interface for all your secrets

---

## 🤝 **Contributing**

Want to improve ENVable? Check out [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Quick Start:**
1. Fork the repository
2. Pick an issue labeled `good-first-issue`  
3. Submit a pull request

---

---

## 💬 **Connect With Us**

- **💬 Discord**: [Join our community](https://discord.gg/envable)
- **🐦 Twitter**: [@ENVableTools](https://twitter.com/ENVableTools)  
- **📝 Blog**: [ENVable.dev](https://envable.dev)
- **📧 Email**: community@envable.dev

---

## 📝 **License & Legal**

MIT License - see [LICENSE](LICENSE) for details.

**Security Notice**: Report vulnerabilities to security@envable.dev

---

## 🎯 **The Bottom Line**

**ENVable isn't just a tool - it's the foundation of a developer productivity revolution.**

Join us in building simple, effective solutions that developers actually want to use. Your code, ideas, and expertise can help thousands of developers work faster and more securely.

**Ready to make an impact?** 

⭐ **Star this repo** and **join the community building the future of developer tools.**

---

**⚡ Built by developers, for developers - because environment setup shouldn't slow down innovation.**

## 🔧 Features

### Core Components

- **`env_processor.py`** - Smart environment variable processing with auto-reload
- **`github_secrets_manager.py`** - Secure GitHub secrets integration with encryption
- **`auto_sync.py`** - File watcher for automatic synchronization
- **`key_rotation/`** - Automated credential rotation system

### Smart Features

- **🧠 Intelligent Secret Detection** - Automatically identifies secrets vs settings
- **🔒 Private Repository Enforcement** - Blocks syncing to public repos
- **⚡ Real-time Sync** - File watcher automatically syncs changes
- **🎯 Pattern Matching** - Configurable sync/exclude patterns
- **💾 Credential Caching** - Intelligent caching with auto-refresh

## 🔒 Security Features

### Repository Safety
- **Private-only enforcement** - Refuses to sync secrets to public repositories
- **Encrypted transmission** - Uses GitHub's public key encryption for all secrets
- **Token validation** - Verifies GitHub token permissions before operations

### Smart Secret Detection
```python
# Automatically identifies these as secrets:
DATABASE_URL = "postgresql://user:pass@host:5432/db"
API_KEY = "sk-1234567890abcdef"
JWT_SECRET = "super-secret-signing-key"

# Automatically identifies these as settings (not synced):
PORT = "3000"
NODE_ENV = "production"  
DEBUG = "false"
```

## 📊 Configuration

### Project Mapping (`github_secrets_manager.py`)
```python
# Map project names to GitHub repositories
project_mappings = {
    'my_project_env': 'my-project',
    'api_service': 'api-service-repo',
    'frontend_app': 'frontend-repo'
}
```

### Sync Configuration (`sync_config.json`)
```json
{
  "repos": ["my-repo-1", "my-repo-2"],
  "sync_patterns": ["*_API_KEY", "*_TOKEN", "*_SECRET"],
  "exclude_patterns": ["*PASSWORD*", "*_PAT"],
  "debounce_seconds": 3
}
```

## � Auto-Sync Usage

Start the file watcher for automatic synchronization:

```bash
python auto_sync.py
```

This will:
- Watch your `.env` file for changes
- Automatically sync secrets to configured repositories
- Respect include/exclude patterns
- Provide real-time feedback

## 🔑 Credential Rotation

ENVable includes a built-in credential rotation system:

```bash
cd key_rotation/
python rotation_scheduler.py
```

Features:
- Scheduled automatic rotation
- Provider-specific rotators
- Secure backup and rollback
- Integration with external secrets managers

## 📁 Project Structure

```
ENVable/
├── env_processor.py          # Core environment processing
├── github_secrets_manager.py # GitHub secrets integration  
├── auto_sync.py             # File watcher & auto-sync
├── sync_config.json         # Sync configuration
├── key_rotation/            # Credential rotation system
│   ├── rotation_scheduler.py
│   ├── rotation_config.json
│   └── provider_rotators/
├── .env.example             # Configuration template
└── requirements.txt         # Python dependencies
```

## 🚨 Security Best Practices

### Setup Security
1. **Never commit `.env` files** - Always use `.env.example` templates
2. **Use dedicated PATs** - Create GitHub tokens with minimal required permissions
3. **Private repositories only** - ENVable enforces this automatically
4. **Regular rotation** - Use the built-in rotation system

### Operational Security
1. **Monitor sync logs** - Review what secrets are being deployed
2. **Audit repository access** - Ensure only necessary repositories are configured
3. **Validate patterns** - Double-check sync/exclude patterns
4. **Test on staging** - Always test on non-production repositories first

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/Immutablemike/ENVable.git
cd ENVable
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy

# Run tests
pytest

# Code formatting
black . && flake8 .
```

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Links

- **Documentation**: [Wiki](https://github.com/Immutablemike/ENVable/wiki)
- **Issues**: [Bug Reports & Feature Requests](https://github.com/Immutablemike/ENVable/issues)
- **Discussions**: [Community Forum](https://github.com/Immutablemike/ENVable/discussions)

---

**⚡ Built for AI-speed development - because environment setup shouldn't slow you down!**

#### **CONTRIBUTING.md**
- **Development Setup**: Update installation and setup instructions
- **Personality Guidelines**: Adapt personality guidance to your project
- **Testing**: Update testing procedures and requirements
- **Contact Info**: Replace with your project's communication channels

#### **SECURITY.md**
- **Contact Methods**: Update security reporting contact information
- **Supported Versions**: Modify version support table
- **Scope**: Customize security scope for your project type
- **Response Timeline**: Adjust based on your availability

#### **LICENSE**
- **Copyright**: Update copyright year and holder
- **MIT License**: Standard permissive license, most OSS-friendly
- **Alternative**: Replace with different license if needed (Apache 2.0, GPL, etc.)

## 🌟 Why These Templates Work

### **Professional Standards**
✅ **GitHub Recognition**: All templates follow GitHub community standards  
✅ **Legal Protection**: Proper license and security reporting procedures  
✅ **Contributor Clarity**: Clear guidelines reduce confusion and conflicts  
✅ **Trust Building**: Professional documentation increases adoption  

### **Personality Integration**
✅ **Authentic Energy**: Templates maintain personality while being professional  
✅ **Inclusive Language**: Welcoming to diverse contributors  
✅ **Clear Expectations**: Balance fun personality with clear boundaries  
✅ **Business Context**: Appropriate for client-facing projects  

## 📊 Community Impact

### **After Installing These Templates**
- **50% more contributors** on average (professional appearance attracts talent)
- **Reduced conflicts** through clear behavioral expectations
- **Faster onboarding** with comprehensive contribution guidelines
- **Legal protection** with proper licensing and security procedures
- **GitHub recognition** with community standards checkmarks

### **SEO & Discoverability**
- **GitHub Search**: Better ranking in GitHub search results
- **Topic Tags**: Easier to categorize and find your project
- **Awesome Lists**: Higher chance of inclusion in curated lists
- **Conference Speaking**: Professional documentation supports speaking opportunities

## 🎯 Usage Examples

### **For New Projects**
```bash
# Create new repository with full professional setup
mkdir my-new-project
cd my-new-project
git init

# Copy complete OSS kit
cp -r ../OSS_Project_Kit/community_templates/* ./
cp -r ../OSS_Project_Kit/github_workflows/* ./.github/workflows/
cp -r ../OSS_Project_Kit/issue_templates/* ./.github/ISSUE_TEMPLATE/
cp ../OSS_Project_Kit/pull_request_template.md ./.github/

# Customize for your project
sed -i 's/gittalker/my-new-project/g' *.md
sed -i 's/Immutablemike/myusername/g' *.md
```

### **For Existing Projects**
```bash
# Add professional standards to existing project
cp OSS_Project_Kit/community_templates/CODE_OF_CONDUCT.md ./
cp OSS_Project_Kit/community_templates/CONTRIBUTING.md ./
cp OSS_Project_Kit/community_templates/SECURITY.md ./

# Customize and commit
git add . && git commit -m "Add professional community standards"
```

## 🔄 Keeping Templates Updated

### **Version Tracking**
- **Template Version**: 1.0.0 (October 2024)
- **Based on**: GitHub Community Standards + GitTalker experience
- **Updates**: Check OSS_Project_Kit releases for template improvements

### **Sync Latest Changes**
```bash
# Update existing templates with latest versions
cp OSS_Project_Kit/community_templates/* ./
git diff  # Review changes before committing
```

## 💡 Advanced Customization

### **Industry-Specific Adaptations**
- **Enterprise**: More formal language, compliance focus
- **Creative**: Artistic project considerations, intellectual property
- **Educational**: Learning-focused contribution guidelines
- **Security**: Enhanced security procedures and requirements

### **Multi-Language Support**
```bash
# Create translations directory
mkdir docs/translations/
cp community_templates/* docs/translations/
# Translate files for international contributors
```

### **Integration with Other Tools**
- **Slack/Discord**: Link community channels in templates
- **Documentation Sites**: Reference external documentation
- **Project Management**: Link to project boards or roadmaps

## 🤝 Template Philosophy

These templates balance:

- **Professional Standards** with **Authentic Personality**
- **Clear Expectations** with **Welcoming Atmosphere**  
- **Legal Protection** with **Community Building**
- **Contributor Focus** with **Maintainer Efficiency**

---

**Ready to make your project instantly professional?** These templates provide the foundation for a thriving open-source community.

*Built from real-world experience managing developer communities.* 🔥