"""
ENVable OpenAPI Schema Validator

Public-safe schema validation utilities for OpenAPI specifications.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import jsonschema
from jsonschema import validate, ValidationError
import logging

logger = logging.getLogger(__name__)


class SchemaValidator:
    """OpenAPI schema validation utilities"""
    
    def __init__(self, schema_dir: Optional[str] = None):
        """Initialize validator with schema directory"""
        if schema_dir:
            self.schema_dir = Path(schema_dir)
        else:
            self.schema_dir = Path(__file__).parent.parent / "schemas"
        
        self.components_dir = Path(__file__).parent.parent / "components"
        
    def load_schema(self, schema_file: str) -> Dict[str, Any]:
        """Load OpenAPI schema from YAML file"""
        schema_path = self.schema_dir / schema_file
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
            
        with open(schema_path, 'r') as f:
            return yaml.safe_load(f)
    
    def load_component(self, component_file: str) -> Dict[str, Any]:
        """Load component schema from YAML file"""
        component_path = self.components_dir / component_file
        
        if not component_path.exists():
            raise FileNotFoundError(f"Component file not found: {component_path}")
            
        with open(component_path, 'r') as f:
            return yaml.safe_load(f)
    
    def validate_openapi_spec(self, spec_file: str = "api-spec.yaml") -> Dict[str, Any]:
        """Validate OpenAPI specification"""
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "summary": {}
        }
        
        try:
            # Load main specification
            spec = self.load_schema(spec_file)
            
            # Basic OpenAPI structure validation
            required_fields = ["openapi", "info", "paths"]
            for field in required_fields:
                if field not in spec:
                    result["errors"].append(f"Missing required field: {field}")
                    result["is_valid"] = False
            
            # Validate OpenAPI version
            if "openapi" in spec:
                version = spec["openapi"]
                if not version.startswith("3.0"):
                    result["warnings"].append(f"OpenAPI version {version} - recommend 3.0.x")
            
            # Validate info section
            if "info" in spec:
                info = spec["info"]
                required_info = ["title", "version"]
                for field in required_info:
                    if field not in info:
                        result["errors"].append(f"Missing info.{field}")
                        result["is_valid"] = False
            
            # Validate paths
            if "paths" in spec:
                paths = spec["paths"]
                if not paths:
                    result["warnings"].append("No paths defined in specification")
                else:
                    for path, methods in paths.items():
                        if not isinstance(methods, dict):
                            result["errors"].append(f"Invalid path definition: {path}")
                            result["is_valid"] = False
                            continue
                            
                        for method, operation in methods.items():
                            if method.lower() in ["get", "post", "put", "delete", "patch", "options", "head"]:
                                if "operationId" not in operation:
                                    result["warnings"].append(f"Missing operationId for {method.upper()} {path}")
                                if "summary" not in operation:
                                    result["warnings"].append(f"Missing summary for {method.upper()} {path}")
            
            # Validate components if present
            if "components" in spec and "schemas" in spec["components"]:
                schemas = spec["components"]["schemas"]
                for schema_name, schema_def in schemas.items():
                    if not isinstance(schema_def, dict):
                        result["errors"].append(f"Invalid schema definition: {schema_name}")
                        result["is_valid"] = False
            
            # Generate summary
            result["summary"] = {
                "total_paths": len(spec.get("paths", {})),
                "total_schemas": len(spec.get("components", {}).get("schemas", {})),
                "total_errors": len(result["errors"]),
                "total_warnings": len(result["warnings"])
            }
            
        except yaml.YAMLError as e:
            result["errors"].append(f"YAML parsing error: {str(e)}")
            result["is_valid"] = False
        except Exception as e:
            result["errors"].append(f"Validation error: {str(e)}")
            result["is_valid"] = False
        
        return result
    
    def validate_enum_consistency(self) -> Dict[str, Any]:
        """Validate enum consistency across components"""
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "enums_found": {}
        }
        
        try:
            # Load all component files
            component_files = [
                "services.yaml",
                "credentials.yaml", 
                "monitoring.yaml",
                "notifications.yaml"
            ]
            
            enums = {}
            
            for file in component_files:
                try:
                    component = self.load_component(file)
                    self._extract_enums(component, enums, file)
                except FileNotFoundError:
                    result["warnings"].append(f"Component file not found: {file}")
                    continue
            
            # Check for enum conflicts
            for enum_name, definitions in enums.items():
                if len(definitions) > 1:
                    # Check if all definitions are identical
                    first_def = definitions[0]
                    for i, other_def in enumerate(definitions[1:], 1):
                        if first_def["values"] != other_def["values"]:
                            result["errors"].append(
                                f"Enum {enum_name} has conflicting definitions in "
                                f"{first_def['file']} vs {other_def['file']}"
                            )
                            result["is_valid"] = False
            
            result["enums_found"] = {
                name: defs[0]["values"] for name, defs in enums.items()
            }
            
        except Exception as e:
            result["errors"].append(f"Enum validation error: {str(e)}")
            result["is_valid"] = False
        
        return result
    
    def _extract_enums(self, data: Any, enums: Dict, file: str, path: str = ""):
        """Recursively extract enum definitions from schema data"""
        if isinstance(data, dict):
            # Check if this is an enum definition
            if "enum" in data and "type" in data:
                enum_name = path.split(".")[-1] if path else "unknown"
                if enum_name not in enums:
                    enums[enum_name] = []
                enums[enum_name].append({
                    "file": file,
                    "path": path,
                    "values": data["enum"]
                })
            
            # Recurse through dictionary
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key
                self._extract_enums(value, enums, file, new_path)
                
        elif isinstance(data, list):
            # Recurse through list items
            for i, item in enumerate(data):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                self._extract_enums(item, enums, file, new_path)
    
    def validate_component_references(self) -> Dict[str, Any]:
        """Validate component references in main spec"""
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "references": []
        }
        
        try:
            # Load main spec
            spec = self.load_schema("api-spec.yaml")
            
            # Find all $ref values
            refs = []
            self._find_references(spec, refs)
            
            # Check component references
            for ref in refs:
                if ref.startswith("#/components/"):
                    # Internal reference - should exist in spec
                    ref_path = ref[2:].split("/")  # Remove "#/" prefix
                    current = spec
                    
                    for part in ref_path:
                        if isinstance(current, dict) and part in current:
                            current = current[part]
                        else:
                            result["errors"].append(f"Broken reference: {ref}")
                            result["is_valid"] = False
                            break
                
                elif ref.startswith("./"):
                    # External component reference
                    file_ref = ref[2:]  # Remove "./" prefix
                    if "#/" in file_ref:
                        file_path, schema_path = file_ref.split("#/", 1)
                    else:
                        file_path = file_ref
                        schema_path = None
                    
                    # Check if component file exists
                    component_path = self.components_dir / file_path
                    if not component_path.exists():
                        result["errors"].append(f"Component file not found: {file_path}")
                        result["is_valid"] = False
                    elif schema_path:
                        # Validate schema path within component
                        try:
                            component = self.load_component(file_path)
                            path_parts = schema_path.split("/")
                            current = component
                            
                            for part in path_parts:
                                if isinstance(current, dict) and part in current:
                                    current = current[part]
                                else:
                                    result["errors"].append(
                                        f"Schema not found in {file_path}: {schema_path}"
                                    )
                                    result["is_valid"] = False
                                    break
                        except Exception as e:
                            result["errors"].append(
                                f"Error validating reference {ref}: {str(e)}"
                            )
                            result["is_valid"] = False
            
            result["references"] = refs
            
        except Exception as e:
            result["errors"].append(f"Reference validation error: {str(e)}")
            result["is_valid"] = False
        
        return result
    
    def _find_references(self, data: Any, refs: List[str]):
        """Recursively find all $ref values in schema data"""
        if isinstance(data, dict):
            if "$ref" in data:
                refs.append(data["$ref"])
            
            for value in data.values():
                self._find_references(value, refs)
                
        elif isinstance(data, list):
            for item in data:
                self._find_references(item, refs)
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        report = {
            "timestamp": "2024-01-20T15:30:00Z",  # Placeholder timestamp
            "summary": {
                "is_valid": True,
                "total_errors": 0,
                "total_warnings": 0
            },
            "spec_validation": {},
            "enum_validation": {},
            "reference_validation": {}
        }
        
        # Validate main specification
        spec_result = self.validate_openapi_spec()
        report["spec_validation"] = spec_result
        
        # Validate enum consistency
        enum_result = self.validate_enum_consistency()
        report["enum_validation"] = enum_result
        
        # Validate component references
        ref_result = self.validate_component_references()
        report["reference_validation"] = ref_result
        
        # Generate overall summary
        all_results = [spec_result, enum_result, ref_result]
        
        total_errors = sum(len(r.get("errors", [])) for r in all_results)
        total_warnings = sum(len(r.get("warnings", [])) for r in all_results)
        is_valid = all(r.get("is_valid", False) for r in all_results)
        
        report["summary"] = {
            "is_valid": is_valid,
            "total_errors": total_errors,
            "total_warnings": total_warnings
        }
        
        return report


def main():
    """CLI entry point for schema validation"""
    validator = SchemaValidator()
    report = validator.generate_validation_report()
    
    print(json.dumps(report, indent=2))
    
    if not report["summary"]["is_valid"]:
        exit(1)


if __name__ == "__main__":
    main()