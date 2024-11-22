# validation.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from src.db_templates.database_target_engine_modules_enum_contraints \
     import ChangeDefaultUsernameAndPassword, TargetDatabaseConnectionStringOption, TargetDatabaseEngine
import src.db_templates.database_target_engine_template_modules as template

@dataclass
class ValidationResult:
    """
    Result of validation operations with context and suggestions.
    """
    is_valid: bool
    message: str = ""
    suggestions: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    validation_step: str = ""
    error_code: Optional[str] = None

    def add_suggestion(self, suggestion: str) -> 'ValidationResult':
        """Add a suggestion to the result."""
        self.suggestions.append(suggestion)
        return self

    def add_context(self, key: str, value: Any) -> 'ValidationResult':
        """Add context information."""
        self.context[key] = value
        return self

    def with_step(self, step: str) -> 'ValidationResult':
        """Set validation step."""
        self.validation_step = step
        return self

    def with_error_code(self, code: str) -> 'ValidationResult':
        """Set error code."""
        self.error_code = code
        return self

    @property
    def has_suggestions(self) -> bool:
        """Check if result has suggestions."""
        return len(self.suggestions) > 0

    @property
    def formatted_message(self) -> str:
        """Get formatted message with context."""
        base_msg = f"[{self.validation_step}] {self.message}"
        if self.has_suggestions:
            base_msg += "\nSuggestions:\n" + "\n".join(f"- {s}" for s in self.suggestions)
        return base_msg

class ValidationStep(Enum):
    """Enumeration of validation steps in connection chain."""
    ENGINE_VALIDATION = "engine_validation"
    CONNECTION_OPTION = "connection_option"
    CREDENTIALS = "credentials"
    PARAMETERS = "parameters"
    TEMPLATE = "template"
    CONNECTION = "connection"

def create_validation_result(
    is_valid: bool,
    step: ValidationStep,
    message: str = "",
    suggestions: List[str] = None,
    context: Dict[str, Any] = None,
    error_code: Optional[str] = None
) -> ValidationResult:
    """Factory function for creating ValidationResult instances."""
    return ValidationResult(
        is_valid=is_valid,
        message=message,
        suggestions=suggestions or [],
        context=context or {},
        validation_step=step.value,
        error_code=error_code
    )

def create_error_result(
    step: ValidationStep,
    message: str,
    suggestions: List[str] = None,
    context: Dict[str, Any] = None,
    error_code: Optional[str] = None
) -> ValidationResult:
    """Create an error validation result."""
    return create_validation_result(
        is_valid=False,
        step=step,
        message=message,
        suggestions=suggestions,
        context=context,
        error_code=error_code
    )

def create_success_result(
    step: ValidationStep,
    context: Dict[str, Any] = None
) -> ValidationResult:
    """Create a success validation result."""
    return create_validation_result(
        is_valid=True,
        step=step,
        context=context
    )

# Example usage in validate_connection_combinations:
def validate_connection_combinations(
    engine: TargetDatabaseEngine,
    connection_option: TargetDatabaseConnectionStringOption,
    credential_option: Optional[ChangeDefaultUsernameAndPassword] = None
) -> ValidationResult:
    """Validate engine, connection, and credential combinations."""
    engine_config = getattr(template, engine.name)
    
    # Validate DSN support
    if connection_option.uses_dsn and not engine_config['DEFAULT_PARAMETERS']['FORMAT_CONNECTION_STRING']['IS_DSN_NAME_SUPPORTED']:
        return create_error_result(
            step=ValidationStep.CONNECTION_OPTION,
            message=f"Engine {engine.name} does not support DSN connections",
            suggestions=[
                f"Use non-DSN options for {engine.name}:",
                "- DefaultFormatAndDefaultUserPwd",
                "- DefaultFormatAndChangeUserPwd"
            ],
            context={'engine': engine.name, 'option': connection_option.name},
            error_code="INVALID_DSN_OPTION"
        )
    
    # Additional validations...
    
    return create_success_result(
        step=ValidationStep.CONNECTION_OPTION,
        context={
            'engine': engine.name,
            'option': connection_option.name,
            'credential_option': credential_option.name if credential_option else None
        }
    )