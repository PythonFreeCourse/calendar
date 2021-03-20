"""Shared code for CRUD tests."""
from collections import Callable
from types import ModuleType
from typing import Optional


def get_getter_function(
    crud: ModuleType,
    column_name: str,
) -> Optional[Callable]:
    """Returns a get function from a CRUD module.

    Args:
        crud: A CRUD module.
        column_name: The column to get the function for.

    Returns:
        A get function for an object's column.
    """
    try:
        return getattr(crud, f"get_{column_name}")
    except AttributeError:
        return None


def get_boolean_getter_function(
    crud: ModuleType,
    column_name: str,
) -> Callable:
    """Returns a get function from a CRUD module for a boolean field.

    Args:
        crud: A CRUD module.
        column_name: The column to get the function for.

    Returns:
        A get function for an object's boolean column.
    """
    return getattr(crud, f"is_{column_name}")


def get_setter_function(crud: ModuleType, column_name: str) -> Callable:
    """Returns a set function from a CRUD module.

    Args:
        crud: A CRUD module.
        column_name: The column to get the function for.

    Returns:
        A set function for an object's column.
    """
    return getattr(crud, f"set_{column_name}")
