"""Exceptions for the AST translator."""

import typing as ty
from pathlib import Path

from openqasm.ast import Span


class UnsupportedFeature(Exception):
    """Exception raised when a unsupported feature is encountered."""

    def __init__(self, feature_name: str, reason: ty.Optional[str] = None):
        """
        Initialise the exception.

        :param feature_name: name of the unsupported feature encountered.
        :param reason: if given, will be appended to the exception message on a
            new line. Can be used to provide more information.
        """
        message = f"Feature '{feature_name}' is currently not supported."
        if reason is not None:
            message += "\n" + reason
        super().__init__(message)


class UnsupportedExpressionType(Exception):
    """Exception raised when a unsupported expression type is encountered."""

    def __init__(self, expression_type_name: str):
        """
        Initialise the exception.

        :param expression_type_name: name of the unsupported expression type
            encountered.
        """
        message = f"Expressions of type '{expression_type_name}' are currently not supported."
        super().__init__(message)


class UndefinedSymbol(Exception):
    """Exception raised when the value of an undefined symbol is needed."""

    def __init__(self, identifier: str, current_location: ty.Optional[Span]):
        """
        Initialise the exception.

        :param identifier: identifier of the undefined symbol.
        :param current_location: actual location in the source OpenQASM file.
        """
        message = f"Symbol '{identifier}' has not been declared before first usage."
        if current_location:
            message = f"[{current_location.start_line}:{current_location.start_column}] {message}"
        super().__init__(message)


class UnknownConstant(Exception):
    """Exception raised when a unknown constant is found."""

    def __init__(self, identifier: str, known_constants: ty.List[str] = None):
        """
        Initialise the exception.

        :param identifier: identifier of the unknown constant.
        """
        message = f"Constant '{identifier}' value is unknown."
        if known_constants:
            message += "\nKnown constants are: " + ", ".join(known_constants)
        super().__init__(message)


class UninitializedSymbol(Exception):
    """Exception raised when the value of an unintialized symbol is needed."""

    def __init__(
        self,
        identifier: str,
        definition_location: ty.Optional[Span],
        current_location: ty.Optional[Span],
    ):
        """
        Initialise the exception.

        :param identifier: identifier of the unintialized symbol.
        :param definition_location: place where the symbol has been defined in
            the OpenQASM source file.
        :param current_location: actual location in the source OpenQASM file.
        """
        message = f"Symbol '{identifier}' has been declared but never initialized."
        if current_location:
            message = f"[{current_location.start_line}:{current_location.start_column}] {message}"
        if definition_location:
            message += f" Symbol was defined at line {definition_location.start_line} and column {definition_location.start_column}."
        super().__init__(message)


class MissingExpression(Exception):
    """Exception raised when an expression was expected an not found."""

    def __init__(self, context: str):
        """Initialise the exception."""
        message = f"Missing expression in '{context}'."
        super().__init__(message)


class WrongRange(Exception):
    """Exception raised when a range is missing some mandatory values."""

    def __init__(self, missing_part: str, location: ty.Optional[Span]):
        message = f"Range is missing the mandatory value {missing_part}."
        if location:
            message = f"[{location.start_line}:{location.start_column}] {message}"
        super().__init__(message)


class InvalidIncludePath(Exception):
    """Exception raised when a file is not present in any of the include paths"""

    def __init__(self, file_name: str, include_paths: ty.Optional[ty.List[Path]] = None):
        message = f"File '{file_name}' not found in any of the provided include directories."
        if include_paths:
            message += f"\nProvided include paths:\n\t- " + "\n\t- ".join(map(str, include_paths))
        super().__init__(message)


class ClassicalTypeOverflow(Exception):
    """Exception raised when there is an integer overflow"""

    def __init__(self, identifier: str, location: ty.Optional[Span]):
        message = f"Integer overflow occured for '{identifier}'."
        if location:
            message = f"[{location.start_line}:{location.start_column}] {message}"
        super().__init__(message)

class InvalidOperation(Exception):
    """Exception raised when an operation is not implemented between two types."""
    def __init__(self, op: str, typevar1: ty.Any, typevar2: ty.Any):
        message = f"Operation '{op}' is invalid for types '{type(typevar1).__name__}[{typevar1.size}]' and '{type(typevar2).__name__}"
        super().__init__(message)

class InvalidTypeAssignment(Exception):
    """Exception raised when a RHS of wrong type is assigned to LHS."""
    def __init__(self, typevar1: ty.Any, typevar2: ty.Any):
        message = f"The type `{type(typevar1).__name__}` cannot be assigned to type `{type(typevar2).__name__}` without explicit type casting."
        super().__init__(message)
