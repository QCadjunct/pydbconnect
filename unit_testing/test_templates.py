# Tests for database templates
import pytest
from pydatabaseconnection.core.template_manager import TemplateManager
from pydatabaseconnection.types.exceptions import DatabaseConfigError

class TestTemplates:
    """Unit tests for database templates"""

    def test_template_loading(self):
        """Test basic template loading"""
        template = TemplateManager("MSSQL")
        config = template.get_default_params()
        
        assert config is not None
        assert "DEFAULT_PARAMETERS" in config
        assert "CRUDBASIC" in config

    def test_template_validation(self):
        """Test template validation"""
        template = TemplateManager("MSSQL")
        
        # Test required fields
        required_fields = {
            "DEFAULT_PARAMETERS",
            "CRUDBASIC",
            "FINALIZED_CONNECTION_PARAMS"
        }
        
        config = template._get_engine_config()
        for field in required_fields:
            assert field in config["MSSQL"]

    def test_connection_string_generation(self):
        """Test connection string generation from template"""
        template = TemplateManager("MSSQL")
        params = {
            "DRIVER": "{ODBC Driver 17 for SQL Server}",
            "SERVER": "localhost",
            "PORT_NUMBER": 1433,
            "DATABASE_NAME": "test_db",
            "USERNAME": "user",
            "PASSWORD": "pass"
        }
        
        conn_string = template.get_connection_string(params)
        
        assert "DRIVER={ODBC Driver 17 for SQL Server}" in conn_string
        assert "SERVER=localhost" in conn_string
        assert "DATABASE=test_db" in conn_string

    def test_dsn_string_generation(self):
        """Test DSN string generation from template"""
        template = TemplateManager("MSSQL")
        params = {
            "DSN_NAME": "TestDSN",
            "USERNAME": "user",
            "PASSWORD": "pass"
        }
        
        dsn_string = template.get_connection_string(params, use_dsn=True)
        
        assert "DSN=TestDSN" in dsn_string
        assert "UID=user" in dsn_string
        assert "PWD=pass" in dsn_string

    @pytest.mark.parametrize("engine_type", ["MSSQL", "POSTGRESQL", "MYSQL"])
    def test_multiple_engine_templates(self, engine_type):
        """Test templates for different engine types"""
        template = TemplateManager(engine_type)
        config = template.get_default_params()
        
        assert config is not None
        assert config[engine_type]["CRUDBASIC"]["PARAMETER_PLACEHOLDER"] in ["?", "%s"]

    def test_invalid_engine_type(self):
        """Test behavior with invalid engine type"""
        with pytest.raises(DatabaseConfigError):
            TemplateManager("INVALID_ENGINE")

    def test_template_parameters(self):
        """Test template parameter handling"""
        template = TemplateManager("MSSQL")
        params = template.get_default_params()
        
        # Test default parameters
        assert "DRIVER" in params["MSSQL"]["DEFAULT_PARAMETERS"]
        assert "SERVER" in params["MSSQL"]["DEFAULT_PARAMETERS"]
        assert "PORT_NUMBER" in params["MSSQL"]["DEFAULT_PARAMETERS"]

    def test_template_customization(self):
        """Test template customization"""
        template = TemplateManager("MSSQL")
        custom_params = {
            "DRIVER": "{Custom Driver}",
            "SERVER": "custom.server",
            "PORT_NUMBER": 1444
        }
        
        # Apply custom parameters
        conn_string = template.get_connection_string(custom_params)
        
        assert "DRIVER={Custom Driver}" in conn_string
        assert "SERVER=custom.server" in conn_string
        assert "1444" in conn_string

    def test_template_required_params(self):
        """Test required parameter validation"""
        template = TemplateManager("MSSQL")
        required_params = template.get_required_params()
        
        assert "SERVER" in required_params
        assert "DATABASE_NAME" in required_params
        
        # Test validation with missing required params
        with pytest.raises(DatabaseConfigError):
            template.validate_params({})

    def test_template_feature_support(self):
        """Test feature support checking"""
        template = TemplateManager("MSSQL")
        
        assert template.supports_feature("dsn")
        assert template.supports_feature("transactions")
        assert not template.supports_feature("nonexistent_feature")
