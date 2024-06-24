from abc import ABC, abstractmethod


class RepositorySession(ABC):
    """
    Abstract base class for managing database transactions with automatic rollback.

    Manages transactions using the context management protocol, ensuring that any changes
    are automatically rolled back if not explicitly committed before exiting the context.
    This behavior guarantees data integrity by preventing partial or erroneous commits.

    Subclasses must implement `commit` and `rollback` methods for specific database interactions.

    Usage:
        with derived_repository_session_instance as session:
            # Perform database operations
            # All operations within this context block are part of the same transaction
            # Call session.commit() to save changes, otherwise changes will rollback.

    If `commit` is not called, all modifications are undone upon exiting the context,
    regardless of whether an exception is raised.

    Note: The isolation level is expected to be serializable for maximum data integrity and program simplicity.
    If performance issues arise due to this high isolation level in future use cases,
    consider exposing a setting in this class to allow adjustment of the isolation level.
    """

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.rollback()

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass
