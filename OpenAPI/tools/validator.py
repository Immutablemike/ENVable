"""
ENVable OpenAPI CLI Validator

Command-line interface for OpenAPI schema validation and code generation.
"""

import json
import click
from pathlib import Path
from typing import Dict, Any

from .schema_validator import SchemaValidator
from .enum_checker import EnumConsistencyChecker
from .generator import CodeGenerator


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def cli(verbose: bool):
    """ENVable OpenAPI validation and generation CLI"""
    if verbose:
        import logging
        logging.basicConfig(level=logging.INFO)


@cli.command()
@click.option('--schema-file', '-s', default='api-spec.yaml', 
              help='OpenAPI schema file to validate')
@click.option('--fail-on-warnings', is_flag=True, 
              help='Fail if warnings are found')
def validate(schema_file: str, fail_on_warnings: bool):
    """Validate OpenAPI schema"""
    validator = SchemaValidator()
    
    try:
        result = validator.validate_openapi_spec(schema_file)
        
        click.echo(json.dumps(result, indent=2))
        
        if not result["is_valid"]:
            click.echo("❌ Schema validation failed", err=True)
            exit(1)
        
        if fail_on_warnings and result.get("warnings"):
            click.echo("⚠️  Failing due to warnings", err=True)
            exit(1)
        
        click.echo("✅ Schema validation passed")
        
    except Exception as e:
        click.echo(f"❌ Validation error: {e}", err=True)
        exit(1)


@cli.command()
@click.option('--fail-on-inconsistency', is_flag=True,
              help='Fail if enum inconsistencies found')
def enum_check(fail_on_inconsistency: bool):
    """Check enum consistency across codebase"""
    checker = EnumConsistencyChecker()
    
    try:
        result = checker.validate_service_consistency()
        
        click.echo(json.dumps(result, indent=2))
        
        if not result["is_valid"] and fail_on_inconsistency:
            click.echo("❌ Enum consistency check failed", err=True)
            exit(1)
        
        if result["is_valid"]:
            click.echo("✅ Enum consistency check passed")
        else:
            click.echo("⚠️  Enum inconsistencies found")
        
    except Exception as e:
        click.echo(f"❌ Enum check error: {e}", err=True)
        exit(1)


@cli.command()
@click.option('--pydantic', is_flag=True, help='Generate Pydantic models')
@click.option('--typescript', is_flag=True, help='Generate TypeScript types')
@click.option('--docs', is_flag=True, help='Generate documentation')
@click.option('--all', 'generate_all', is_flag=True, help='Generate all artifacts')
@click.option('--output-dir', '-o', help='Output directory for generated files')
def generate(pydantic: bool, typescript: bool, docs: bool, 
             generate_all: bool, output_dir: str):
    """Generate code artifacts from OpenAPI schema"""
    generator = CodeGenerator(output_dir=output_dir)
    
    try:
        if generate_all or not any([pydantic, typescript, docs]):
            results = generator.generate_all()
        else:
            results = {}
            
            if pydantic:
                results["pydantic_models"] = generator.generate_pydantic_models()
            
            if typescript:
                results["typescript_types"] = generator.generate_typescript_types()
            
            if docs:
                results["documentation"] = generator.generate_documentation()
        
        click.echo(json.dumps(results, indent=2))
        click.echo("✅ Code generation completed")
        
    except Exception as e:
        click.echo(f"❌ Generation error: {e}", err=True)
        exit(1)


@cli.command()
@click.option('--fail-on-issues', is_flag=True,
              help='Fail if any validation issues found')
def full_check(fail_on_issues: bool):
    """Run comprehensive validation and consistency checks"""
    click.echo("🔍 Running comprehensive OpenAPI validation...")
    
    # Schema validation
    click.echo("\n📋 Validating OpenAPI schema...")
    validator = SchemaValidator()
    
    try:
        validation_report = validator.generate_validation_report()
        
        click.echo(f"Schema validation: {'✅ PASS' if validation_report['summary']['is_valid'] else '❌ FAIL'}")
        
        if validation_report["summary"]["total_errors"] > 0:
            click.echo(f"Errors: {validation_report['summary']['total_errors']}")
        
        if validation_report["summary"]["total_warnings"] > 0:
            click.echo(f"Warnings: {validation_report['summary']['total_warnings']}")
        
    except Exception as e:
        click.echo(f"❌ Schema validation error: {e}", err=True)
        if fail_on_issues:
            exit(1)
        validation_report = {"summary": {"is_valid": False, "total_errors": 1}}
    
    # Enum consistency check
    click.echo("\n🔧 Checking enum consistency...")
    checker = EnumConsistencyChecker()
    
    try:
        enum_result = checker.validate_service_consistency()
        
        click.echo(f"Enum consistency: {'✅ PASS' if enum_result['is_valid'] else '⚠️  ISSUES'}")
        
        if not enum_result["is_valid"]:
            click.echo(f"Inconsistencies: {len(enum_result['errors'])}")
        
    except Exception as e:
        click.echo(f"❌ Enum check error: {e}", err=True)
        if fail_on_issues:
            exit(1)
        enum_result = {"is_valid": False, "errors": [str(e)]}
    
    # Summary
    click.echo("\n📊 Summary:")
    all_valid = (validation_report["summary"]["is_valid"] and enum_result["is_valid"])
    
    if all_valid:
        click.echo("✅ All checks passed - OpenAPI system is healthy")
    else:
        click.echo("⚠️  Issues found - review validation results")
        
        if fail_on_issues:
            click.echo("❌ Failing due to validation issues")
            exit(1)


@cli.command()
def report():
    """Generate comprehensive validation report"""
    click.echo("📊 Generating comprehensive OpenAPI report...")
    
    # Schema validation
    validator = SchemaValidator()
    validation_report = validator.generate_validation_report()
    
    # Enum consistency
    checker = EnumConsistencyChecker()
    enum_report = checker.generate_enum_report()
    
    # Combined report
    full_report = {
        "timestamp": validation_report.get("timestamp"),
        "schema_validation": validation_report,
        "enum_consistency": enum_report,
        "overall_status": {
            "is_healthy": (
                validation_report["summary"]["is_valid"] and 
                enum_report["validation_result"]["is_valid"]
            ),
            "total_errors": (
                validation_report["summary"]["total_errors"] +
                len(enum_report["validation_result"]["errors"])
            ),
            "total_warnings": (
                validation_report["summary"]["total_warnings"] +
                len(enum_report["validation_result"]["warnings"])
            )
        }
    }
    
    click.echo(json.dumps(full_report, indent=2))


if __name__ == "__main__":
    cli()