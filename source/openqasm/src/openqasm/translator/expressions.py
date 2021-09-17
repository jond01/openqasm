import math
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
    @staticmethod
    def compute_BinaryExpression(expr: BinaryExpression, context: OpenQASMContext) -> ty.Any:
        lhs = _ComputeExpressionNamespace.compute_Expression(expr.lhs, context)
        rhs = _ComputeExpressionNamespace.compute_Expression(expr.rhs, context)
        return eval(f"{lhs} {expr.op} {rhs}")

    @staticmethod
    def compute_UnaryExpression(expr: UnaryExpression, context: OpenQASMContext) -> ty.Any:
        value = _ComputeExpressionNamespace.compute_Expression(expr.expression, context)
        return eval(f"{expr.op} {value}")

    @staticmethod
    def compute_Constant(expr: Constant, context: OpenQASMContext) -> ty.Any:
        if expr.name not in _CONSTANT_VALUES:
            raise UnknownConstant(expr.name.name)
        return _CONSTANT_VALUES[expr.name.name]

    @staticmethod
    def compute_Identifier(expr: Identifier, context: OpenQASMContext) -> ty.Any:
        return context.lookup(expr.name)

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
        return context.lookup(expr.name)(*arguments)

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
