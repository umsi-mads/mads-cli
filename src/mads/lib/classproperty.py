"""Extend built-in python functionality"""

from typing import Callable, TypeVar


class classproperty(property):
    """
    A decorator for class-level properties.
    https://stackoverflow.com/a/13624858/1893290
    """

    # fget: Callable
    # fset: Callable

    def __get__(self, _, owner_cls):
        return self.fget(owner_cls)

    def __set__(self, owner_cls, value):
        self.fset(owner_cls, value)
