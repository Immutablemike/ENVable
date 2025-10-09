# 🚀 ENVable - Lightning-Fast Environment Variable Deployment

**Production developer's dream tool for AI-speed environment variable deployment across multiple repositories instantly.**

[![GitHub release](https://img.shields.io/github/release/Immutablemike/ENVable.svg)](https://github.com/Immutablemike/ENVable/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🎯 What ENVable Does

ENVable solves the pain of managing environment variables across multiple repositories by:

- **🔄 Auto-syncing** `.env` files to GitHub repository secrets
- **⚡ Lightning deployment** of environment variables across multiple projects  
- **🔒 Secure credential rotation** with automated scheduling
- **🎯 Smart pattern matching** to sync only secrets (not settings)
- **🚨 Security-first** - only works with private repositories

## ⚡ Quick Start

### 1. Installation

```bash
git clone https://github.com/Immutablemike/ENVable.git
cd ENVable
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy template and configure
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required configuration:
```bash
# GitHub Personal Access Token (with repo permissions)
ENVTHING_GITHUB_PAT=your_github_pat_here

# Your GitHub username
GITHUB_OWNER=your-github-username
```

### 3. Quick Test

```python
from env_processor import ENVProcessor
from github_secrets_manager import GitHubSecretsManager

# Load your environment
env = ENVProcessor()

# Initialize GitHub integration  
github = GitHubSecretsManager()

# Sync secrets to a repository
project_result = {
    'project_name': 'my-awesome-project',
    'credentials': {
        'resolved': {
            'DATABASE_URL': 'postgresql://localhost:5432/mydb',
            'API_KEY': 'your-secret-api-key'
        }
    }
}

result = github.process_project_secrets(project_result)
print(f"✅ Synced {result['secrets_synced']} secrets!")
```

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