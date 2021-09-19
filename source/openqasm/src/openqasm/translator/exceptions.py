"""Exceptions for the AST translator."""

import typing as ty


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

    def __init__(self, identifier: str):
        """
        Initialise the exception.

        :param identifier: identifier of the undefined symbol.
        """
        message = f"Symbol '{identifier}' has not been declared before first usage."
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

    def __init__(self, identifier: str):
        """
        Initialise the exception.

        :param identifier: identifier of the unintialized symbol.
        """
        message = f"Symbol '{identifier}' has been declared but never initialized."
        super().__init__(message)


class MissingExpression(Exception):
    """Exception raised when an expression was expected an not found."""

    def __init__(self, context: str):
        """Initialise the exception."""
        message = f"Missing expression in '{context}'."
        super().__init__(message)
