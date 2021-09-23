import typing as ty
import openqasm.ast as ast

class ClassicalType:
    """Base class for all classical types"""
    def __init__(self, size: int):
        self._size: int = size

    @property
    def size(self) -> int:
        return self._size

class ContantType(ClassicalType):
    pass

class BitType(ClassicalType):
    pass

class BitArrayType(BitType):
    pass

class BooleanType(ClassicalType):
    pass

class BooleanArrayType(BooleanType):
    pass

class IntegerType(ClassicalType):
    pass

class SignedIntegerType(IntegerType):
    pass

class UnsignedIntegerType(IntegerType):
    pass

class FloatType(ClassicalType):
    pass

class FixedType(ClassicalType):
    pass

def get_type(type_: ast.ClassicalType):
    pass
