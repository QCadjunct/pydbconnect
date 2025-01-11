"""Transaction Management Module."""

from contextlib import contextmanager
from utils.decorators import ensure_connected, log_operation
from templates.constraints import IsolationLevel, TransactionType


class TransactionManager:
    def __init__(self, connector):
        """Initialize TransactionManager with a database connector."""
        self.connector = connector
        self._transaction_level = 0
        self._savepoints = []
        self._transaction_active = False
        self._current_isolation = IsolationLevel.READ_COMMITTED

    def _begin(self, isolation_level: IsolationLevel) -> None:
        """Handle beginning a transaction."""
        if self._transaction_active:
            self._transaction_level += 1
            return

        self.connector.execute(isolation_level.get_sql_statement())
        self.connector.execute(TransactionType.BEGIN.sql_statement)
        self._current_isolation = isolation_level
        self._transaction_active = True
        self._transaction_level = 1

    def _commit(self) -> None:
        """Handle committing a transaction."""
        if not self._transaction_active:
            return

        self._transaction_level -= 1
        if self._transaction_level == 0:
            self.connector.execute(TransactionType.COMMIT.sql_statement)
            self._reset_transaction_state()

    def _rollback(self) -> None:
        """Handle rolling back a transaction."""
        if not self._transaction_active:
            return

        try:
            self.connector.execute(TransactionType.ROLLBACK.sql_statement)
        finally:
            self._reset_transaction_state()

    def _manage_transaction(
        self, transaction_type: TransactionType, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED
    ) -> None:
        """Route transaction operation to appropriate handler."""
        transaction_handlers = {
            TransactionType.BEGIN: lambda: self._begin(isolation_level),
            TransactionType.COMMIT: self._commit,
            TransactionType.ROLLBACK: self._rollback,
        }

        if not transaction_type.can_nest and self._transaction_level > 0:
            return

        transaction_handlers[transaction_type]()

    def _reset_transaction_state(self) -> None:
        """Reset transaction state to default values."""
        self._transaction_active = False
        self._transaction_level = 0
        self._current_isolation = IsolationLevel.READ_COMMITTED
        self._savepoints = []

    @ensure_connected
    @log_operation("transaction_begin")
    def begin_transaction(self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED) -> None:
        """Begin transaction with specified isolation level."""
        self._manage_transaction(TransactionType.BEGIN, isolation_level)

    @ensure_connected
    @log_operation("transaction_commit")
    def commit(self) -> None:
        """Commit transaction."""
        self._manage_transaction(TransactionType.COMMIT)

    @log_operation("transaction_rollback")
    def rollback(self) -> None:
        """Rollback transaction."""
        self._manage_transaction(TransactionType.ROLLBACK)

    @contextmanager
    def transaction_scope(self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED):
        """Transaction context manager."""
        try:
            self.begin_transaction(isolation_level)
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise
