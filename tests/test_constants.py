from pydbconnect.db_constants.enum_connection_constants import TargetDatabaseEngine


def test_engine_module_name():
    assert TargetDatabaseEngine.DUCKDB.import_module == "duckdb"
