from abc import ABC, abstractmethod


class RepositorySession(ABC):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    @abstractmethod
    def commit(self):
        pass
