import pytest
from ..core.connection import DatabaseConnection
from ..types.exceptions import DatabaseConnectionError

class TestDatabaseConnection:
    """Unit tests for database connection functionality"""

    def test_connection_initialization(self):
        """Test basic connection initialization"""
        db = DatabaseConnection("MSSQL")
        assert not db.is_connected
        assert db.template_manager is not None

    def test_connection_with_credentials(self, db_config):
        """Test connection with explicit credentials"""
        db = DatabaseConnection("MSSQL") \
            .with_credentials(
                db_config["MSSQL"]["username"],
                db_config["MSSQL"]["password"]
            )
        assert db._credentials["username"] == db_config["MSSQL"]["username"]
        assert db._credentials["password"] == db_config["MSSQL"]["password"]

    def test_connection_with_invalid_credentials(self):
        """Test connection with invalid credentials"""
        with pytest.raises(DatabaseConnectionError):
            DatabaseConnection("MSSQL") \
                .with_credentials("invalid", "invalid") \
                .connect()

    def test_connection_parameters(self, db_config):
        """Test connection with custom parameters"""
        db = DatabaseConnection("MSSQL") \
            .with_credentials(
                db_config["MSSQL"]["username"],
                db_config["MSSQL"]["password"]
            ) \
            .with_params(
                PORT_NUMBER=1433,
                DATABASE_NAME="test_db"
            )
        assert db._params["PORT_NUMBER"] == 1433
        assert db._params["DATABASE_NAME"] == "test_db"

    def test_connection_string_generation(self, db_config):
        """Test connection string generation"""
        db = DatabaseConnection("MSSQL") \
            .with_credentials(
                db_config["MSSQL"]["username"],
                db_config["MSSQL"]["password"]
            ) \
            .with_params(
                SERVER="localhost",
                PORT_NUMBER=1433,
                DATABASE_NAME="test_db"
            )
        conn_string = db.template_manager.get_connection_string(db._params)
        assert "SERVER=localhost" in conn_string
        assert "PORT=1433" in conn_string
        assert "DATABASE=test_db" in conn_string

    def test_connection_close(self, db_connection):
        """Test connection close"""
        assert db_connection.is_connected
        db_connection.close()
        assert not db_connection.is_connected

    @pytest.mark.parametrize("engine_type", ["MSSQL", "POSTGRESQL", "MYSQL"])
    def test_multiple_engine_types(self, engine_type, db_config):
        """Test connection with different engine types"""
        db = DatabaseConnection(engine_type)
        assert db.template_manager.target_engine == engine_type

    def test_dsn_connection(self, db_config):
        """Test DSN-based connection"""
        db = DatabaseConnection("MSSQL", use_dsn=True) \
            .with_credentials(
                db_config["MSSQL"]["username"],
                db_config["MSSQL"]["password"]
            ) \
            .with_params(DSN_NAME="TestDSN")
        conn_string = db.template_manager.get_connection_string(db._params, True)
        assert "DSN=TestDSN" in conn_string

    def test_connection_context_manager(self, db_config):
        """Test connection using context manager"""
        with DatabaseConnection("MSSQL") \
            .with_credentials(
                db_config["MSSQL"]["username"],
                db_config["MSSQL"]["password"]
            ) as db:
            assert db.is_connected
        assert not db.is_connected
