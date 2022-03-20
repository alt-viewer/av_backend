from abc import ABC, abstractmethod


class HasInventory(ABC):
    @abstractmethod
    def __str__(self) -> str:
        """Should show a summary of the items rather than the full list"""
        raise NotImplementedError()

    @abstractmethod
    def __repr__(self) -> str:
        """Should show the items"""
        raise NotImplementedError()

    @abstractmethod
    def _hide_items(self) -> str:
        """Should convert the items to a summary."""
        raise NotImplementedError()
