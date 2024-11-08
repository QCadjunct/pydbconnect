import pytest
import os
from ..core import DatabaseConnection
from ..types.exceptions import CredentialError
from ..utils.credentials import CredentialManager

class TestCredentials:
    """Unit tests for credential management"""

    def setup_method(self):
        """Setup test environment variables"""
        os.environ["MSSQL_USERNAME"] = "test_user"
        os.environ["MSSQL_PASSWORD"] = "test_pass"

    def teardown_method(self):
        """Clean up test environment variables"""
        del os.environ["MSSQL_USERNAME"]
        del os.environ["MSSQL_PASSWORD"]

    def test_explicit_credentials(self):
        """Test setting explicit credentials"""
        manager = CredentialManager()
        manager.set_credentials("user", "pass")
        credentials = manager.get_credentials()
        
        assert credentials["username"] == "user"
        assert credentials["password"] == "pass"
        assert not credentials["is_default"]

    def test_env_credentials(self):
        """Test loading credentials from environment"""
        manager = CredentialManager()
        manager.load_from_env("MSSQL")
        credentials = manager.get_credentials()
        
        assert credentials["username"] == "test_user"
        assert credentials["password"] == "test_pass"
        assert credentials["is_default"]

    def test_missing_env_credentials(self):
        """Test behavior with missing environment variables"""
        if "MSSQL_USERNAME" in os.environ:
            del os.environ["MSSQL_USERNAME"]
        
        with pytest.raises(CredentialError) as exc_info:
            manager = CredentialManager()
            manager.load_from_env("MSSQL")
        
        assert "Missing environment variables" in str(exc_info.value)

    def test_credential_validation(self):
        """Test credential validation"""
        manager = CredentialManager()
        
        with pytest.raises(CredentialError):
            manager.set_credentials("", "pass")
        
        with pytest.raises(CredentialError):
            manager.set_credentials("user", "")
        
        with pytest.raises(CredentialError):
            manager.set_credentials(None, "pass")

    def test_credential_clearing(self):
        """Test clearing credentials"""
        manager = CredentialManager()
        manager.set_credentials("user", "pass")
        
        manager.clear_credentials()
        
        with pytest.raises(CredentialError):
            manager.get_credentials()

    def test_credential_overriding(self):
        """Test overriding existing credentials"""
        manager = CredentialManager()
        manager.set_credentials("user1", "pass1")
        
        manager.set_credentials("user2", "pass2")
        credentials = manager.get_credentials()
        
        assert credentials["username"] == "user2"
        assert credentials["password"] == "pass2"
        assert not credentials["is_default"]

    @pytest.mark.parametrize("engine_type", ["MSSQL", "POSTGRESQL", "MYSQL"])
    def test_multiple_engine_credentials(self, engine_type):
        """Test credentials for different engine types"""
        os.environ[f"{engine_type}_USERNAME"] = "test_user"
        os.environ[f"{engine_type}_PASSWORD"] = "test_pass"
        
        try:
            manager = CredentialManager()
            manager.load_from_env(engine_type)
            credentials = manager.get_credentials()
            
            assert credentials["username"] == "test_user"
            assert credentials["password"] == "test_pass"
            
        finally:
            del os.environ[f"{engine_type}_USERNAME"]
            del os.environ[f"{engine_type}_PASSWORD"]

    def test_credential_security(self):
        """Test credential security measures"""
        manager = CredentialManager()
        manager.set_credentials("user", "pass")
        
        # Test string representation doesn't expose credentials
        assert "pass" not in str(manager)
        assert "user" not in str(manager)
        
        # Test repr doesn't expose credentials
        assert "pass" not in repr(manager)
        assert "user" not in repr(manager)

    def test_database_connection_integration(self):
        """Test credentials with database connection"""
        db = DatabaseConnection("MSSQL")
        
        # Test with explicit credentials
        db.with_credentials("user", "pass")
        assert db._credentials["username"] == "user"
        assert db._credentials["password"] == "pass"
        
        # Test with environment credentials
        db = DatabaseConnection("MSSQL")
        db.with_credentials_from_env()
        assert db._credentials["username"] == "test_user"
        assert db._credentials["password"] == "test_pass"
