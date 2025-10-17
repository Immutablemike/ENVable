# OpenAPI Schema Management System

🔧 **Comprehensive OpenAPI schema system for enum consistency and API standardization**

## Overview

The OpenAPI system provides a single source of truth for all data structures, enums, and API specifications across your credential management ecosystem. This public version demonstrates best practices for API schema validation and code generation.

## Key Features

- **Enum Consistency**: Standardized enums across all systems and APIs
- **Schema Validation**: Automatic validation of data structures
- **Type Generation**: Auto-generated Pydantic models and TypeScript types
- **API Documentation**: Interactive OpenAPI documentation
- **CI/CD Integration**: Validation hooks for continuous integration

## Architecture

```
OpenAPI/
├── schemas/
│   └── api-spec.yaml          # Main OpenAPI specification
├── components/
│   ├── credentials.yaml       # Credential management schemas
│   ├── services.yaml          # Service definitions and enums
│   ├── monitoring.yaml        # Monitoring schemas
│   └── notifications.yaml    # Alert and notification schemas
├── generated/
│   ├── pydantic_models.py    # Generated Pydantic models
│   ├── typescript_types.ts   # Generated TypeScript types
│   └── docs/                 # Generated documentation
├── validators/
│   ├── schema_validator.py   # Core validation utilities
│   ├── enum_checker.py       # Enum consistency checker
│   └── ci_validator.py       # CI/CD validation hooks
└── tools/
    ├── generator.py          # Code generation utilities
    ├── validator.py          # CLI validation tool
    └── sync_checker.py       # Cross-system consistency checker
```

## Standardized Enums

### Service Types
```yaml
ServiceType:
  type: string
  enum:
    - openai        # OpenAI API services
    - github        # GitHub and GitHub Actions  
    - stripe        # Payment processing
    - supabase      # Database and authentication
    - cloudflare    # CDN and storage
    - mongodb       # Database services
    - vercel        # Deployment platform
    - airtable      # Database and workflows
    - telegram      # Notifications and bots
```

### Credential Types
```yaml
CredentialType:
  type: string
  enum:
    - api_key       # Standard API keys
    - token         # Bearer tokens and PATs
    - url           # Service URLs and endpoints
    - secret        # Encrypted secrets
    - certificate   # SSL certificates
    - oauth_token   # OAuth access tokens
    - webhook_url   # Webhook endpoints
```

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r OpenAPI/requirements.txt
   ```

2. **Validate Schemas**:
   ```bash
   python OpenAPI/tools/validator.py validate
   ```

3. **Generate Models**:
   ```bash
   python OpenAPI/tools/generator.py --generate-all
   ```

4. **Check Enum Consistency**:
   ```bash
   python OpenAPI/tools/validator.py enum-check
   ```

## Usage Examples

### Schema Validation
```python
from OpenAPI.validators.schema_validator import SchemaValidator

validator = SchemaValidator()
report = validator.generate_validation_report()

if report['summary']['is_valid']:
    print("✅ All schemas are valid")
else:
    print(f"❌ Found {report['summary']['total_errors']} errors")
```

### Code Generation
```python
from OpenAPI.tools.generator import CodeGenerator

generator = CodeGenerator()
generator.generate_pydantic_models()
generator.generate_typescript_types()
generator.generate_documentation()
```

### Enum Consistency Checking
```python
from OpenAPI.validators.enum_checker import EnumConsistencyChecker

checker = EnumConsistencyChecker()
result = checker.validate_service_consistency()

if not result['is_valid']:
    for error in result['errors']:
        print(f"❌ {error}")
```

## CLI Tool

The included CLI tool provides comprehensive validation and generation capabilities:

```bash
# Full validation
python OpenAPI/tools/validator.py full-check

# Generate all artifacts
python OpenAPI/tools/validator.py generate --all

# Check specific enum consistency
python OpenAPI/tools/validator.py enum-check --fail-on-inconsistency
```

## CI/CD Integration

Add to your GitHub Actions workflow:

```yaml
- name: Validate OpenAPI Schemas
  run: |
    pip install -r OpenAPI/requirements.txt
    python OpenAPI/tools/validator.py full-check --fail-on-issues
    
- name: Generate Code Artifacts
  run: python OpenAPI/tools/validator.py generate --all
```

## Configuration

### Environment Variables
```bash
# Optional: Custom schema location
OPENAPI_SCHEMA_DIR=./custom/schemas

# Optional: Custom output directory  
OPENAPI_OUTPUT_DIR=./custom/generated
```

### Schema Validation Rules
- All enums must be consistently defined across components
- New service types require schema updates
- Breaking changes require version bumps
- All API operations must have complete schemas

## Benefits

- ✅ **Type Safety**: Compile-time validation of all data structures
- ✅ **Consistency**: Single source of truth for enums and schemas
- ✅ **Documentation**: Auto-generated, always up-to-date API docs
- ✅ **Validation**: Prevent runtime errors from schema mismatches
- ✅ **Integration**: Seamless integration with existing systems
- ✅ **Maintenance**: Easier refactoring with schema-driven development

## Example Integration

```python
# Using generated Pydantic models
from OpenAPI.generated.pydantic_models import (
    ServiceType, 
    CredentialType, 
    CredentialSchema
)

# Type-safe credential creation
credential = CredentialSchema(
    service=ServiceType.OPENAI,
    credential_type=CredentialType.API_KEY,
    name="OpenAI Production Key",
    value="sk-...",
    is_active=True
)

# Automatic validation
try:
    credential.model_validate(data)
except ValidationError as e:
    print(f"Invalid credential data: {e}")
```

## Development Workflow

1. **Update Schemas**: Modify YAML files in `schemas/` or `components/`
2. **Validate**: Run `validator.py validate` 
3. **Generate**: Run `generator.py --generate-all`
4. **Test**: Validate against existing code
5. **Commit**: Include generated files in version control

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Update schemas and run validation
4. Generate new artifacts
5. Submit a pull request

---

**🎯 Professional API schema management for scalable systems**