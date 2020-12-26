from typing import Generic, TypeVar

# Specifies that T can be anything
T = TypeVar("T")


class Optional(Generic[T]):
    """An object that either contains something or nothing"""

    @staticmethod
    def empty():
        return Optional(None)

    def __init__(self, value: T):
        self.value = value

    def get(self) -> T:
        if self.value is None:
            raise ValueError("Called get() on empty optional ya dum-dum!")

        return self.value

    def is_empty(self) -> bool:
        return self.value is None

    def is_present(self) -> bool:
        return self.value is not None
