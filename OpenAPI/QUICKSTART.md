# ENVable OpenAPI Quick Start Guide

🚀 **Ready to validate and generate code from your OpenAPI schemas!**

## Installation Complete ✅

The ENVable OpenAPI system has been successfully installed with:

- ✅ Complete OpenAPI 3.0.3 specification (`schemas/api-spec.yaml`)
- ✅ Modular component schemas (`components/`)
- ✅ Schema validation utilities (`validators/`)
- ✅ Code generation tools (`tools/`)
- ✅ Generated artifacts directory (`generated/`)

## Quick Commands

### 1. Validate Your Schemas
```bash
# Basic validation
python OpenAPI/validators/schema_validator.py

# Full validation report
python OpenAPI/tools/validator.py full-check

# Check enum consistency
python OpenAPI/validators/enum_checker.py
```

### 2. Generate Code Artifacts
```bash
# Generate Pydantic models
python OpenAPI/tools/generator.py --pydantic

# Generate TypeScript types  
python OpenAPI/tools/generator.py --typescript

# Generate HTML documentation
python OpenAPI/tools/generator.py --docs

# Generate everything
python OpenAPI/tools/generator.py --all
```

### 3. CLI Tool Usage
```bash
# Install CLI dependencies first
pip install click

# Use the CLI validator
python OpenAPI/tools/validator.py validate
python OpenAPI/tools/validator.py enum-check
python OpenAPI/tools/validator.py generate --all
python OpenAPI/tools/validator.py full-check
```

## Next Steps

1. **Test the system**:
   ```bash
   cd /Users/michaelsprimary/ENVable
   python OpenAPI/tools/validator.py full-check
   ```

2. **Generate initial artifacts**:
   ```bash
   python OpenAPI/tools/validator.py generate --all
   ```

3. **Customize schemas** in `OpenAPI/components/` for your specific needs

4. **Integrate with your codebase** using the generated Pydantic models

## Key Features

- 🎯 **Standardized Enums**: ServiceType, CredentialType, and more
- 🔍 **Comprehensive Validation**: Schema and consistency checking
- 🏗️ **Code Generation**: Pydantic models and TypeScript types
- 📚 **Auto Documentation**: Interactive API documentation
- 🔧 **CLI Tools**: Command-line interface for all operations

## Example Integration

```python
# Using generated Pydantic models (after running generator)
from OpenAPI.generated.pydantic_models import ServiceType, CredentialType

# Type-safe service references
service = ServiceType.OPENAI
cred_type = CredentialType.API_KEY
```

🎉 **Your OpenAPI system is ready to ensure enum consistency across your entire ENVable ecosystem!**