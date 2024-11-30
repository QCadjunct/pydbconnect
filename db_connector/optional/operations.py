"""Simple database operations."""

import subprocess
from typing import Any


def backup_database(connection: Any, backup_path: str) -> None:
    """Create database backup."""
    db_type = connection.__class__.__module__.split(".")[0]

    if db_type == "psycopg2":
        subprocess.run(["pg_dump", "-f", backup_path])
    elif db_type == "mysql":
        subprocess.run(["mysqldump", "-r", backup_path])


def restore_database(connection: Any, backup_path: str) -> None:
    """Restore database from backup."""
    db_type = connection.__class__.__module__.split(".")[0]

    if db_type == "psycopg2":
        subprocess.run(["psql", "-f", backup_path])
    elif db_type == "mysql":
        subprocess.run(["mysql", "<", backup_path], shell=True)
