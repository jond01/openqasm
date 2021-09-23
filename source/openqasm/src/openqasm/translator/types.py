# import typing as ty
import math
from qiskit.circuit.classicalregister import ClassicalRegister
import openqasm.ast as qasm_ast

class ClassicalType:
    """Base class for all classical types"""
    def __init__(self, size: int):
        self._size: int = size

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        self._size = value

class UnsignedIntegerType(ClassicalType):
    def __init__(self, size: int, value: int):
        super().__init__(size)
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        if value > ((2**self._size)-1):
            raise OverflowError(f"Not enough bits in the `uint[{self._size}]` type to store result.")
        if value < 0:
            raise ValueError(f"Cannot store negative result value in `uint[{self._size}]` type.")
        self._value = value

    def __getitem__(self, subscript):
        if isinstance(subscript, int):
            if subscript in range(-self._size, self._size):
                res = (self._value & (0x1 << subscript)) >> subscript
                return UnsignedIntegerType(1, int(res))
            # TODO: Think of providing some error localization and variable name here
            raise IndexError(f"Index value '{subscript}' is out of range.")

        elif isinstance(subscript, slice):
            bit_str = str(bin(self._value)).zfill(self._size)
            if subscript.start is None and subscript.stop is None:
                return self._value

            res = bit_str[::-1][subscript][::-1]
            res_len = math.fabs(subscript.stop - subscript.start)
            return UnsignedIntegerType(res_len, int(res, 2))

        else:
            # TODO: Think of providing some error localization and variable name here
            raise TypeError(f"Expected 'int/uint' or 'slice' in subscript, found '{type(subscript)}'.")

    def __setitem__(self, subscript, value: int) -> None:
        if value > 1:
            # TODO: Think of providing some error localization and variable name here
            raise ValueError("Expected one-bit value, found more than one.")

        if value < 0:
            raise ValueError(f"Expected non-negative value, found '{value}'.")

        if isinstance(subscript, int):
            if subscript in range(-self._size, self._size):
                prev_bit = ((self._value & (0x1 << subscript)) >> subscript)
                same_or_not = prev_bit ^ value
                self._value ^= (same_or_not << subscript)
            else:
                # TODO: Think of providing some error localization and variable name here
                raise IndexError(f"Index value '{subscript}' is out of range.")

        else:
            # TODO: Think of providing some error localization and variable name here
            raise TypeError(f"Expected type 'int/uint' for subscript, found '{type(subscript)}'.")

        if self._value > ((2**self._size)-1):
            raise OverflowError(f"Overflow occured for `uint[{self._size}]` type.")

    def __add__(self, other: int) -> int:
        return int(self._value + other)

    def __sub__(self, other: int) -> int:
        return int(self._value - other)

    def __mul__(self, other: int) -> int:
        return int(self._value * other)

    def __truediv__(self, other: int) -> int:
        return int(self._value / other)

    def __and__(self, other: int) -> int:
        return int(self._value & other)

    def __or__(self, other: int) -> int:
        return int(self._value | other)

    def __xor__(self, other: int) -> int:
        return int(self._value ^ other)

    def __mod__(self, other: int) -> int:
        return int(self._value % other)

    def __pow__(self, other: int) -> int:
        return int(self._value ** other)

    def __lshift__(self, other: int) -> int:
        return int(self._value << other)

    def __rshift__(self, other: int) -> int:
        return int(self._value >> other)

    def __neg__(self) -> int:
        return int(-self._value)

    def __inv__(self) -> int:
        return int(~self._value)

    def __eq__(self, other: int) -> bool:
        return self._value == other

    def __ne__(self, other: int) -> bool:
        return self._value != other

    def __ge__(self, other: int) -> bool:
        return self._value >= other

    def __le__(self, other: int) -> bool:
        return self._value <= other

    def __gt__(self, other: int) -> bool:
        return self._value > other

    def __lt__(self, other: int) -> bool:
        return self._value < other

    def __repr__(self) -> str:
        return str(self._value)

class BitArrayType(UnsignedIntegerType):
    def __init__(self, size: int, value: str, name: str):
        if size != len(value):
            raise ValueError(f"Size of `bit[{size}]` not equal to length of assigned value {value!r}.")
        super().__init__(size, int(value, 2))
        self._register = ClassicalRegister(size=size, name=name)
        self._name = name

    @property
    def register(self) -> ClassicalRegister:
        return self._register

    @register.setter
    def register(self, creg: ClassicalRegister) -> None:
        self._register = creg

    @property
    def value(self) -> str:
        return str(bin(self._value)).zfill(self._size)

    @value.setter
    def value(self, value: str) -> None:
        int_value = int(value, 2)
        super().value(int_value)

    def __getitem__(self, subscript):
        item = super().__getitem__(subscript)
        if isinstance(subscript, int):
            bit_str = str(item)
            return BitArrayType(len(bit_str), bit_str, (self._name+f'[{subscript}]'))

        if isinstance(subscript, slice):
            str_len = math.fabs(subscript.stop - subscript.start)
            bit_str = str(bin(item)).zfill(str_len)
            return BitArrayType(len(bit_str), bit_str, (self._name+f'[{subscript.start}:{subscript.stop}:{subscript.step}]'))

        # TODO: Think of providing some error localization and variable name here
        raise TypeError(f"Expected 'int/uint' or 'slice' in subscript, found '{type(subscript)}'.")

    def __setitem__(self, subscript, value: str) -> None:
        super().__setitem__(subscript, int(value, 2))

    def __repr__(self) -> str:
        return str(bin(self._value)).zfill(self._size)

class SignedIntegerType(ClassicalType):
    pass

class AngleType(ClassicalType):
    pass

class FixedType(ClassicalType):
    pass

def get_type(type_: qasm_ast.ClassicalType):
    pass
