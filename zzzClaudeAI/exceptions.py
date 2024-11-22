# exceptions.py
"""
Exception hierarchy for database operations with validation chain support.
"""
from typing import Any, List, Dict, Optional
from enum import Enum
from src.db_templates.database_target_engine_modules_enum_contraints \
     import TargetDatabaseConnectionStringOption, TargetDatabaseEngine,ChangeDefaultUsernameAndPassword
# import src.db_templates.database_target_engine_template_modules as template

class DatabaseError(Exception):
    """Base exception for all database-related errors."""
    pass

class ConnectionError(DatabaseError):
    """Connection failure errors."""
    pass

class CredentialsError(DatabaseError):
    """Authentication and credential issues."""
    pass

class ValidationError(DatabaseError):
    """Enhanced validation error with chain context."""
    
    def __init__(self, 
                 field: str, 
                 message: str, 
                 chain_step: str,
                 validation_context: Dict[str, Any],
                 value: Any = None):
        self.field = field
        self.value = value
        self.chain_step = chain_step
        self.validation_context = validation_context
        super().__init__(
            f"Validation failed at {chain_step} - {field}: {message}"
        )

class ChainValidationError(DatabaseError):
    """Errors in the fluent validation chain."""
    
    def __init__(self, 
                 step: str,
                 engine_type: 'TargetDatabaseEngine',
                 connection_option: 'TargetDatabaseConnectionStringOption',
                 message: str,
                 suggestions: List[str],
                 context: Optional[Dict[str, Any]] = None):
        self.step = step
        self.engine_type = engine_type
        self.connection_option = connection_option
        self.suggestions = suggestions
        self.context = context or {}
        
        error_message = (
            f"Validation failed at step '{step}'\n"
            f"Engine: {engine_type.name}\n"
            f"Connection Option: {connection_option.name}\n"
            f"Error: {message}\n\n"
            f"Suggestions:\n{chr(10).join(f'- {s}' for s in suggestions)}"
        )
        super().__init__(error_message)

class TemplateValidationError(DatabaseError):
    """Template configuration validation errors."""
    
    def __init__(self, 
                 template_name: str,
                 field: str,
                 message: str,
                 template_context: Dict[str, Any]):
        self.template_name = template_name
        self.field = field
        self.template_context = template_context
        super().__init__(
            f"Template validation failed for {template_name}.{field}: {message}"
        )

class ConnectionChainError(DatabaseError):
    """Errors in connection chain execution."""
    
    def __init__(self, 
                 current_step: str,
                 previous_steps: List[str],
                 message: str):
        self.current_step = current_step
        self.previous_steps = previous_steps
        self.chain = ' -> '.join(previous_steps + [current_step])
        super().__init__(
            f"Connection chain failed at '{current_step}'\n"
            f"Chain: {self.chain}\n"
            f"Error: {message}"
        )

class ParameterValidationError(ValidationError):
    """Parameter validation with template context."""
    
    def __init__(self, 
                 parameter: str,
                 template_value: Any,
                 provided_value: Any,
                 message: str):
        self.template_value = template_value
        self.provided_value = provided_value
        super().__init__(
            field=parameter,
            message=f"{message} (expected: {template_value}, got: {provided_value})",
            chain_step="parameter_validation",
            validation_context={
                'template_value': template_value,
                'provided_value': provided_value
            }
        )

class QueryError(DatabaseError):
    """Query execution errors."""
    pass

class TransactionError(DatabaseError):
    """Transaction-related failures."""
    pass

class ConfigurationError(DatabaseError):
    """Configuration-related issues."""
    pass

# Error codes with validation chain support
ERROR_CODES = {
    # Existing codes...
    "CONNECTION_FAILED": ("E001", "Failed to establish database connection"),
    "CONNECTION_TIMEOUT": ("E002", "Connection attempt timed out"),
    
    # New validation chain codes
    "CHAIN_VALIDATION_FAILED": ("V001", "Validation chain failed"),
    "TEMPLATE_VALIDATION_FAILED": ("V002", "Template validation failed"),
    "PARAMETER_VALIDATION_FAILED": ("V003", "Parameter validation failed"),
    "CREDENTIAL_VALIDATION_FAILED": ("V004", "Credential validation failed"),
    "CONNECTION_CHAIN_FAILED": ("V005", "Connection chain execution failed")
}

def get_error_info(code: str) -> tuple:
    """Get error code and message."""
    return ERROR_CODES.get(code, ("UNKNOWN", "Unknown error occurred"))

def create_chain_error(step: str,
                      engine_type: 'TargetDatabaseEngine',
                      connection_option: 'TargetDatabaseConnectionStringOption',
                      message: str,
                      suggestions: List[str],
                      context: Optional[Dict[str, Any]] = None) -> ChainValidationError:
    """Create a chain validation error with context."""
    return ChainValidationError(
        step=step,
        engine_type=engine_type,
        connection_option=connection_option,
        message=message,
        suggestions=suggestions,
        context=context
    )

def create_template_error(template_name: str,
                         field: str,
                         message: str,
                         context: Dict[str, Any]) -> TemplateValidationError:
    """Create a template validation error."""
    return TemplateValidationError(
        template_name=template_name,
        field=field,
        message=message,
        template_context=context
    )

# Usage example in validation chain:
"""
try:
    connector.attach(...).change_default_username_and_password(...).connect_to_database()
except ChainValidationError as e:
    print(f"Validation failed:\n{e}")
    print(f"Step: {e.step}")
    print(f"Suggestions: {e.suggestions}")
except TemplateValidationError as e:
    print(f"Template error in {e.template_name}: {e.message}")
except ConnectionChainError as e:
    print(f"Chain failed: {e.chain}")
    print(f"At step: {e.current_step}")
"""