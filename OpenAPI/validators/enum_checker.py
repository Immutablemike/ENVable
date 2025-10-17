"""
ENVable OpenAPI Enum Consistency Checker

Specialized tool for validating enum consistency across the ENVable ecosystem.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Set, Optional
import logging

logger = logging.getLogger(__name__)


class EnumConsistencyChecker:
    """Specialized enum consistency validation for ENVable system"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """Initialize checker with base directory"""
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            # Assume we're in ENVable project structure
            self.base_dir = Path(__file__).parent.parent.parent
        
        self.openapi_dir = self.base_dir / "OpenAPI"
        self.components_dir = self.openapi_dir / "components"
        
    def load_standard_enums(self) -> Dict[str, List[str]]:
        """Load standardized enums from OpenAPI components"""
        standard_enums = {}
        
        try:
            # Load service types
            services_file = self.components_dir / "services.yaml"
            if services_file.exists():
                with open(services_file, 'r') as f:
                    services = yaml.safe_load(f)
                    if "ServiceType" in services and "enum" in services["ServiceType"]:
                        standard_enums["ServiceType"] = services["ServiceType"]["enum"]
            
            # Load credential types  
            creds_file = self.components_dir / "credentials.yaml"
            if creds_file.exists():
                with open(creds_file, 'r') as f:
                    creds = yaml.safe_load(f)
                    # CredentialType is referenced from services.yaml
                    pass
            
            # Load from services again for CredentialType
            if services_file.exists():
                with open(services_file, 'r') as f:
                    services = yaml.safe_load(f)
                    if "CredentialType" in services and "enum" in services["CredentialType"]:
                        standard_enums["CredentialType"] = services["CredentialType"]["enum"]
        
        except Exception as e:
            logger.error(f"Error loading standard enums: {e}")
        
        return standard_enums
    
    def find_python_files(self) -> List[Path]:
        """Find Python files in the project"""
        python_files = []
        
        # Look for Python files in common directories
        search_dirs = [
            self.base_dir,
            self.base_dir / "validators",
            self.base_dir / "tools", 
            self.base_dir / "generated"
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                for py_file in search_dir.rglob("*.py"):
                    if "__pycache__" not in str(py_file):
                        python_files.append(py_file)
        
        return python_files
    
    def find_hardcoded_service_names(self, file_path: Path) -> List[Dict[str, Any]]:
        """Find hardcoded service names in a Python file"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Common service name patterns
            service_patterns = [
                r'["\']openai["\']',
                r'["\']github["\']', 
                r'["\']stripe["\']',
                r'["\']supabase["\']',
                r'["\']cloudflare["\']',
                r'["\']mongodb["\']',
                r'["\']vercel["\']',
                r'["\']airtable["\']',
                r'["\']telegram["\']',
                r'["\']slack["\']',
                r'["\']discord["\']'
            ]
            
            for line_num, line in enumerate(lines, 1):
                for pattern in service_patterns:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        # Skip if it's in a comment
                        comment_pos = line.find('#')
                        if comment_pos != -1 and match.start() > comment_pos:
                            continue
                        
                        # Skip if it's in a URL or path
                        if 'http' in line.lower() or '/' in line:
                            continue
                        
                        findings.append({
                            "file": str(file_path.relative_to(self.base_dir)),
                            "line": line_num,
                            "content": line.strip(),
                            "service": match.group().strip('"\''),
                            "position": match.start()
                        })
        
        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")
        
        return findings
    
    def find_credential_type_usage(self, file_path: Path) -> List[Dict[str, Any]]:
        """Find credential type usage in a Python file"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Credential type patterns
            cred_patterns = [
                r'["\']api_key["\']',
                r'["\']token["\']',
                r'["\']url["\']', 
                r'["\']secret["\']',
                r'["\']certificate["\']',
                r'["\']oauth_token["\']',
                r'["\']webhook_url["\']',
                r'["\']connection_string["\']'
            ]
            
            for line_num, line in enumerate(lines, 1):
                for pattern in cred_patterns:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        # Skip comments and URLs
                        comment_pos = line.find('#')
                        if comment_pos != -1 and match.start() > comment_pos:
                            continue
                        
                        if 'http' in line.lower():
                            continue
                        
                        findings.append({
                            "file": str(file_path.relative_to(self.base_dir)),
                            "line": line_num,
                            "content": line.strip(),
                            "credential_type": match.group().strip('"\''),
                            "position": match.start()
                        })
        
        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")
        
        return findings
    
    def validate_service_consistency(self) -> Dict[str, Any]:
        """Validate service name consistency across codebase"""
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "findings": {
                "hardcoded_services": [],
                "credential_types": [],
                "inconsistencies": []
            }
        }
        
        # Load standard enums
        standard_enums = self.load_standard_enums()
        standard_services = set(standard_enums.get("ServiceType", []))
        standard_cred_types = set(standard_enums.get("CredentialType", []))
        
        # Find Python files
        python_files = self.find_python_files()
        
        # Check each file
        found_services = set()
        found_cred_types = set()
        
        for py_file in python_files:
            # Find hardcoded service names
            service_findings = self.find_hardcoded_service_names(py_file)
            result["findings"]["hardcoded_services"].extend(service_findings)
            
            for finding in service_findings:
                found_services.add(finding["service"])
            
            # Find credential type usage
            cred_findings = self.find_credential_type_usage(py_file)
            result["findings"]["credential_types"].extend(cred_findings)
            
            for finding in cred_findings:
                found_cred_types.add(finding["credential_type"])
        
        # Check for inconsistencies
        
        # Services not in standard enum
        unknown_services = found_services - standard_services
        for service in unknown_services:
            result["errors"].append(
                f"Service '{service}' found in code but not in ServiceType enum"
            )
            result["is_valid"] = False
        
        # Standard services not found in code
        unused_services = standard_services - found_services
        for service in unused_services:
            result["warnings"].append(
                f"ServiceType enum contains '{service}' but not found in code"
            )
        
        # Credential types not in standard enum
        unknown_cred_types = found_cred_types - standard_cred_types
        for cred_type in unknown_cred_types:
            result["errors"].append(
                f"Credential type '{cred_type}' found in code but not in CredentialType enum"
            )
            result["is_valid"] = False
        
        # Add summary
        result["summary"] = {
            "total_service_usages": len(result["findings"]["hardcoded_services"]),
            "unique_services_found": len(found_services),
            "standard_services": len(standard_services),
            "unknown_services": len(unknown_services),
            "total_credential_usages": len(result["findings"]["credential_types"]),
            "unique_cred_types_found": len(found_cred_types),
            "standard_cred_types": len(standard_cred_types),
            "unknown_cred_types": len(unknown_cred_types)
        }
        
        return result
    
    def suggest_enum_updates(self) -> Dict[str, Any]:
        """Suggest updates to enum definitions based on code analysis"""
        suggestions = {
            "service_type_additions": [],
            "credential_type_additions": [],
            "code_updates_needed": []
        }
        
        validation_result = self.validate_service_consistency()
        
        # Extract suggestions from validation results
        for error in validation_result["errors"]:
            if "not in ServiceType enum" in error:
                service = error.split("'")[1]
                suggestions["service_type_additions"].append({
                    "service": service,
                    "reason": "Found in codebase but missing from enum"
                })
            elif "not in CredentialType enum" in error:
                cred_type = error.split("'")[1] 
                suggestions["credential_type_additions"].append({
                    "credential_type": cred_type,
                    "reason": "Found in codebase but missing from enum"
                })
        
        # Suggest code updates for hardcoded values
        hardcoded = validation_result["findings"]["hardcoded_services"]
        unique_files = set(finding["file"] for finding in hardcoded)
        
        for file_path in unique_files:
            suggestions["code_updates_needed"].append({
                "file": file_path,
                "suggestion": "Replace hardcoded service names with enum references",
                "example": "Use ServiceType.OPENAI instead of 'openai'"
            })
        
        return suggestions
    
    def generate_enum_report(self) -> Dict[str, Any]:
        """Generate comprehensive enum consistency report"""
        report = {
            "timestamp": "2024-01-20T15:30:00Z",  # Placeholder
            "validation_result": self.validate_service_consistency(),
            "suggestions": self.suggest_enum_updates(),
            "standard_enums": self.load_standard_enums()
        }
        
        return report


def main():
    """CLI entry point"""
    import json
    
    checker = EnumConsistencyChecker()
    report = checker.generate_enum_report()
    
    print(json.dumps(report, indent=2))
    
    if not report["validation_result"]["is_valid"]:
        exit(1)


if __name__ == "__main__":
    main()