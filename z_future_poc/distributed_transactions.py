# distributed_transactions.py

from enum import Enum
from typing import Optional, Dict, Any
from templates.constraints import IsolationLevel, TargetDatabaseEngine


class TransactionCoordinatorType(Enum):
    """Supported distributed transaction coordinators."""

    MSDTC = "Microsoft DTC"  # For SQL Server
    XA = "XA"  # For MySQL, PostgreSQL
    LOCAL = "Local"  # For single database transactions


class DistributedTransactionManager:
    """Manages distributed transactions based on database engine."""

    def __init__(self, engine_type: TargetDatabaseEngine):
        self.engine_type = engine_type
        self.coordinator_type = self._get_coordinator_type()

    def _get_coordinator_type(self) -> TransactionCoordinatorType:
        """Determine appropriate transaction coordinator."""
        if self.engine_type == TargetDatabaseEngine.MSSQL:
            return TransactionCoordinatorType.MSDTC
        elif self.engine_type in (TargetDatabaseEngine.MYSQL, TargetDatabaseEngine.POSTGRESQL):
            return TransactionCoordinatorType.XA
        return TransactionCoordinatorType.LOCAL

    def get_transaction_coordinator_info(self) -> Dict[str, Any]:
        """Get recommended transaction coordinator information."""
        coordinator_info = {
            TransactionCoordinatorType.MSDTC: {
                "name": "Microsoft Distributed Transaction Coordinator",
                "setup_guide": "Enable MSDTC service and configure security",
                "connection_string_addition": ";Enlist=true",
                "documentation": "https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/msdtc",
            },
            TransactionCoordinatorType.XA: {
                "name": "XA Distributed Transactions",
                "setup_guide": "Configure max_prepared_transactions in postgresql.conf",
                "packages": ["python-transaction", "psycopg2"],
                "documentation": "https://www.postgresql.org/docs/current/runtime-config-resource.html#GUC-MAX-PREPARED-TRANSACTIONS",
            },
            TransactionCoordinatorType.LOCAL: {
                "name": "Local Transaction Manager",
                "note": "Distributed transactions not supported for this engine",
            },
        }
        return coordinator_info.get(self.coordinator_type, {})
