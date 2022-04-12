import math
import operator
import typing as ty

from openqasm.ast_qasm3 import (AssignmentOperator, BinaryExpression, BooleanLiteral,
                          Cast, Constant, DurationLiteral, Expression,
                          FunctionCall, Identifier, IndexExpression,
                          IntegerLiteral, RealLiteral, StringLiteral,
                          Subscript, UnaryExpression)
from openqasm.translator.context import OpenQASMContext
from openqasm.translator.exceptions import (UnknownConstant,
                                            UnsupportedExpressionType)
from openqasm.translator.types import ClassicalType, get_typecast

__all__ = ["compute_expression"]

_CONSTANT_VALUES: ty.Dict[str, float] = {
    "pi": math.pi,
    "π": math.pi,
    "tau": math.tau,
    "𝜏": math.tau,
    "euler": math.e,
    "ℇ": math.e,
}


class _ComputeExpressionNamespace:

    _BINARY_FUNCTIONS = {
        ">": operator.__gt__,
        "<": operator.__lt__,
        ">=": operator.__ge__,
        "<=": operator.__le__,
        "==": operator.__eq__,
        "!=": operator.__ne__,
        "&&": None,
        "||": None,
        "|": operator.__or__,
        "^": operator.__xor__,
        "&": operator.__and__,
        "<<": operator.__lshift__,
        ">>": operator.__rshift__,
        "+": operator.__add__,
        "-": operator.__sub__,
        "*": operator.__mul__,
        "/": operator.__truediv__,
        "%": operator.__mod__,
        "**": operator.__pow__,
    }
    _UNARY_FUNCTIONS = {"-": operator.__neg__, "~": operator.__inv__, "!": operator.__not__}

    @staticmethod
    def compute_BinaryExpression(expr: BinaryExpression, context: OpenQASMContext) -> ty.Any:
        lhs = _ComputeExpressionNamespace.compute_Expression(expr.lhs, context)
        rhs = _ComputeExpressionNamespace.compute_Expression(expr.rhs, context)
        return _ComputeExpressionNamespace._BINARY_FUNCTIONS[expr.op.name](lhs, rhs)

    @staticmethod
    def compute_UnaryExpression(expr: UnaryExpression, context: OpenQASMContext) -> ty.Any:
        value = _ComputeExpressionNamespace.compute_Expression(expr.expression, context)
        return _ComputeExpressionNamespace._UNARY_FUNCTIONS[expr.op.name](value)

    @staticmethod
    def compute_Constant(expr: Constant, context: OpenQASMContext) -> ty.Any:
        name: str = expr.name.name
        if name not in _CONSTANT_VALUES:
            raise UnknownConstant(name)
        return _CONSTANT_VALUES[name]

    @staticmethod
    def compute_Identifier(expr: Identifier, context: OpenQASMContext) -> ty.Any:
        return context.lookup(expr.name, expr.span)

    @staticmethod
    def compute_IntegerLiteral(expr: IntegerLiteral, context: OpenQASMContext) -> int:
        return expr.value

    @staticmethod
    def compute_RealLiteral(expr: RealLiteral, context: OpenQASMContext) -> float:
        return expr.value

    @staticmethod
    def compute_BooleanLiteral(expr: BooleanLiteral, context: OpenQASMContext) -> bool:
        return expr.value

    @staticmethod
    def compute_StringLiteral(expr: StringLiteral, context: OpenQASMContext) -> str:
        return expr.value

    @staticmethod
    def compute_DurationLiteral(expr: DurationLiteral, context: OpenQASMContext):
        raise UnsupportedExpressionType(DurationLiteral.__name__)

    @staticmethod
    def compute_FunctionCall(expr: FunctionCall, context: OpenQASMContext):
        arguments = [
            _ComputeExpressionNamespace.compute_Expression(arg, context) for arg in expr.arguments
        ]
        return context.lookup(expr.name, expr.span)(*arguments)

    @staticmethod
    def compute_IndexExpression(expr: IndexExpression, context: OpenQASMContext) -> ty.Any:
        index: int = _ComputeExpressionNamespace.compute_Expression(expr.index_expression, context)
        return _ComputeExpressionNamespace.compute_Expression(expr.expression, context)[index]

    @staticmethod
    def compute_Cast(expr: Cast, context: OpenQASMContext) -> ty.Any:
        type_ = expr.type
        # TODO: Enable multiple arguments in cast. Right now limited to only one
        cast_arg = _ComputeExpressionNamespace.compute_Expression(expr.arguments[0], context)
        typecasted_identifer = get_typecast(type_, cast_arg)
        return typecasted_identifer

    @staticmethod
    def compute_Expression(expr: Expression, context: OpenQASMContext) -> ty.Any:
        """Compute a generic expression."""
        method_name: str = f"compute_{type(expr).__name__}"
        if not hasattr(_ComputeExpressionNamespace, method_name):
            raise UnsupportedExpressionType(type(expr).__name__)
        return getattr(_ComputeExpressionNamespace, method_name)(expr, context)


compute_expression = _ComputeExpressionNamespace.compute_Expression


class _ComputeAssignmentExpressionNamespace:

    _FUNCTIONS = {
        "|=": operator.__or__,
        "^=": operator.__xor__,
        "&=": operator.__and__,
        "<<=": operator.__lshift__,
        ">>=": operator.__rshift__,
        "+=": operator.__add__,
        "-=": operator.__sub__,
        "*=": operator.__mul__,
        "/=": operator.__truediv__,
        "%=": operator.__mod__,
    }

    @staticmethod
    def compute_Assignment(
        lhs: ty.Union[Identifier, Subscript],
        op: AssignmentOperator,
        rhs: ty.Any,
        context: OpenQASMContext,
    ) -> None:
        if op.name == "=":
            context.assign_value_symbol(lhs.name, rhs, lhs.span)
        else:
            lhs_identifier = context.lookup(lhs.name)
            if isinstance(lhs_identifier, float):
                if isinstance(rhs, float):
                    result = _ComputeAssignmentExpressionNamespace._FUNCTIONS[op.name](
                        lhs_identifier, rhs
                    )
                elif isinstance(rhs, ClassicalType):
                    result = _ComputeAssignmentExpressionNamespace._FUNCTIONS[op.name](
                        lhs_identifier, rhs._value
                    )
            elif isinstance(lhs_identifier, ClassicalType):
                if isinstance(rhs, float):
                    result = _ComputeAssignmentExpressionNamespace._FUNCTIONS[op.name](
                        lhs_identifier._value, rhs
                    )
                elif isinstance(rhs, ClassicalType):
                    result = _ComputeAssignmentExpressionNamespace._FUNCTIONS[op.name](
                        lhs_identifier._value, rhs._value
                    )
            context.assign_value_symbol(lhs.name, result, lhs.span)


compute_assignment = _ComputeAssignmentExpressionNamespace.compute_Assignment
