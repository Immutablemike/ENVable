# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Advanced credential rotation system
- Multi-platform support (GitLab, Bitbucket, Azure DevOps)
- Analytics dashboard for secret usage tracking
- CLI tool for organization-wide deployment

## [1.0.0] - 2024-10-08

### Added
- Initial public release of ENVable
- Core .env to GitHub secrets synchronization
- Intelligent secret vs setting detection
- Private repository enforcement for security
- Real-time file watching and auto-sync
- Pattern-based sync/exclude configuration
- Basic credential rotation framework
- Comprehensive documentation and community standards
- GitHub Actions automation workflows
- Professional issue and PR templates

### Security
- Complete removal of any committed secrets from git history
- Private-only repository enforcement
- Encrypted transmission using GitHub's sodium encryption
- Token validation and permission verification

## [0.1.0] - 2024-10-01

### Added
- Initial development version
- Basic environment variable processing
- GitHub secrets manager core functionality
- Auto-sync file watcher implementation

---

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## Security

For security vulnerabilities, please see [SECURITY.md](SECURITY.md) for our responsible disclosure policy.