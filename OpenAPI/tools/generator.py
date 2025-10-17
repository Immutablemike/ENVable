"""
ENVable OpenAPI Code Generator

Generates Pydantic models, TypeScript types, and documentation from OpenAPI specs.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CodeGenerator:
    """OpenAPI code generation utilities"""
    
    def __init__(self, schema_dir: Optional[str] = None, output_dir: Optional[str] = None):
        """Initialize generator with directories"""
        if schema_dir:
            self.schema_dir = Path(schema_dir)
        else:
            self.schema_dir = Path(__file__).parent.parent / "schemas"
        
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(__file__).parent.parent / "generated"
        
        self.components_dir = Path(__file__).parent.parent / "components"
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def load_schema(self, schema_file: str = "api-spec.yaml") -> Dict[str, Any]:
        """Load OpenAPI schema"""
        schema_path = self.schema_dir / schema_file
        
        with open(schema_path, 'r') as f:
            return yaml.safe_load(f)
    
    def load_components(self) -> Dict[str, Any]:
        """Load all component schemas"""
        components = {}
        
        component_files = [
            "services.yaml",
            "credentials.yaml",
            "monitoring.yaml", 
            "notifications.yaml"
        ]
        
        for file in component_files:
            file_path = self.components_dir / file
            if file_path.exists():
                with open(file_path, 'r') as f:
                    component_data = yaml.safe_load(f)
                    components.update(component_data)
        
        return components
    
    def generate_pydantic_models(self) -> str:
        """Generate Pydantic models from OpenAPI schema"""
        schema = self.load_schema()
        components = self.load_components()
        
        # Start building the Python file
        lines = [
            '"""',
            'Generated Pydantic models from ENVable OpenAPI specification',
            '',
            'Auto-generated on: ' + datetime.now().isoformat(),
            'Do not edit manually - regenerate using CodeGenerator',
            '"""',
            '',
            'from typing import Optional, List, Dict, Any, Union',
            'from datetime import datetime',
            'from enum import Enum',
            'from pydantic import BaseModel, Field, EmailStr, HttpUrl',
            'from uuid import UUID',
            '',
            ''
        ]
        
        # Generate enums first
        enums_generated = set()
        
        # ServiceType enum
        if "ServiceType" in components and "enum" in components["ServiceType"]:
            lines.extend([
                'class ServiceType(str, Enum):',
                '    """Supported service types for credential management"""',
                ''
            ])
            
            for service in components["ServiceType"]["enum"]:
                service_upper = service.upper()
                lines.append(f'    {service_upper} = "{service}"')
            
            lines.extend(['', ''])
            enums_generated.add("ServiceType")
        
        # CredentialType enum
        if "CredentialType" in components and "enum" in components["CredentialType"]:
            lines.extend([
                'class CredentialType(str, Enum):',
                '    """Types of credentials that can be stored"""',
                ''
            ])
            
            for cred_type in components["CredentialType"]["enum"]:
                cred_upper = cred_type.upper()
                lines.append(f'    {cred_upper} = "{cred_type}"')
            
            lines.extend(['', ''])
            enums_generated.add("CredentialType")
        
        # Generate status enums from monitoring
        if "DependencyStatus" in components:
            dep_status = components["DependencyStatus"]
            if "properties" in dep_status and "status" in dep_status["properties"]:
                status_prop = dep_status["properties"]["status"]
                if "enum" in status_prop:
                    lines.extend([
                        'class HealthStatus(str, Enum):',
                        '    """Health status enumeration"""',
                        ''
                    ])
                    
                    for status in status_prop["enum"]:
                        status_upper = status.upper()
                        lines.append(f'    {status_upper} = "{status}"')
                    
                    lines.extend(['', ''])
                    enums_generated.add("HealthStatus")
        
        # Generate Pydantic models
        if "components" in schema and "schemas" in schema["components"]:
            schemas = schema["components"]["schemas"]
            
            for schema_name, schema_def in schemas.items():
                if schema_name in enums_generated:
                    continue
                
                lines.extend([
                    f'class {schema_name}(BaseModel):',
                    f'    """Generated model for {schema_name}"""',
                    ''
                ])
                
                if "properties" in schema_def:
                    required_fields = schema_def.get("required", [])
                    
                    for prop_name, prop_def in schema_def["properties"].items():
                        field_type = self._get_python_type(prop_def)
                        is_optional = prop_name not in required_fields
                        
                        if is_optional:
                            field_type = f"Optional[{field_type}]"
                        
                        # Add field with description
                        description = prop_def.get("description", "")
                        if description:
                            field_def = f'Field(description="{description}")'
                        else:
                            field_def = "Field()"
                        
                        if is_optional:
                            field_def = f"Field(None, description=\"{description}\")"
                        
                        lines.append(f'    {prop_name}: {field_type} = {field_def}')
                    
                    lines.extend(['', ''])
                else:
                    lines.extend(['    pass', '', ''])
        
        # Add component models
        for comp_name, comp_def in components.items():
            if comp_name in enums_generated:
                continue
            
            if isinstance(comp_def, dict) and "type" in comp_def and comp_def["type"] == "object":
                lines.extend([
                    f'class {comp_name}(BaseModel):',
                    f'    """Generated component model for {comp_name}"""',
                    ''
                ])
                
                if "properties" in comp_def:
                    required_fields = comp_def.get("required", [])
                    
                    for prop_name, prop_def in comp_def["properties"].items():
                        field_type = self._get_python_type(prop_def)
                        is_optional = prop_name not in required_fields
                        
                        if is_optional:
                            field_type = f"Optional[{field_type}]"
                        
                        description = prop_def.get("description", "")
                        if is_optional:
                            field_def = f'Field(None, description="{description}")'
                        else:
                            field_def = f'Field(description="{description}")'
                        
                        lines.append(f'    {prop_name}: {field_type} = {field_def}')
                    
                    lines.extend(['', ''])
                else:
                    lines.extend(['    pass', '', ''])
        
        # Write to file
        output_file = self.output_dir / "pydantic_models.py"
        content = '\n'.join(lines)
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        return str(output_file)
    
    def generate_typescript_types(self) -> str:
        """Generate TypeScript type definitions"""
        schema = self.load_schema()
        components = self.load_components()
        
        lines = [
            '/**',
            ' * Generated TypeScript types from ENVable OpenAPI specification',
            ' *',
            ' * Auto-generated on: ' + datetime.now().isoformat(),
            ' * Do not edit manually - regenerate using CodeGenerator',
            ' */',
            '',
            ''
        ]
        
        # Generate enums
        if "ServiceType" in components and "enum" in components["ServiceType"]:
            lines.extend([
                'export enum ServiceType {',
            ])
            
            services = components["ServiceType"]["enum"]
            for i, service in enumerate(services):
                service_upper = service.upper()
                comma = ',' if i < len(services) - 1 else ''
                lines.append(f'  {service_upper} = "{service}"{comma}')
            
            lines.extend(['}', ''])
        
        if "CredentialType" in components and "enum" in components["CredentialType"]:
            lines.extend([
                'export enum CredentialType {',
            ])
            
            cred_types = components["CredentialType"]["enum"]
            for i, cred_type in enumerate(cred_types):
                cred_upper = cred_type.upper()
                comma = ',' if i < len(cred_types) - 1 else ''
                lines.append(f'  {cred_upper} = "{cred_type}"{comma}')
            
            lines.extend(['}', ''])
        
        # Generate interfaces
        if "components" in schema and "schemas" in schema["components"]:
            schemas = schema["components"]["schemas"]
            
            for schema_name, schema_def in schemas.items():
                # Skip enums
                if "enum" in schema_def:
                    continue
                
                lines.extend([
                    f'export interface {schema_name} {{',
                ])
                
                if "properties" in schema_def:
                    required_fields = schema_def.get("required", [])
                    
                    for prop_name, prop_def in schema_def["properties"].items():
                        ts_type = self._get_typescript_type(prop_def)
                        is_optional = prop_name not in required_fields
                        
                        optional_marker = '?' if is_optional else ''
                        description = prop_def.get("description", "")
                        
                        if description:
                            lines.append(f'  /** {description} */')
                        
                        lines.append(f'  {prop_name}{optional_marker}: {ts_type};')
                
                lines.extend(['}', ''])
        
        # Write to file
        output_file = self.output_dir / "typescript_types.ts"
        content = '\n'.join(lines)
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        return str(output_file)
    
    def generate_documentation(self) -> str:
        """Generate HTML documentation"""
        schema = self.load_schema()
        
        # Simple HTML documentation
        html_lines = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'    <title>{schema.get("info", {}).get("title", "API Documentation")}</title>',
            '    <style>',
            '        body { font-family: Arial, sans-serif; margin: 40px; }',
            '        .endpoint { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }',
            '        .method { font-weight: bold; padding: 4px 8px; margin-right: 10px; }',
            '        .get { background: #61affe; color: white; }',
            '        .post { background: #49cc90; color: white; }',
            '        .put { background: #fca130; color: white; }',
            '        .delete { background: #f93e3e; color: white; }',
            '    </style>',
            '</head>',
            '<body>',
            f'    <h1>{schema.get("info", {}).get("title", "API Documentation")}</h1>',
            f'    <p>{schema.get("info", {}).get("description", "")}</p>',
            ''
        ]
        
        # Add endpoints
        if "paths" in schema:
            html_lines.append('    <h2>Endpoints</h2>')
            
            for path, methods in schema["paths"].items():
                for method, operation in methods.items():
                    if method.lower() in ["get", "post", "put", "delete", "patch"]:
                        summary = operation.get("summary", "")
                        description = operation.get("description", "")
                        
                        html_lines.extend([
                            '    <div class="endpoint">',
                            f'        <span class="method {method.lower()}">{method.upper()}</span>',
                            f'        <code>{path}</code>',
                            f'        <h3>{summary}</h3>',
                            f'        <p>{description}</p>',
                            '    </div>',
                        ])
        
        html_lines.extend([
            '</body>',
            '</html>'
        ])
        
        # Write to file
        docs_dir = self.output_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        output_file = docs_dir / "index.html"
        content = '\n'.join(html_lines)
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        return str(output_file)
    
    def _get_python_type(self, prop_def: Dict[str, Any]) -> str:
        """Convert OpenAPI property to Python type"""
        prop_type = prop_def.get("type", "Any")
        prop_format = prop_def.get("format", "")
        
        if prop_type == "string":
            if prop_format == "email":
                return "EmailStr"
            elif prop_format == "uri":
                return "HttpUrl"
            elif prop_format == "date-time":
                return "datetime"
            elif prop_format == "uuid":
                return "UUID"
            else:
                return "str"
        elif prop_type == "integer":
            return "int"
        elif prop_type == "number":
            return "float"
        elif prop_type == "boolean":
            return "bool"
        elif prop_type == "array":
            items = prop_def.get("items", {})
            item_type = self._get_python_type(items)
            return f"List[{item_type}]"
        elif prop_type == "object":
            return "Dict[str, Any]"
        else:
            return "Any"
    
    def _get_typescript_type(self, prop_def: Dict[str, Any]) -> str:
        """Convert OpenAPI property to TypeScript type"""
        prop_type = prop_def.get("type", "any")
        prop_format = prop_def.get("format", "")
        
        if prop_type == "string":
            if prop_format == "date-time":
                return "Date"
            else:
                return "string"
        elif prop_type == "integer" or prop_type == "number":
            return "number"
        elif prop_type == "boolean":
            return "boolean"
        elif prop_type == "array":
            items = prop_def.get("items", {})
            item_type = self._get_typescript_type(items)
            return f"{item_type}[]"
        elif prop_type == "object":
            return "Record<string, any>"
        else:
            return "any"
    
    def generate_all(self) -> Dict[str, str]:
        """Generate all artifacts"""
        results = {}
        
        try:
            results["pydantic_models"] = self.generate_pydantic_models()
            logger.info(f"Generated Pydantic models: {results['pydantic_models']}")
        except Exception as e:
            logger.error(f"Error generating Pydantic models: {e}")
            results["pydantic_models"] = f"Error: {e}"
        
        try:
            results["typescript_types"] = self.generate_typescript_types()
            logger.info(f"Generated TypeScript types: {results['typescript_types']}")
        except Exception as e:
            logger.error(f"Error generating TypeScript types: {e}")
            results["typescript_types"] = f"Error: {e}"
        
        try:
            results["documentation"] = self.generate_documentation()
            logger.info(f"Generated documentation: {results['documentation']}")
        except Exception as e:
            logger.error(f"Error generating documentation: {e}")
            results["documentation"] = f"Error: {e}"
        
        return results


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate code from OpenAPI specs")
    parser.add_argument("--pydantic", action="store_true", help="Generate Pydantic models")
    parser.add_argument("--typescript", action="store_true", help="Generate TypeScript types")
    parser.add_argument("--docs", action="store_true", help="Generate documentation")
    parser.add_argument("--all", action="store_true", help="Generate all artifacts")
    
    args = parser.parse_args()
    
    generator = CodeGenerator()
    
    if args.all or not any([args.pydantic, args.typescript, args.docs]):
        results = generator.generate_all()
        print(json.dumps(results, indent=2))
    else:
        results = {}
        
        if args.pydantic:
            results["pydantic"] = generator.generate_pydantic_models()
        
        if args.typescript:
            results["typescript"] = generator.generate_typescript_types()
        
        if args.docs:
            results["docs"] = generator.generate_documentation()
        
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()