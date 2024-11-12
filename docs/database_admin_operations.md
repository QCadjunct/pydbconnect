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

# Database Administrative Operations Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Operations](#core-operations)
3. [Usage Examples](#usage-examples)
4. [Monitoring and Verification](#monitoring-and-verification)
5. [High Availability](#high-availability)
6. [Best Practices](#best-practices)

## Overview

The database_admin_operations module provides template-driven administrative operations for different database engines. This design enables:

- 🔄 Template-based extensibility
- 🛡️ Type-safe operations
- 📊 Performance monitoring
- 💾 Backup management
- 🔍 Operation verification

```python
from typing import Dict, Any, Optional
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
import logging

class AdminOperationType(Enum):
    """Types of administrative operations."""
    BACKUP = "backup"
    RESTORE = "restore"
    VERIFY = "verify"
    OPTIMIZE = "optimize"
    ANALYZE = "analyze"

@dataclass
class AdminOperationResult:
    """Result of administrative operation."""
    operation_type: AdminOperationType
    success: bool
    execution_time: float
    details: Dict[str, Any]
    timestamp: datetime = datetime.now()

class DatabaseAdminTemplate(ABC):
    """
    Template for database administrative operations.
    
    Each database engine implements this template through its
    configuration to provide engine-specific behaviors.
    """
    
    @abstractmethod
    def backup_database(self, 
                       path: str, 
                       options: Optional[Dict[str, Any]] = None) -> AdminOperationResult:
        """Backup database to specified path."""
        pass
    
    @abstractmethod
    def restore_database(self, 
                        path: str, 
                        options: Optional[Dict[str, Any]] = None) -> AdminOperationResult:
        """Restore database from specified path."""
        pass
    
    @abstractmethod
    def verify_database(self, 
                       options: Optional[Dict[str, Any]] = None) -> AdminOperationResult:
        """Verify database integrity."""
        pass
    
    @abstractmethod
    def optimize_database(self, 
                         options: Optional[Dict[str, Any]] = None) -> AdminOperationResult:
        """Optimize database performance."""
        pass

    def log_operation(self, result: AdminOperationResult) -> None:
        """Log administrative operation result."""
        log_level = logging.INFO if result.success else logging.ERROR
        logging.log(
            log_level,
            f"{result.operation_type.value} operation "
            f"{'succeeded' if result.success else 'failed'}: "
            f"{result.details}"
        )
```

## Usage Examples

### Basic Administrative Operations

```python
from pydbconnect import TargetDatabaseEngine

# Get admin handler for PostgreSQL
db_engine = TargetDatabaseEngine.POSTGRESQL
admin = db_engine.get_admin_handler()

# Perform backup
result = admin.backup_database(
    path="/backups/db_backup_20240201.bak",
    options={
        "compression": True,
        "verify": True
    }
)

if result.success:
    print(f"Backup completed in {result.execution_time:.2f} seconds")
else:
    print(f"Backup failed: {result.details.get('error')}")

# Verify database
verify_result = admin.verify_database(
    options={
        "check_indexes": True,
        "check_constraints": True
    }
)

if verify_result.success:
    print("Database verification passed")
else:
    print(f"Verification issues found: {verify_result.details}")
```

### Automated Backup Management

```python
class BackupManager:
    """Manages automated database backups."""
    
    def __init__(self, 
                 engine: TargetDatabaseEngine,
                 backup_path: str):
        self.admin = engine.get_admin_handler()
        self.backup_path = Path(backup_path)
        self.backup_path.mkdir(parents=True, exist_ok=True)
    
    def perform_backup(self, 
                      verify: bool = True, 
                      compress: bool = True) -> AdminOperationResult:
        """Perform backup with verification."""
        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_path / f"backup_{timestamp}.bak"
        
        # Perform backup
        result = self.admin.backup_database(
            str(backup_file),
            options={
                "compression": compress,
                "verify": verify
            }
        )
        
        if result.success and verify:
            # Verify backup
            verify_result = self.verify_backup(backup_file)
            result.details['verification'] = verify_result.details
        
        return result
    
    def verify_backup(self, backup_file: Path) -> AdminOperationResult:
        """Verify backup file integrity."""
        return self.admin.verify_database(
            options={
                "backup_file": str(backup_file)
            }
        )
    
    def cleanup_old_backups(self, 
                           keep_days: int = 30) -> None:
        """Remove backups older than specified days."""
        cutoff = datetime.now() - timedelta(days=keep_days)
        
        for backup_file in self.backup_path.glob("*.bak"):
            if datetime.fromtimestamp(backup_file.stat().st_mtime) < cutoff:
                backup_file.unlink()

# Usage example
backup_manager = BackupManager(
    engine=TargetDatabaseEngine.POSTGRESQL,
    backup_path="/path/to/backups"
)

# Schedule regular backups
def scheduled_backup():
    result = backup_manager.perform_backup(
        verify=True,
        compress=True
    )
    
    if result.success:
        backup_manager.cleanup_old_backups(keep_days=30)
    
    return result
```

### Monitoring Integration

```python
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class DatabaseMetrics:
    """Database performance metrics."""
    database_size: int
    index_size: int
    active_connections: int
    cache_hit_ratio: float
    transaction_rate: float
    timestamp: datetime = datetime.now()

class DatabaseMonitor:
    """Monitors database performance and health."""
    
    def __init__(self, engine: TargetDatabaseEngine):
        self.admin = engine.get_admin_handler()
        self.metrics_history: List[DatabaseMetrics] = []
    
    def collect_metrics(self) -> DatabaseMetrics:
        """Collect current database metrics."""
        result = self.admin.verify_database(
            options={"collect_metrics": True}
        )
        
        metrics = DatabaseMetrics(
            database_size=result.details['database_size'],
            index_size=result.details['index_size'],
            active_connections=result.details['active_connections'],
            cache_hit_ratio=result.details['cache_hit_ratio'],
            transaction_rate=result.details['transaction_rate']
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def analyze_performance(self, 
                          window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Analyze performance over time window."""
        cutoff = datetime.now() - window
        recent_metrics = [
            m for m in self.metrics_history
            if m.timestamp >= cutoff
        ]
        
        return {
            'avg_cache_hit_ratio': sum(m.cache_hit_ratio for m in recent_metrics) / len(recent_metrics),
            'max_connections': max(m.active_connections for m in recent_metrics),
            'avg_transaction_rate': sum(m.transaction_rate for m in recent_metrics) / len(recent_metrics)
        }

# Usage example
monitor = DatabaseMonitor(TargetDatabaseEngine.POSTGRESQL)

# Collect current metrics
metrics = monitor.collect_metrics()
print(f"Database size: {metrics.database_size / 1024**3:.2f} GB")
print(f"Cache hit ratio: {metrics.cache_hit_ratio:.2%}")

# Analyze performance
analysis = monitor.analyze_performance(window=timedelta(hours=24))
print(f"24-hour average cache hit ratio: {analysis['avg_cache_hit_ratio']:.2%}")
```

# Database Administrative Operations Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Operations](#core-operations)
3. [Usage Examples](#usage-examples)
4. [Monitoring and Verification](#monitoring-and-verification)
5. [High Availability](#high-availability)
6. [Best Practices](#best-practices)

## Overview

The database_admin_operations module provides template-driven administrative operations for different database engines. This design enables:

- 🔄 Template-based extensibility
- 🛡️ Type-safe operations
- 📊 Performance monitoring
- 💾 Backup management
- 🔍 Operation verification

```python
from typing import Dict, Any, Optional
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
import logging

class AdminOperationType(Enum):
    """Types of administrative operations."""
    BACKUP = "backup"
    RESTORE = "restore"
    VERIFY = "verify"
    OPTIMIZE = "optimize"
    ANALYZE = "analyze"

@dataclass
class AdminOperationResult:
    """Result of administrative operation."""
    operation_type: AdminOperationType
    success: bool
    execution_time: float
    details: Dict[str, Any]
    timestamp: datetime = datetime.now()

class DatabaseAdminTemplate(ABC):
    """
    Template for database administrative operations.
    
    Each database engine implements this template through its
    configuration to provide engine-specific behaviors.
    """
    
    @abstractmethod
    def backup_database(self, 
                       path: str, 
                       options: Optional[Dict[str, Any]] = None) -> AdminOperationResult:
        """Backup database to specified path."""
        pass
    
    @abstractmethod
    def restore_database(self, 
                        path: str, 
                        options: Optional[Dict[str, Any]] = None) -> AdminOperationResult:
        """Restore database from specified path."""
        pass
    
    @abstractmethod
    def verify_database(self, 
                       options: Optional[Dict[str, Any]] = None) -> AdminOperationResult:
        """Verify database integrity."""
        pass
    
    @abstractmethod
    def optimize_database(self, 
                         options: Optional[Dict[str, Any]] = None) -> AdminOperationResult:
        """Optimize database performance."""
        pass

    def log_operation(self, result: AdminOperationResult) -> None:
        """Log administrative operation result."""
        log_level = logging.INFO if result.success else logging.ERROR
        logging.log(
            log_level,
            f"{result.operation_type.value} operation "
            f"{'succeeded' if result.success else 'failed'}: "
            f"{result.details}"
        )
```

## Usage Examples

### Basic Administrative Operations

```python
from pydbconnect import TargetDatabaseEngine

# Get admin handler for PostgreSQL
db_engine = TargetDatabaseEngine.POSTGRESQL
admin = db_engine.get_admin_handler()

# Perform backup
result = admin.backup_database(
    path="/backups/db_backup_20240201.bak",
    options={
        "compression": True,
        "verify": True
    }
)

if result.success:
    print(f"Backup completed in {result.execution_time:.2f} seconds")
else:
    print(f"Backup failed: {result.details.get('error')}")

# Verify database
verify_result = admin.verify_database(
    options={
        "check_indexes": True,
        "check_constraints": True
    }
)

if verify_result.success:
    print("Database verification passed")
else:
    print(f"Verification issues found: {verify_result.details}")
```

### Automated Backup Management

```python
class BackupManager:
    """Manages automated database backups."""
    
    def __init__(self, 
                 engine: TargetDatabaseEngine,
                 backup_path: str):
        self.admin = engine.get_admin_handler()
        self.backup_path = Path(backup_path)
        self.backup_path.mkdir(parents=True, exist_ok=True)
    
    def perform_backup(self, 
                      verify: bool = True, 
                      compress: bool = True) -> AdminOperationResult:
        """Perform backup with verification."""
        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_path / f"backup_{timestamp}.bak"
        
        # Perform backup
        result = self.admin.backup_database(
            str(backup_file),
            options={
                "compression": compress,
                "verify": verify
            }
        )
        
        if result.success and verify:
            # Verify backup
            verify_result = self.verify_backup(backup_file)
            result.details['verification'] = verify_result.details
        
        return result
    
    def verify_backup(self, backup_file: Path) -> AdminOperationResult:
        """Verify backup file integrity."""
        return self.admin.verify_database(
            options={
                "backup_file": str(backup_file)
            }
        )
    
    def cleanup_old_backups(self, 
                           keep_days: int = 30) -> None:
        """Remove backups older than specified days."""
        cutoff = datetime.now() - timedelta(days=keep_days)
        
        for backup_file in self.backup_path.glob("*.bak"):
            if datetime.fromtimestamp(backup_file.stat().st_mtime) < cutoff:
                backup_file.unlink()

# Usage example
backup_manager = BackupManager(
    engine=TargetDatabaseEngine.POSTGRESQL,
    backup_path="/path/to/backups"
)

# Schedule regular backups
def scheduled_backup():
    result = backup_manager.perform_backup(
        verify=True,
        compress=True
    )
    
    if result.success:
        backup_manager.cleanup_old_backups(keep_days=30)
    
    return result
```

### Monitoring Integration

```python
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class DatabaseMetrics:
    """Database performance metrics."""
    database_size: int
    index_size: int
    active_connections: int
    cache_hit_ratio: float
    transaction_rate: float
    timestamp: datetime = datetime.now()

class DatabaseMonitor:
    """Monitors database performance and health."""
    
    def __init__(self, engine: TargetDatabaseEngine):
        self.admin = engine.get_admin_handler()
        self.metrics_history: List[DatabaseMetrics] = []
    
    def collect_metrics(self) -> DatabaseMetrics:
        """Collect current database metrics."""
        result = self.admin.verify_database(
            options={"collect_metrics": True}
        )
        
        metrics = DatabaseMetrics(
            database_size=result.details['database_size'],
            index_size=result.details['index_size'],
            active_connections=result.details['active_connections'],
            cache_hit_ratio=result.details['cache_hit_ratio'],
            transaction_rate=result.details['transaction_rate']
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def analyze_performance(self, 
                          window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Analyze performance over time window."""
        cutoff = datetime.now() - window
        recent_metrics = [
            m for m in self.metrics_history
            if m.timestamp >= cutoff
        ]
        
        return {
            'avg_cache_hit_ratio': sum(m.cache_hit_ratio for m in recent_metrics) / len(recent_metrics),
            'max_connections': max(m.active_connections for m in recent_metrics),
            'avg_transaction_rate': sum(m.transaction_rate for m in recent_metrics) / len(recent_metrics)
        }

# Usage example
monitor = DatabaseMonitor(TargetDatabaseEngine.POSTGRESQL)

# Collect current metrics
metrics = monitor.collect_metrics()
print(f"Database size: {metrics.database_size / 1024**3:.2f} GB")
print(f"Cache hit ratio: {metrics.cache_hit_ratio:.2%}")

# Analyze performance
analysis = monitor.analyze_performance(window=timedelta(hours=24))
print(f"24-hour average cache hit ratio: {analysis['avg_cache_hit_ratio']:.2%}")
```

# Database Administrative Operations Module

## Overview

The database_admin_operations module provides a unified interface for database administrative tasks across different database engines. It leverages template-based configuration for extensibility and supports operations like backup, restore, maintenance, and monitoring.

## Table of Contents
1. [Core Components](#core-components)
2. [Template Structure](#template-structure)
3. [Basic Usage](#basic-usage)
4. [Advanced Operations](#advanced-operations)
5. [High Availability](#high-availability)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Best Practices](#best-practices)
8. [Examples](#examples)

## Core Components

### Database Admin Template
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging

class DatabaseAdminTemplate(ABC):
    """
    Abstract base class for database administration operations.
    Provides unified interface for common administrative tasks.
    """
    
    def __init__(self, connection: Any):
        self.connection = connection
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def backup_database(self, path: str, options: Optional[Dict[str, Any]] = None) -> str:
        """
        Backup database to specified path.
        
        Args:
            path: Backup file path
            options: Engine-specific backup options
            
        Returns:
            str: Backup file path
        """
        pass

    @abstractmethod
    def restore_database(self, backup_path: str, 
                        options: Optional[Dict[str, Any]] = None) -> None:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup file
            options: Engine-specific restore options
        """
        pass

    @abstractmethod
    def verify_backup(self, backup_path: str) -> bool:
        """
        Verify backup file integrity.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            bool: True if backup is valid
        """
        pass

    @abstractmethod
    def get_database_size(self) -> int:
        """
        Get current database size in bytes.
        
        Returns:
            int: Database size in bytes
        """
        pass
```

### Usage with Engine Templates
```python
from enum import Enum
from typing import Optional

class TargetDatabaseEngine(Enum):
    """Supported database engines."""
    MSSQL = "MSSQL"
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    SQLITE3 = "SQLITE3"
    DUCKDB = "DUCKDB"
    PSYCOPG2 = "PSYCOPG2"

    def get_admin_handler(self, connection: Any) -> DatabaseAdminTemplate:
        """
        Get admin handler for this engine type.
        
        Args:
            connection: Database connection object
            
        Returns:
            DatabaseAdminTemplate: Engine-specific admin handler
        """
        from . import templates
        engine_config = getattr(templates, self.value)
        handler_class = engine_config.get('ADMIN_HANDLER')
        
        if not handler_class:
            raise ValueError(f"No admin handler for {self.value}")
            
        return handler_class(connection)
```

## Basic Usage

### Basic Operations
```python
from pydbconnect import DatabaseConnection, TargetDatabaseEngine

# Initialize connection
db = DatabaseConnection(TargetDatabaseEngine.POSTGRESQL)
db.connect()

# Get admin handler
admin = db.engine_type.get_admin_handler(db._connection)

# Backup database
backup_path = admin.backup_database(
    path="/backups/mydb.bak",
    options={
        "compression": True,
        "verify": True
    }
)

# Restore database
admin.restore_database(
    backup_path=backup_path,
    options={
        "recovery_mode": "RECOVERY"
    }
)

# Get database size
size_bytes = admin.get_database_size()
print(f"Database size: {size_bytes / (1024*1024):.2f} MB")
```

### Advanced Backup Options
```python
# Full backup with compression
admin.backup_database(
    path="/backups/full_backup.bak",
    options={
        "type": "FULL",
        "compression": True,
        "verify": True,
        "checksum": True,
        "stats": True
    }
)

# Differential backup
admin.backup_database(
    path="/backups/diff_backup.bak",
    options={
        "type": "DIFFERENTIAL",
        "base_backup": "/backups/full_backup.bak"
    }
)
```

## Advanced Operations

### Backup Chain Management
```python
class BackupChainManager:
    """Manages backup chains and retention."""
    
    def __init__(self, admin_handler: DatabaseAdminTemplate):
        self.admin = admin_handler
        
    def create_backup_chain(self, base_path: str, retention_days: int = 7):
        """Create backup chain with retention policy."""
        # Create full backup
        full_path = self.admin.backup_database(
            f"{base_path}/full_{datetime.now():%Y%m%d}.bak",
            options={"type": "FULL"}
        )
        
        # Create differential backups
        for i in range(retention_days):
            diff_path = self.admin.backup_database(
                f"{base_path}/diff_{datetime.now():%Y%m%d}_{i}.bak",
                options={
                    "type": "DIFFERENTIAL",
                    "base_backup": full_path
                }
            )
            
            # Verify backup
            if not self.admin.verify_backup(diff_path):
                raise ValueError(f"Backup verification failed: {diff_path}")
```

### Database Maintenance
```python
class DatabaseMaintenance:
    """Database maintenance operations."""
    
    def __init__(self, admin_handler: DatabaseAdminTemplate):
        self.admin = admin_handler
        
    def optimize_database(self):
        """Perform database optimization."""
        stats = self.admin.analyze_database()
        
        if stats['fragmentation_level'] > 30:
            self.admin.defragment_database()
            
        if stats['unused_space'] > 1024 * 1024 * 100:  # 100MB
            self.admin.shrink_database()
            
        return self.admin.get_database_stats()
```

## High Availability

### Replication Setup
```python
class ReplicationManager:
    """Manages database replication."""
    
    def __init__(self, primary_admin: DatabaseAdminTemplate, 
                 replica_admin: DatabaseAdminTemplate):
        self.primary = primary_admin
        self.replica = replica_admin
        
    def setup_replication(self):
        """Setup streaming replication."""
        # Backup primary
        backup_path = self.primary.backup_database(
            "/tmp/replica_seed.bak",
            options={"type": "FULL"}
        )
        
        # Restore to replica
        self.replica.restore_database(
            backup_path,
            options={"standby_mode": True}
        )
        
        # Configure streaming
        self.primary.configure_replication(
            target=self.replica,
            options={
                "sync_mode": "ASYNC",
                "apply_delay": 0
            }
        )
```

## Monitoring & Maintenance

### Performance Monitoring
```python
class PerformanceMonitor:
    """Database performance monitoring."""
    
    def __init__(self, admin_handler: DatabaseAdminTemplate):
        self.admin = admin_handler
        
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics."""
        return {
            "size": self.admin.get_database_size(),
            "connections": self.admin.get_active_connections(),
            "cache_hit_ratio": self.admin.get_cache_stats(),
            "query_stats": self.admin.get_query_stats(),
            "lock_info": self.admin.get_lock_info(),
            "io_stats": self.admin.get_io_stats()
        }
```

## Best Practices

### 1. Backup Verification
```python
def verify_and_log_backup(admin: DatabaseAdminTemplate, 
                         backup_path: str, 
                         required_size: int):
    """Verify backup meets requirements."""
    # Check file exists
    if not os.path.exists(backup_path):
        raise ValueError(f"Backup file not found: {backup_path}")
        
    # Verify integrity
    if not admin.verify_backup(backup_path):
        raise ValueError(f"Backup verification failed: {backup_path}")
        
    # Check size
    if os.path.getsize(backup_path) < required_size:
        raise ValueError(f"Backup file too small: {backup_path}")
        
    logging.info(f"Backup verified successfully: {backup_path}")
```

### 2. Resource Management
```python
class DatabaseResourceManager:
    """Manages database resources."""
    
    def __init__(self, admin_handler: DatabaseAdminTemplate):
        self.admin = admin_handler
        
    def optimize_resources(self):
        """Optimize database resource usage."""
        # Check space usage
        size = self.admin.get_database_size()
        if size > self.admin.get_max_size():
            self.admin.archive_old_data()
            
        # Optimize memory
        memory_stats = self.admin.get_memory_stats()
        if memory_stats['usage'] > 80:
            self.admin.optimize_memory_usage()
```

### 3. Error Handling
```python
class AdminOperationHandler:
    """Safe handling of admin operations."""
    
    def __init__(self, admin_handler: DatabaseAdminTemplate):
        self.admin = admin_handler
        
    def safe_backup(self, path: str) -> Optional[str]:
        """Execute backup with error handling."""
        try:
            backup_path = self.admin.backup_database(path)
            if self.admin.verify_backup(backup_path):
                return backup_path
        except Exception as e:
            logging.error(f"Backup failed: {e}")
            self.admin.cleanup_failed_backup(path)
        return None
```

# Database Administrative Operations

## Overview

The database_admin_operations module provides a template-driven approach to database administration tasks, leveraging the `TargetDatabaseEngine` configuration for extensible database management.

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [Administrative Operations](#administrative-operations)
3. [High Availability Features](#high-availability-features)
4. [Backup Management](#backup-management)
5. [Performance Tuning](#performance-tuning)
6. [Examples](#examples)

## Core Concepts

### Engine-Specific Administration

```python
from pydbconnect import TargetDatabaseEngine
from datetime import datetime

# Get engine-specific admin handler
engine = TargetDatabaseEngine.POSTGRESQL
admin = engine.get_admin_handler()

# Basic operations
admin.backup_database("/path/to/backup.bak")
admin.restore_database("/path/to/backup.bak")
```

### Template-Based Configuration

```python
# Example template configuration
POSTGRESQL = {
    "ADMIN_HANDLER": PostgreSQLAdmin,
    "BACKUP": {
        "FORMAT": "custom",
        "COMPRESSION": 9,
        "JOBS": 4,
        "VERIFY": True
    },
    "MAINTENANCE": {
        "VACUUM_THRESHOLD": 20,  # Percentage
        "ANALYZE_THRESHOLD": 10  # Percentage
    }
}
```

## Administrative Operations

### Basic Administration
```python
from pydbconnect.admin import DatabaseAdmin

class PostgreSQLAdmin(DatabaseAdmin):
    def vacuum_analyze(self, table: Optional[str] = None) -> None:
        """Vacuum and analyze database or specific table."""
        cmd = "VACUUM ANALYZE"
        if table:
            cmd += f" {table}"
        self.execute(cmd)
    
    def reindex(self, table: Optional[str] = None) -> None:
        """Reindex database or specific table."""
        cmd = "REINDEX"
        if table:
            cmd += f" TABLE {table}"
        self.execute(cmd)

# Usage
admin = TargetDatabaseEngine.POSTGRESQL.get_admin_handler()
admin.vacuum_analyze("large_table")
admin.reindex()
```

### Schema Management
```python
class SchemaOperations(DatabaseAdmin):
    def create_schema(self, schema: str) -> None:
        self.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    
    def drop_schema(self, schema: str, cascade: bool = False) -> None:
        cmd = f"DROP SCHEMA {schema}"
        if cascade:
            cmd += " CASCADE"
        self.execute(cmd)
    
    def clone_schema(self, source: str, target: str) -> None:
        """Clone schema structure and data."""
        self.execute(f"""
            DO $$
            DECLARE
                obj record;
            BEGIN
                -- Create schema
                EXECUTE 'CREATE SCHEMA IF NOT EXISTS ' || quote_ident('{target}');
                
                -- Copy tables
                FOR obj IN 
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = '{source}'
                LOOP
                    EXECUTE 'CREATE TABLE ' || 
                            quote_ident('{target}') || '.' || 
                            quote_ident(obj.tablename) || 
                            ' (LIKE ' || 
                            quote_ident('{source}') || '.' || 
                            quote_ident(obj.tablename) || 
                            ' INCLUDING ALL)';
                            
                    EXECUTE 'INSERT INTO ' || 
                            quote_ident('{target}') || '.' || 
                            quote_ident(obj.tablename) || 
                            ' SELECT * FROM ' || 
                            quote_ident('{source}') || '.' || 
                            quote_ident(obj.tablename);
                END LOOP;
            END $$;
        """)
```

## High Availability Features

### Replication Management
```python
class ReplicationAdmin(DatabaseAdmin):
    def check_replication_status(self) -> Dict[str, Any]:
        """Check replication status and lag."""
        if self.engine == TargetDatabaseEngine.POSTGRESQL:
            return self.execute("""
                SELECT 
                    client_addr,
                    state,
                    sent_lsn,
                    write_lsn,
                    flush_lsn,
                    replay_lsn,
                    EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))::INT 
                        as lag_seconds
                FROM pg_stat_replication
            """)
    
    def promote_standby(self) -> None:
        """Promote standby to primary."""
        if self.engine == TargetDatabaseEngine.POSTGRESQL:
            self.execute("SELECT pg_promote()")
    
    def setup_streaming_replication(self, primary_host: str, 
                                  primary_port: int) -> None:
        """Setup streaming replication."""
        config = {
            "primary_conninfo": (
                f"host={primary_host} "
                f"port={primary_port} "
                f"user=replication "
                f"password=xxx"
            ),
            "recovery_target_timeline": "latest"
        }
        
        self._write_recovery_conf(config)
```

## Backup Management

### Advanced Backup Features
```python
class BackupManager(DatabaseAdmin):
    def backup_with_verification(self, path: str) -> bool:
        """Create backup with verification."""
        try:
            # Create backup
            self.backup_database(path)
            
            # Verify backup
            if not self.verify_backup(path):
                raise ValueError("Backup verification failed")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False
    
    def incremental_backup(self, base_path: str, 
                          incremental_path: str) -> None:
        """Create incremental backup."""
        if self.engine == TargetDatabaseEngine.POSTGRESQL:
            self.execute(f"""
                SELECT pg_start_backup('{base_path}');
                -- Copy files
                SELECT pg_stop_backup();
            """)
    
    def point_in_time_recovery(self, backup_path: str, 
                             target_time: datetime) -> None:
        """Restore to specific point in time."""
        config = {
            "restore_command": f"cp /path/to/archive/%f %p",
            "recovery_target_time": target_time.isoformat()
        }
        
        self.restore_database(backup_path)
        self._write_recovery_conf(config)
```

### Backup Verification
```python
class BackupVerification(DatabaseAdmin):
    def verify_backup(self, path: str) -> bool:
        """Verify backup integrity."""
        if self.engine == TargetDatabaseEngine.POSTGRESQL:
            try:
                result = self.execute(f"""
                    SELECT pg_verify_backup(
                        '{path}',
                        repair_actions => true
                    )
                """)
                return result[0][0]
            except Exception as e:
                self.logger.error(f"Backup verification failed: {e}")
                return False
    
    def test_restore(self, backup_path: str) -> bool:
        """Test restore in temporary environment."""
        temp_db = f"test_restore_{int(time.time())}"
        try:
            # Create temporary database
            self.execute(f"CREATE DATABASE {temp_db}")
            
            # Restore backup
            self.restore_database(backup_path, target_db=temp_db)
            
            # Run tests
            self._run_restore_tests(temp_db)
            
            return True
            
        finally:
            # Cleanup
            self.execute(f"DROP DATABASE IF EXISTS {temp_db}")
```

## Performance Tuning

### Automated Optimization
```python
class PerformanceOptimizer(DatabaseAdmin):
    def analyze_table_statistics(self, table: str) -> Dict[str, Any]:
        """Analyze table statistics."""
        return self.execute(f"""
            SELECT 
                schemaname,
                tablename,
                n_live_tup,
                n_dead_tup,
                last_vacuum,
                last_analyze
            FROM pg_stat_user_tables
            WHERE tablename = '{table}'
        """)
    
    def optimize_table(self, table: str, 
                      analyze: bool = True) -> None:
        """Optimize table based on statistics."""
        stats = self.analyze_table_statistics(table)
        
        if stats['n_dead_tup'] / stats['n_live_tup'] > 0.2:
            self.vacuum_analyze(table)
        
        if analyze:
            self.analyze_table(table)
    
    def suggest_indexes(self, table: str) -> List[str]:
        """Suggest indexes based on query patterns."""
        return self.execute(f"""
            SELECT 
                schemaname || '.' || tablename as table_name,
                indexrelname as index_name,
                idx_scan as index_scans,
                idx_tup_read as tuples_read,
                idx_tup_fetch as tuples_fetched
            FROM pg_stat_user_indexes
            WHERE tablename = '{table}'
            ORDER BY idx_scan DESC
        """)
```

## Examples

### Complete Administration Workflow
```python
def manage_database(engine: TargetDatabaseEngine):
    """Complete database administration workflow."""
    admin = engine.get_admin_handler()
    
    try:
        # Backup current state
        backup_path = f"/backups/db_{datetime.now():%Y%m%d_%H%M%S}.bak"
        admin.backup_with_verification(backup_path)
        
        # Optimize performance
        admin.vacuum_analyze()
        admin.reindex()
        
        # Check replication
        if isinstance(admin, ReplicationAdmin):
            status = admin.check_replication_status()
            print(f"Replication status: {status}")
        
        # Optimize specific tables
        tables = admin.get_large_tables()
        for table in tables:
            admin.optimize_table(table)
        
    except Exception as e:
        print(f"Administration failed: {e}")
        # Restore from backup if needed
        admin.restore_database(backup_path)
```

# Database Administrative Operations Documentation

## Overview

PyDBConnect provides a robust, template-based system for database administrative operations that extends to any supported database engine. This module implements administrative operations using a flexible, extensible pattern that follows DuckDB's philosophy of dynamic engine support.

## Table of Contents
1. [Core Features](#core-features)
2. [Usage Examples](#usage-examples)
3. [Administrative Operations](#administrative-operations)
4. [High Availability Features](#high-availability-features)
5. [Backup and Recovery](#backup-and-recovery)
6. [Performance Optimization](#performance-optimization)

## Core Features

### Basic Administrative Operations
```python
from pydbconnect import TargetDatabaseEngine, DatabaseConnection

# Get admin handler directly from engine type
engine = TargetDatabaseEngine.POSTGRESQL
admin = engine.get_admin_handler()

# Perform operations
admin.backup_database("/path/to/backup")
admin.restore_database("/path/to/restore")
```

### Integration with Database Connection
```python
from pydbconnect import DatabaseConnection, TargetDatabaseEngine

class AdminConnection:
    def __init__(self, engine: TargetDatabaseEngine):
        self.engine = engine
        self.admin = engine.get_admin_handler()
        self.connection = None

    def connect(self, **connection_params):
        """Establish database connection with admin privileges."""
        self.connection = DatabaseConnection(
            self.engine,
            connection_params
        ).connect_to_database()
        return self

    def backup(self, path: str, verify: bool = True):
        """Perform database backup with optional verification."""
        self.admin.backup_database(path)
        if verify:
            self.admin.verify_backup(path)

    def close(self):
        """Close admin connection."""
        if self.connection:
            self.connection.close()
```

## Usage Examples

### 1. Basic Administrative Tasks
```python
# Initialize admin connection
admin_conn = AdminConnection(TargetDatabaseEngine.POSTGRESQL)
admin_conn.connect(
    host="localhost",
    database="production_db",
    username="admin_user",
    password="admin_pass"
)

try:
    # Perform backup
    admin_conn.backup("/backups/prod_backup.bak")
    
    # Get database statistics
    stats = admin_conn.admin.get_database_stats()
    print(f"Database Size: {stats['size']}")
    print(f"Active Connections: {stats['active_connections']}")
    
finally:
    admin_conn.close()
```

### 2. Scheduled Maintenance
```python
import schedule
import time

def scheduled_maintenance(engine: TargetDatabaseEngine, 
                        connection_params: dict):
    """Perform scheduled database maintenance."""
    admin_conn = AdminConnection(engine)
    
    try:
        admin_conn.connect(**connection_params)
        
        # Perform maintenance tasks
        admin_conn.admin.analyze_tables()
        admin_conn.admin.vacuum_database()
        admin_conn.admin.reindex_database()
        
        # Create backup
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        admin_conn.backup(f"/backups/maintenance_{timestamp}.bak")
        
    finally:
        admin_conn.close()

# Schedule daily maintenance
schedule.every().day.at("02:00").do(
    scheduled_maintenance,
    engine=TargetDatabaseEngine.POSTGRESQL,
    connection_params={
        "host": "localhost",
        "database": "production_db",
        "username": "admin_user",
        "password": "admin_pass"
    }
)
```

### 3. High Availability Configuration
```python
def setup_replication(primary_conn: AdminConnection, 
                     replica_conn: AdminConnection):
    """Set up streaming replication between databases."""
    try:
        # Configure primary
        primary_conn.admin.configure_replication(
            role="primary",
            replica_host="replica.example.com",
            replica_port=5432
        )
        
        # Configure replica
        replica_conn.admin.configure_replication(
            role="replica",
            primary_host="primary.example.com",
            primary_port=5432
        )
        
        # Verify replication
        replica_conn.admin.verify_replication_status()
        
    except Exception as e:
        print(f"Replication setup failed: {e}")
        raise
```

## Administrative Operations

### Database Statistics
```python
async def monitor_database_health(admin_conn: AdminConnection):
    """Monitor database health metrics."""
    stats = await admin_conn.admin.get_detailed_stats()
    
    return {
        "size": stats["database_size"],
        "connections": stats["active_connections"],
        "locks": stats["lock_count"],
        "oldest_transaction": stats["oldest_transaction_age"],
        "cache_hit_ratio": stats["cache_hit_ratio"],
        "index_usage": stats["index_usage_stats"]
    }
```

### Performance Optimization
```python
async def optimize_database(admin_conn: AdminConnection):
    """Perform database optimization tasks."""
    # Analyze table statistics
    await admin_conn.admin.analyze_tables()
    
    # Identify and fix fragmentation
    fragmented_tables = await admin_conn.admin.get_fragmented_tables(
        threshold=30  # 30% fragmentation threshold
    )
    
    for table in fragmented_tables:
        await admin_conn.admin.defragment_table(table["name"])
    
    # Optimize indexes
    await admin_conn.admin.optimize_indexes()
    
    # Update statistics
    await admin_conn.admin.update_statistics()
```

### Backup Verification
```python
class BackupVerification:
    def __init__(self, admin_conn: AdminConnection):
        self.admin_conn = admin_conn

    async def verify_backup(self, backup_path: str):
        """Comprehensive backup verification."""
        # Verify backup integrity
        is_valid = await self.admin_conn.admin.verify_backup_integrity(
            backup_path
        )
        if not is_valid:
            raise ValueError("Backup integrity check failed")
            
        # Test restore in temporary database
        temp_restore = await self.admin_conn.admin.test_restore(
            backup_path,
            temp_db="verify_restore"
        )
        
        # Compare row counts
        source_counts = await self.admin_conn.admin.get_table_row_counts()
        restored_counts = await temp_restore.get_table_row_counts()
        
        if source_counts != restored_counts:
            raise ValueError("Restored database row counts do not match source")
            
        # Cleanup
        await temp_restore.drop_database("verify_restore")
        
        return True
```

### High Availability Configuration
```python
class HighAvailabilityConfig:
    def __init__(self, admin_conn: AdminConnection):
        self.admin_conn = admin_conn

    async def setup_streaming_replication(self, replica_configs: List[dict]):
        """Configure streaming replication with multiple replicas."""
        # Configure primary
        await self.admin_conn.admin.configure_primary_for_replication(
            max_wal_senders=len(replica_configs) + 2,
            wal_level='replica',
            max_replication_slots=len(replica_configs) + 2
        )
        
        # Configure each replica
        for replica in replica_configs:
            # Create replication slot
            slot_name = f"replica_{replica['name']}"
            await self.admin_conn.admin.create_replication_slot(slot_name)
            
            # Configure replica connection
            await self.admin_conn.admin.setup_replica_connection(
                name=replica['name'],
                host=replica['host'],
                port=replica['port'],
                slot_name=slot_name
            )
            
        # Verify replication status
        await self.admin_conn.admin.verify_replication_status()
```

## Would you like me to continue with:
1. More administrative operations examples?
2. High availability configurations?
3. Backup verification patterns?
4. Performance optimization strategies?