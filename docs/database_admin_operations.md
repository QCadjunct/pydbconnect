# Database Administration Operations Documentation

## Overview

The database administration module provides a flexible, extensible framework for managing different database engines through a consistent interface. It follows template and factory patterns while maintaining separation of concerns and avoiding hardcoded implementations.

## Key Features

### 1. Template Pattern Implementation

```python
from abc import ABC, abstractmethod
from typing import Optional

class DatabaseAdminTemplate(ABC):
    """
    Abstract base class defining the database administration interface.
    Each database engine implements this template to provide specific behaviors.
    """
    
    @abstractmethod
    def backup_database(self, path: str, options: Optional[dict] = None) -> None:
        """
        Create database backup.
        
        Args:
            path: Backup file path
            options: Engine-specific backup options
        """
        pass

    @abstractmethod
    def restore_database(self, path: str, options: Optional[dict] = None) -> None:
        """
        Restore database from backup.
        
        Args:
            path: Backup file path
            options: Engine-specific restore options
        """
        pass

    @abstractmethod
    def vacuum_database(self, full: bool = False) -> None:
        """
        Perform database maintenance operations.
        
        Args:
            full: Whether to perform full vacuum
        """
        pass

    @abstractmethod
    def get_database_size(self) -> int:
        """Get current database size in bytes."""
        pass

    @abstractmethod
    def get_table_sizes(self) -> dict:
        """Get sizes of all tables."""
        pass
```

### 2. Engine-Specific Implementations

```python
class PostgreSQLAdmin(DatabaseAdminTemplate):
    """PostgreSQL-specific administration operations."""
    
    def backup_database(self, path: str, options: Optional[dict] = None) -> None:
        options = options or {}
        compression = options.get('compression', 'gzip')
        
        cmd = f"pg_dump -Fc -Z 9 -f {path}"
        if compression == 'none':
            cmd = f"pg_dump -Fp -f {path}"
            
        self._execute_command(cmd)

    def vacuum_database(self, full: bool = False) -> None:
        cmd = "VACUUM FULL ANALYZE" if full else "VACUUM ANALYZE"
        self._execute_sql(cmd)

class MySQLAdmin(DatabaseAdminTemplate):
    """MySQL-specific administration operations."""
    
    def backup_database(self, path: str, options: Optional[dict] = None) -> None:
        options = options or {}
        with_events = options.get('with_events', False)
        
        cmd = f"mysqldump --routines --triggers"
        if with_events:
            cmd += " --events"
            
        cmd += f" > {path}"
        self._execute_command(cmd)

    def vacuum_database(self, full: bool = False) -> None:
        tables = self._get_tables()
        for table in tables:
            self._execute_sql(f"OPTIMIZE TABLE {table}")
```

### 3. Integration with TargetDatabaseEngine

```python
from enum import Enum

class TargetDatabaseEngine(Enum):
    """Supported database engines."""
    POSTGRESQL = "POSTGRESQL"
    MYSQL = "MYSQL"
    MSSQL = "MSSQL"
    SQLITE = "SQLITE"
    
    def get_admin_handler(self) -> DatabaseAdminTemplate:
        """Get appropriate admin handler for this engine."""
        from . import templates
        config = getattr(templates, self.value)
        handler_class = config.get('ADMIN_HANDLER')
        return handler_class()
```

### 4. Template Configuration Structure

```python
# templates.py
POSTGRESQL = {
    'ENGINE': 'postgresql',
    'ADMIN_HANDLER': PostgreSQLAdmin,
    'DEFAULT_BACKUP_OPTIONS': {
        'compression': 'gzip',
        'format': 'custom'
    },
    'COMMANDS': {
        'BACKUP': 'pg_dump',
        'RESTORE': 'pg_restore',
        'VACUUM': 'VACUUM'
    }
}

MYSQL = {
    'ENGINE': 'mysql',
    'ADMIN_HANDLER': MySQLAdmin,
    'DEFAULT_BACKUP_OPTIONS': {
        'with_events': True,
        'add_locks': True
    },
    'COMMANDS': {
        'BACKUP': 'mysqldump',
        'RESTORE': 'mysql',
        'OPTIMIZE': 'OPTIMIZE'
    }
}
```

### 5. Error Handling and Validation

