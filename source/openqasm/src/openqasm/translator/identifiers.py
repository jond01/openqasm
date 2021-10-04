import typing as ty

from qiskit.circuit.classicalregister import \
    ClassicalRegister as qiskit_ClassicalRegister

from openqasm.ast import (Concatenation, Identifier, IndexIdentifier,
                          RangeDefinition, Selection, Slice, Subscript)
from openqasm.translator.context import OpenQASMContext
from openqasm.translator.exceptions import UnsupportedFeature
from openqasm.translator.expressions import compute_expression
from openqasm.translator.types import BitArrayType, ClassicalType


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
        return obj[indices]

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
        return obj[slice(start=start, stop=end, step=step)]

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


# TODO: Do we still require this?
# def get_register(
#         identifier: ty.Union[Identifier, IndexIdentifier], context: OpenQASMContext
# ) -> qiskit_ClassicalRegister:
#     iden_value = context.lookup(identifier.name, identifier.span)
#     if isinstance(iden_value, BitArrayType):
#         return iden_value.register
#
#     context.modify_symbol(identifier.name, BitArrayType.cast(iden_value), identifier.span)
#     new_iden_value = context.lookup(identifier.name, identifier.span)
#     return new_iden_value.register


def get_identifier(
    identifier: ty.Union[Identifier, IndexIdentifier], context: OpenQASMContext
) -> ty.List:
    method_name: str = "get_" + type(identifier).__name__
    if not hasattr(_IdentifierRetrieverNamespace, method_name):
        raise UnsupportedFeature(
            type(identifier).__name__, "Identifier or IndexIdentifier type not supported."
        )
    return getattr(_IdentifierRetrieverNamespace, method_name)(identifier, context)
