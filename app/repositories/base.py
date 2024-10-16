from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Callable, Generic, TypeVar


Operator = TypeVar("Operator")


class RepositorySession(ABC, Generic[Operator]):
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
    """

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.rollback()

    @abstractmethod
    def new_operator(self) -> Operator:
        """
        Return a new instance of Operator that is used for database interactions within the repository.

        This method can be passed to the constructor of a class implementing AbstractRepository.

        This setup allows AbstractRepository to utilize the specific Operator for executing database operations,
        while separating the concerns of transaction management (committing and rolling back) which are handled
        by the RepositorySession class.
        """
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass


class AbstractRepository(ABC, Generic[Operator]):
    def __init__(self, new_operator: Callable[[], Operator]):
        """
        Args:
           new_operator (Callable[[], Operator]): A factory method that returns an instance of Operator.
                This callable is expected to be provided by an implementation of the RepositorySession class.
                Also see the comment of new_operator in the RepositorySession class.
        """
        self.new_operator = new_operator


class LockLevel(Enum):
    NONE = auto()
    MODIFY_LOCK = (
        auto()
    )  # If a transaction have acquired data with this lock level, no other transaction can acquire the same lock or modify the locked data until the original transaction has finished.
