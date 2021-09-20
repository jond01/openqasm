import math
import operator
import typing as ty

from openqasm.ast import (BinaryExpression, BooleanLiteral, Constant,
                          DurationLiteral, Expression, FunctionCall,
                          Identifier, IndexExpression, IntegerLiteral,
                          RealLiteral, StringLiteral, UnaryExpression)
from openqasm.translator.context import OpenQASMContext
from openqasm.translator.exceptions import (UnknownConstant,
                                            UnsupportedExpressionType)

__all__ = ["compute_expression"]

_CONSTANT_VALUES: ty.Dict[str, float] = {
    "pi": math.pi,
    "π": math.pi,
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
    def compute_Expression(expr: Expression, context: OpenQASMContext) -> ty.Any:
        """Compute a generic expression."""
        method_name: str = f"compute_{type(expr).__name__}"
        if not hasattr(_ComputeExpressionNamespace, method_name):
            raise UnsupportedExpressionType(type(expr).__name__)
        return getattr(_ComputeExpressionNamespace, method_name)(expr, context)


compute_expression = _ComputeExpressionNamespace.compute_Expression