```python
from typing import Optional
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AdminOperationResult:
    """Result of administrative operation."""
    success: bool
    message: str
    duration: float
    timestamp: datetime = datetime.now()
    details: Optional[dict] = None

class DatabaseAdminError(Exception):
    """Base class for administration errors."""
    pass

class BackupError(DatabaseAdminError):
    """Error during backup operation."""
    pass

class RestoreError(DatabaseAdminError):
    """Error during restore operation."""
    pass

class AdminOperation:
    """Base class for administrative operations with error handling."""
    
    def __init__(self, handler: DatabaseAdminTemplate):
        self.handler = handler
        self.logger = logging.getLogger(__name__)

    def execute(self, operation: str, *args, **kwargs) -> AdminOperationResult:
        """Execute administrative operation with error handling."""
        start_time = datetime.now()
        
        try:
            # Validate inputs
            self._validate_inputs(*args, **kwargs)
            
            # Execute operation
            method = getattr(self.handler, operation)
            method(*args, **kwargs)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Log success
            self.logger.info(
                f"Operation {operation} completed successfully in {duration:.2f}s"
            )
            
            return AdminOperationResult(
                success=True,
                message=f"{operation} completed successfully",
                duration=duration
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            
            # Log error
            self.logger.error(
                f"Operation {operation} failed after {duration:.2f}s: {str(e)}"
            )
            
            return AdminOperationResult(
                success=False,
                message=str(e),
                duration=duration,
                details={'error_type': type(e).__name__}
            )

    def _validate_inputs(self, *args, **kwargs):
        """Validate operation inputs."""
        if 'path' in kwargs:
            path = kwargs['path']
            if not isinstance(path, str):
                raise ValueError("Path must be a string")
            if not os.path.exists(os.path.dirname(path)):
                raise ValueError(f"Directory does not exist: {os.path.dirname(path)}")
```

### 6. Usage Examples

```python
# Basic usage
engine = TargetDatabaseEngine.POSTGRESQL
admin = engine.get_admin_handler()

# Backup with options
admin.backup_database(
    path="/backups/db.backup",
    options={'compression': 'gzip'}
)

# Maintenance operations
admin.vacuum_database(full=True)

# With error handling
operation = AdminOperation(admin)
result = operation.execute(
    'backup_database',
    path="/backups/db.backup"
)

if result.success:
    print(f"Backup completed in {result.duration:.2f}s")
else:
    print(f"Backup failed: {result.message}")
```

### 7. Integration Example

```python
from pydbconnect import MultiDatabaseConnector
from datetime import datetime

class DatabaseManager:
    """High-level database management interface."""
    
    def __init__(self, connector: MultiDatabaseConnector):
        self.connector = connector
        self.admin_handlers = {}
    
    def initialize_admin(self, database_name: str) -> None:
        """Initialize admin handler for database."""
        if database_name not in self.connector.databases:
            raise ValueError(f"Database {database_name} not attached")
            
        db_info = self.connector.databases[database_name]
        engine = TargetDatabaseEngine(db_info.type)
        self.admin_handlers[database_name] = engine.get_admin_handler()
    
    def backup_all_databases(self, backup_dir: str) -> dict:
        """Backup all attached databases."""
        results = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for db_name in self.connector.databases:
            if db_name not in self.admin_handlers:
                self.initialize_admin(db_name)
                
            admin = self.admin_handlers[db_name]
            operation = AdminOperation(admin)
            
            backup_path = f"{backup_dir}/{db_name}_{timestamp}.backup"
            result = operation.execute('backup_database', path=backup_path)
            results[db_name] = result
            
        return results

# Usage example
connector = MultiDatabaseConnector()
connector.attach("postgresql://...", "main_db", "POSTGRESQL")
connector.attach("mysql://...", "reporting_db", "MYSQL")

manager = DatabaseManager(connector)
results = manager.backup_all_databases("/backups")

for db_name, result in results.items():
    print(f"{db_name}: {'Success' if result.success else 'Failed'}")
```

### 8. Adding New Database Engine Support

1. Create handler implementation:
```python
class NewDatabaseAdmin(DatabaseAdminTemplate):
    """Administration handler for new database type."""
    
    def backup_database(self, path: str, options: Optional[dict] = None) -> None:
        # Implement backup logic
        pass
    
    def restore_database(self, path: str, options: Optional[dict] = None) -> None:
        # Implement restore logic
        pass
```

2. Add template configuration:
```python
# templates.py
NEW_DATABASE = {
    'ENGINE': 'new_database',
    'ADMIN_HANDLER': NewDatabaseAdmin,
    'DEFAULT_BACKUP_OPTIONS': {
        'option1': 'value1'
    }
}
```

