import typing as ty

from openqasm.ast import (Concatenation, Identifier, IndexIdentifier,
                          RangeDefinition, Selection, Slice, Subscript)
from openqasm.translator.context import OpenQASMContext
from openqasm.translator.exceptions import UnsupportedFeature
from openqasm.translator.expressions import compute_expression


class _IdentifierRetrieverNamespace:
    @staticmethod
    def get_Identifier(identifier: Identifier, context: OpenQASMContext) -> ty.Any:
        return context.lookup(identifier.name, identifier.span)

    @staticmethod
    def get_Subscript(identifier: Subscript, context: OpenQASMContext) -> ty.Any:
        index: int = compute_expression(identifier.index, context)
        return context.lookup(identifier.name, identifier.span)[index]

    @staticmethod
    def get_Selection(identifier: Selection, context: OpenQASMContext) -> ty.List:
        indices: ty.List[int] = [compute_expression(expr, context) for expr in identifier.indices]
        obj = context.lookup(identifier.name, identifier.span)
        return [obj[i] for i in indices]

    @staticmethod
    def get_Slice(identifier: Slice, context: OpenQASMContext) -> ty.List:
        rdef: RangeDefinition = identifier.range
        obj = context.lookup(identifier.name, identifier.span)
        # Default values if not provided
        start, end, step = 0, len(obj), 1
        if rdef.start is not None:
            start = compute_expression(rdef.start, context)
        if rdef.end is not None:
            end = compute_expression(rdef.end, context)
        if rdef.step is not None:
            step = compute_expression(rdef.step, context)
        return [obj[i] for i in range(start, end, step)]

    @staticmethod
    def get_Concatenation(identifier: Concatenation, context: OpenQASMContext) -> ty.List:
        lhs = get_identifier(identifier.lhs, context)
        rhs = get_identifier(identifier.rhs, context)
        # Making sure we have lists
        if not isinstance(lhs, list):
            lhs = [lhs]
        if not isinstance(rhs, list):
            rhs = [rhs]
        return lhs + rhs


def get_identifier(
    identifier: ty.Union[Identifier, IndexIdentifier], context: OpenQASMContext
) -> ty.List:
    method_name: str = "get_" + type(identifier).__name__
    if not hasattr(_IdentifierRetrieverNamespace, method_name):
        raise UnsupportedFeature(
            type(identifier).__name__, "Identifier or IndexIdentifier type not supported."
        )
    return getattr(_IdentifierRetrieverNamespace, method_name)(identifier, context)