3. Add to TargetDatabaseEngine:
```python
class TargetDatabaseEngine(Enum):
    NEW_DATABASE = "NEW_DATABASE"
```

pah
# Database Administrative Operations Guide

## Overview

This module provides a unified interface for database administrative operations across different database engines. It leverages template-based configurations for extensibility and consistent behavior.

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [Administrative Operations](#administrative-operations)
3. [Engine-Specific Features](#engine-specific-features)
4. [Usage Examples](#usage-examples)
5. [Best Practices](#best-practices)
6. [Advanced Features](#advanced-features)
7. [Error Handling](#error-handling)

## Core Concepts

### Engine Templates

Database engines are defined in the `TargetDatabaseEngine` enum, with configurations loaded from templates:

```python
from enum import Enum
from typing import Dict, Any
from abc import ABC, abstractmethod

class TargetDatabaseEngine(Enum):
    """
    Supported database engine types.
    Each value maps to a template configuration.
    """
    MSSQL = "MSSQL"
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    SQLITE3 = "SQLITE3"
    DUCKDB = "DUCKDB"
    PSYCOPG2 = "PSYCOPG2"

    def get_admin_handler(self) -> 'DatabaseAdminTemplate':
        """Get admin handler from engine's template configuration."""
        from . import templates
        engine_config = getattr(templates, self.value)
        return engine_config['ADMIN_HANDLER']()
```

### Administrative Template

Base template defining standard administrative operations:

```python
class DatabaseAdminTemplate(ABC):
    """Template for database administrative operations."""
    
    @abstractmethod
    def backup_database(self, path: str, **options) -> None:
        """Backup database to specified path."""
        pass
    
    @abstractmethod
    def restore_database(self, path: str, **options) -> None:
        """Restore database from specified path."""
        pass
    
    @abstractmethod
    def vacuum(self, table: str = None, **options) -> None:
        """Perform database or table vacuum."""
        pass
    
    @abstractmethod
    def analyze_statistics(self, table: str = None, **options) -> Dict[str, Any]:
        """Update database statistics."""
        pass
```

## Administrative Operations

### Basic Operations Example

```python
from pydbconnect import (
    TargetDatabaseEngine, 
    DatabaseConnection
)

def perform_maintenance(conn: DatabaseConnection):
    """Perform standard database maintenance."""
    # Get admin handler for engine
    admin = conn.engine_type.get_admin_handler()
    
    # Backup database
    admin.backup_database("/backups/daily.bak")
    
    # Update statistics
    admin.analyze_statistics()
    
    # Vacuum database
    admin.vacuum()

# Usage
conn = DatabaseConnection(TargetDatabaseEngine.POSTGRESQL)
perform_maintenance(conn)
```

### Scheduled Backups

```python
import schedule
import time
from datetime import datetime
from pathlib import Path

class DatabaseMaintenance:
    def __init__(self, engine: TargetDatabaseEngine, backup_dir: str):
        self.admin = engine.get_admin_handler()
        self.backup_dir = Path(backup_dir)
        
    def daily_backup(self):
        """Perform daily backup with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}.bak"
        
        try:
            self.admin.backup_database(str(backup_path))
            print(f"Backup created: {backup_path}")
        except Exception as e:
            print(f"Backup failed: {e}")
    
    def schedule_backups(self):
        """Schedule daily backups at 2 AM."""
        schedule.every().day.at("02:00").do(self.daily_backup)
        
        while True:
            schedule.run_pending()
            time.sleep(60)

# Usage
maintenance = DatabaseMaintenance(
    TargetDatabaseEngine.POSTGRESQL,
    "/path/to/backups"
)
maintenance.schedule_backups()
```

## Engine-Specific Features

### PostgreSQL Implementation

```python
class PostgreSQLAdmin(DatabaseAdminTemplate):
    """PostgreSQL administrative operations."""
    
    def backup_database(self, path: str, **options) -> None:
        format = options.get('format', 'custom')
        compression = options.get('compression', 9)
        jobs = options.get('jobs', 4)
        
        command = f"""
            pg_dump 
                --format={format} 
                --compress={compression} 
                --jobs={jobs} 
                --file={path}
        """
        self._execute_command(command)
    
    def vacuum(self, table: str = None, **options) -> None:
        analyze = options.get('analyze', True)
        full = options.get('full', False)
        
        query = "VACUUM "
        if analyze:
            query += "ANALYZE "
        if full:
            query += "FULL "
        if table:
            query += f"{table}"
            
        self._execute_sql(query)
```

### MSSQL Implementation

```python
class MSSQLAdmin(DatabaseAdminTemplate):
    """MSSQL administrative operations."""
    
    def backup_database(self, path: str, **options) -> None:
        compression = options.get('compression', True)
        verify = options.get('verify', True)
        
        query = f"""
            BACKUP DATABASE {self.database_name}
            TO DISK = '{path}'
            WITH 
                {'COMPRESSION, ' if compression else ''}
                {'VERIFY, ' if verify else ''}
                STATS = 10
        """
        self._execute_sql(query)
    
    def analyze_statistics(self, table: str = None, **options) -> Dict[str, Any]:
        sample_percent = options.get('sample_percent', 100)
        
        if table:
            query = f"""
                UPDATE STATISTICS {table}
                WITH FULLSCAN, SAMPLE {sample_percent} PERCENT
            """
        else:
            query = "sp_updatestats"
            
        return self._execute_sql(query)
```

## Usage Examples

### Comprehensive Maintenance

```python
from typing import List, Dict
import logging

class DatabaseMaintenanceManager:
    def __init__(self, engine: TargetDatabaseEngine):
        self.admin = engine.get_admin_handler()
        self.logger = logging.getLogger(__name__)
    
    def perform_full_maintenance(self, 
                               backup_path: str,
                               tables: List[str] = None) -> Dict[str, Any]:
        """Perform complete database maintenance."""
        results = {}
        
        try:
            # Backup
            self.logger.info("Starting database backup")
            self.admin.backup_database(backup_path, compression=True)
            results['backup'] = 'success'
            
            # Update statistics
            self.logger.info("Updating statistics")
            stats = self.admin.analyze_statistics()
            results['statistics'] = stats
            
            # Vacuum tables
            if tables:
                self.logger.info("Vacuuming specific tables")
                for table in tables:
                    self.admin.vacuum(table, analyze=True)
            else:
                self.logger.info("Vacuuming entire database")
                self.admin.vacuum(analyze=True)
            results['vacuum'] = 'success'
            
            return results
            
        except Exception as e:
            self.logger.error(f"Maintenance failed: {e}")
            results['error'] = str(e)
            raise
```

### Backup Verification

```python
import hashlib
from pathlib import Path

class BackupVerification:
    def __init__(self, admin_handler: DatabaseAdminTemplate):
        self.admin = admin_handler
    
    def verify_backup(self, backup_path: str) -> bool:
        """Verify backup integrity."""
        backup_file = Path(backup_path)
        
        # Calculate backup checksum
        original_checksum = self._calculate_checksum(backup_file)
        
        # Restore to temporary database
        temp_db = "temp_verify_db"
        try:
            self.admin.restore_database(
                backup_path,
                database_name=temp_db
            )
            
            # Backup temporary database
            verify_path = backup_file.parent / f"verify_{backup_file.name}"
            self.admin.backup_database(str(verify_path))
            
            # Compare checksums
            verify_checksum = self._calculate_checksum(verify_path)
            
            return original_checksum == verify_checksum
            
        finally:
            # Cleanup
            verify_path.unlink(missing_ok=True)
            self.admin.drop_database(temp_db)
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file."""
        sha256 = hashlib.sha256()
        
        with file_path.open('rb') as f:
            for block in iter(lambda: f.read(65536), b''):
                sha256.update(block)
                
        return sha256.hexdigest()
```

## Best Practices

1. **Always Verify Backups**
```python
def safe_backup(admin: DatabaseAdminTemplate, path: str):
    """Perform backup with verification."""
    admin.backup_database(path)
    verifier = BackupVerification(admin)
    
    if not verifier.verify_backup(path):
        raise ValueError("Backup verification failed")
```

2. **Implement Retry Logic**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

class RetryableAdmin:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def safe_operation(self, func, *args, **kwargs):
        """Retry administrative operations with exponential backoff."""
        return func(*args, **kwargs)
```

3. **Monitor Operation Times**
```python
import time
from contextlib import contextmanager

@contextmanager
def operation_timer(operation_name: str):
    """Time database operations."""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        print(f"{operation_name} took {duration:.2f} seconds")
```

Would you like me to:
1. Add more administrative operations?
2. Include monitoring examples?
3. Add backup verification features?
4. Include high availability configurations?