import typing as ty
import math
from qiskit.circuit.classicalregister import ClassicalRegister
from openqasm.translator.exceptions import InvalidOperation, InvalidTypeAssignment
import openqasm.ast as qasm_ast

class ClassicalType:
    """Base class for all classical types"""
    def __init__(self, size: int, value: int):
        self._size: int = size
        self._value: int = value

    @property
    def size(self) -> int:
        return self._size

    # TODO: Should we allow changing the size?
    @size.setter
    def size(self, value: int) -> None:
        self._size = value

    def __repr__(self) -> str:
        return f"<{type(self).__name__}[{self._size}]: {self._value}>"

    def __str__(self) -> str:
        return f"<{type(self).__name__}[{self._size}]: {self._value}>"

class SignedIntegerType(ClassicalType):
    """Class for unsigned integer type
        int[16] foo;
        int[24] bar;
        int[32] baz;
    """
    def __init__(self, size: int, value: int):
        if value not in range(-(0x1 << (size-1)), (0x1 << (size-1))):
            raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{size}]` type to store result.")
        super().__init__(size, value)

    @staticmethod
    def _get_type_size(var: ty.Any) -> int:
        if isinstance(var, int):
            return len(bin(var)[2:]) if var > 0 else len(bin(var)[3:])+1

        if isinstance(var, float):
            return len(bin(int(var))[2:]) if var > 0 else len(bin(int(var))[3:])+1

    @staticmethod
    def coerce(size: int, var: ty.Any):
        if isinstance(var, (int, float)):
            result = int(var)
            if result not in range(-(0x1 << (size-1)), (0x1 << (size-1))):
                raise OverflowError(f"Not enough bits in the `qasm_int[{size}]` type to store result.")
            return result

        if isinstance(var, SignedIntegerType):
            if var.size > size:
                raise OverflowError(f"Not enough bits in the `qasm_int[{size}]` type to store result.")
            return var.value

        if isinstance(var, BitArrayType):
            if var.size == size:
                return int(var.value, 2) - (0x1 << size)
            if var.size < size:
                return int(var.value, 2)

            raise OverflowError(f"Not enough bits in the `qasm_int[{size}]` type to store result.")

        if isinstance(var, (UnsignedIntegerType, AngleType)):
            if var.size == size:
                new_value = var.value if var.value < (0x1 << (size-1)) else (var.value - (0x1 << size))
                return new_value
            if var.size < size:
                return var.value

            raise OverflowError(f"Not enough bits in the `qasm_int[{size}]` type to store result.")

        raise TypeError(f"Invalid operation 'coercion' for types `qasm_int[{size}]` and '{type(var).__name__}'")

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, rhs: ty.Any) -> None:
        if isinstance(rhs, int):
            if rhs not in range(-(0x1 << (self._size-1)), (0x1 << (self._size-1))):
                raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")
            self._value = rhs

        elif isinstance(rhs, SignedIntegerType):
            if rhs.size > self._size:
                raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")
            self._value = rhs.value

        elif isinstance(rhs, (UnsignedIntegerType, BitArrayType, AngleType)):
            raise InvalidTypeAssignment(rhs, self)

        else:
            raise TypeError(f"Cannot store '{type(rhs).__name__}' type value in `{type(self).__name__}[{self._size}]` type.")

    def __getitem__(self, subscript):
        if isinstance(subscript, int):
            if subscript in range(-self._size+1, self._size-1):
                result = (self._value & (0x1 << subscript)) >> subscript
                return SignedIntegerType(2, int(result))
            # TODO: Think of providing some error localization and variable name here
            raise IndexError(f"Index value '{subscript}' is out of range.")

        elif isinstance(subscript, slice):
            bit_str = f"{self._value:b}".zfill(self._size)
            result = bit_str[::-1][subscript][::-1]
            return SignedIntegerType(len(result)+1, int(result, 2))

        else:
            # TODO: Think of providing some error localization and variable name here
            raise TypeError(f"Expected 'int/uint' or 'slice' in subscript, found '{type(subscript)}'.")

    def __setitem__(self, subscript, rhs: ty.Any) -> None:
        if isinstance(rhs, int):
            if rhs not in range(0, 2):
                # TODO: Think of providing some error localization and variable name here
                raise ValueError(f"Expected one-bit value, found '{str(bin(rhs))}'.")
            set_value = rhs

        elif isinstance(rhs, SignedIntegerType):
            if rhs.size != 2:
                # TODO: Think of providing some error localization and variable name here
                raise ValueError(f"Expected one-bit value, found '{str(bin(rhs.value))[:2]+str(bin(rhs.value))[3:]}'.")
            rhs_lsb = rhs.value & 0x01
            set_value = rhs_lsb

        elif isinstance(rhs, (UnsignedIntegerType, BitArrayType)):
            if rhs.size != 1:
                # TODO: Think of providing some error localization and variable name here
                raise ValueError(f"Expected one-bit value, found '{str(bin(rhs.value))[:2]+str(bin(rhs.value))[3:]}'.")
            set_value = rhs.value

        # TODO: Not sure what to do of this one
        # Should it be invalid coercion
        # or just coerce into corresponding bits?
        elif isinstance(rhs, AngleType):
            pass

        else:
            raise InvalidOperation("__setitem__", self, rhs)

        if isinstance(subscript, int):
            if subscript in range(-self._size, self._size):
                prev_bit = ((self._value & (0x1 << subscript)) >> subscript)
                same_or_not = prev_bit ^ set_value
                self._value ^= (same_or_not << subscript)
            else:
                # TODO: Think of providing some error localization and variable name here
                raise IndexError(f"Index value '{subscript}' is out of range.")

        else:
            # TODO: Think of providing some error localization and variable name here
            raise TypeError(f"Expected type 'int/uint' for subscript, found '{type(subscript)}'.")

        if self._value not in range(-(0x1 << (self._size-1)), (0x1 << (self._size-1))):
            raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")

    # TODO: Maybe I can use existing code in `expressions.py`?!
    def __add__(self, other: ty.Any):
        if isinstance(other, int):
            return SignedIntegerType(self._size, int(self._value + other))

        if isinstance(other, float):
            return float(self._value + other)

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            return SignedIntegerType(self._size, int(self._value + other._value))

        raise InvalidOperation("+", self, other)

    def __sub__(self, other: ty.Any):
        if isinstance(other, int):
            return SignedIntegerType(self._size, int(self._value - other))

        if isinstance(other, float):
            return float(self._value - other)

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            return SignedIntegerType(self._size, int(self._value - other._value))

        raise InvalidOperation("-", self, other)

    def __mul__(self, other: ty.Any):
        if isinstance(other, int):
            return SignedIntegerType(self._size, int(self._value * other))

        if isinstance(other, float):
            return float(self._value * other)

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            return SignedIntegerType(self._size, int(self._value * other._value))

        raise InvalidOperation("*", self, other)

    def __truediv__(self, other: ty.Any):
        if isinstance(other, int):
            return SignedIntegerType(self._size, int(self._value / other))

        if isinstance(other, float):
            return float(self._value / other)

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            return SignedIntegerType(self._size, int(self._value / other._value))

        raise InvalidOperation("/", self, other)

    def __and__(self, other: ty.Any):
        if isinstance(other, int):
            return SignedIntegerType(self._size, int(self._value & other))

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            return SignedIntegerType(self._size, int(self._value & other._value))

        raise InvalidOperation("&", self, other)

    def __or__(self, other: ty.Any):
        if isinstance(other, int):
            return SignedIntegerType(self._size, int(self._value | other))

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            return SignedIntegerType(self._size, int(self._value | other._value))

        raise InvalidOperation("|", self, other)

    def __xor__(self, other: ty.Any):
        if isinstance(other, int):
            return SignedIntegerType(self._size, int(self._value ^ other))

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            return SignedIntegerType(self._size, int(self._value ^ other._value))

        raise InvalidOperation("^", self, other)

    def __mod__(self, other: ty.Any):
        if isinstance(other, int):
            return SignedIntegerType(self._size, int(self._value % other))

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            return SignedIntegerType(self._size, int(self._value % other._value))

        raise InvalidOperation("%", self, other)

    def __pow__(self, other: ty.Any):
        if isinstance(other, (int, float)):
            return SignedIntegerType(self._size, int(self._value ** other))

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            return SignedIntegerType(self._size, int(self._value ** other._value))

        raise InvalidOperation("**", self, other)

    def __lshift__(self, other: ty.Any):
        if isinstance(other, int):
            return SignedIntegerType(self._size, int((self._value << other) % 2**(self._size-1)))

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType)):
            return SignedIntegerType(self._size, int((self._value << other._value) % 2**(self._size-1)))

        if isinstance(other, SignedIntegerType):
            if other.value < 0:
                raise ValueError("Negative shift value not allowed for `<<`.")
            return SignedIntegerType(self._size, int((self._value << other.value) % 2**(self._size-1)))

        raise InvalidOperation("<<", self, other)

    def __rshift__(self, other: ty.Any):
        if isinstance(other, int):
            return SignedIntegerType(self._size, int(self._value >> other))

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType)):
            return SignedIntegerType(self._size, int(self._value >> other._value))

        if isinstance(other, SignedIntegerType):
            if other.value < 0:
                raise ValueError("Negative shift value not allowed for `>>`.")
            return SignedIntegerType(self._size, int(self._value >> other.value))

        raise InvalidOperation(">>", self, other)

    def __neg__(self):
        return SignedIntegerType(self._size, int(-self._value))

    def __inv__(self):
        return SignedIntegerType(self._size, int(~self._value))

    def __eq__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value == other

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            if self._size == other.size:
                return self._value == other._value
            return False

        raise InvalidOperation("==", self, other)

    def __ne__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value != other

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            if self._size != other.size:
                return self._value != other._value
            return False

        raise InvalidOperation("!=", self, other)

    def __ge__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value >= other

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            return self._value >= other._value

        raise InvalidOperation(">=", self, other)

    def __le__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value <= other

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            return self._value <= other._value

        raise InvalidOperation("<=", self, other)

    def __gt__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value > other

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            return self._value > other._value

        raise InvalidOperation(">", self, other)

    def __lt__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value < other

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            return self._value < other._value

        raise InvalidOperation("<", self, other)

SignedIntegerType.__name__ = "qasm_int"


class UnsignedIntegerType(ClassicalType):
    """Class for unsigned integer type
        uint[16] foo;
        uint[24] bar;
        uint[32] baz;
    """
    def __init__(self, size: int, value: int):
        if value > ((2**size)-1):
            raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{size}]` type to store result.")
        if value < 0:
            raise ValueError(f"Cannot store negative value in `{type(self).__name__}[{size}]` type.")
        super().__init__(size, value)

    @staticmethod
    def _get_type_size(var: ty.Any) -> int:
        if isinstance(var, int):
            return len(bin(var)[2:])

        if isinstance(var, float):
            return len(bin(int(var))[2:])+1

    def _get_ret_type(self, res: int):
        if isinstance(self, AngleType):
            print('Hello')
            return AngleType(self.size, res)
        if isinstance(self, BitArrayType):
            return BitArrayType(self.size, f"{res}".zfill(self.size))

        return UnsignedIntegerType(self.size, res)

    @staticmethod
    def coerce(size: int, var: ty.Any, err_type: ty.Optional[str]=None):
        err_type_string = err_type if err_type is not None else "qasm_uint"
        if isinstance(var, (int, float)):
            result = int(var)
            if result not in range(0, (0x1 << size)):
                raise OverflowError(f"Not enough bits in the `{err_type_string}[{size}]` type to store result.")
            return result

        if isinstance(var, SignedIntegerType):
            if var.size > size:
                raise OverflowError(f"Not enough bits in the `{err_type_string}[{size}]` type to store result.")
            new_value = var.value if var.value > 0 else (var.value + (0x1 << var.size))
            return new_value

        if isinstance(var, BitArrayType):
            if var.size > size:
                raise OverflowError(f"Not enough bits in the `{err_type_string}[{size}]` type to store result.")
            return int(var.value, 2)

        if isinstance(var, (UnsignedIntegerType, AngleType)):
            if var.size > size:
                raise OverflowError(f"Not enough bits in the `{err_type_string}[{size}]` type to store result.")
            return var.value

        raise TypeError(f"Invalid operation 'coercion' for types `{err_type_string}[{size}]` and '{type(var).__name__}'")

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, rhs: ty.Any) -> None:
        if isinstance(rhs, int):
            if rhs > ((2**self._size)-1):
                raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")
            if rhs < 0:
                raise ValueError(f"Cannot store negative value in `{type(self).__name__}[{self._size}]` type.")
            self._value = rhs

        elif isinstance(rhs, (BitArrayType, SignedIntegerType, AngleType)):
            raise InvalidTypeAssignment(rhs, self)

        elif isinstance(rhs, UnsignedIntegerType):
            if rhs.size > self._size:
                raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")
            self._value = rhs.value

        else:
            raise TypeError(f"Cannot store '{type(rhs).__name__}' type value in `{type(self).__name__}[{self._size}]` type.")

    def __getitem__(self, subscript):
        if isinstance(subscript, int):
            if subscript in range(-self._size, self._size):
                result = (self._value & (0x1 << subscript)) >> subscript
                return UnsignedIntegerType(1, int(result))
            # TODO: Think of providing some error localization and variable name here
            raise IndexError(f"Index value '{subscript}' is out of range.")

        elif isinstance(subscript, slice):
            bit_str = f"{self._value:b}".zfill(self._size)
            result = bit_str[::-1][subscript][::-1]
            return UnsignedIntegerType(len(result), int(result, 2))

        else:
            # TODO: Think of providing some error localization and variable name here
            raise TypeError(f"Expected 'int/uint' or 'slice' in subscript, found '{type(subscript)}'.")

    def __setitem__(self, subscript, rhs: ty.Any) -> None:
        if isinstance(rhs, int):
            if rhs not in range(0, 2):
                # TODO: Think of providing some error localization and variable name here
                raise ValueError(f"Expected one-bit value, found '{str(bin(rhs))}'.")
            set_value = rhs

        elif isinstance(rhs, SignedIntegerType):
            if rhs.size != 2:
                # TODO: Think of providing some error localization and variable name here
                raise ValueError(f"Expected one-bit value, found '{str(bin(rhs.value))[:2]+str(bin(rhs.value))[3:]}'.")
            rhs_lsb = rhs.value & 0x01
            set_value = rhs_lsb

        elif isinstance(rhs, (UnsignedIntegerType, BitArrayType)):
            if rhs.size != 1:
                # TODO: Think of providing some error localization and variable name here
                raise ValueError(f"Expected one-bit value, found '{str(bin(rhs.value))[:2]+str(bin(rhs.value))[3:]}'.")
            set_value = rhs.value

        # TODO: Not sure what to do of this one
        # Should it be invalid coercion
        # or just coerce into corresponding bits?
        elif isinstance(rhs, AngleType):
            pass

        else:
            raise InvalidOperation("__setitem__", self, rhs)

        if isinstance(subscript, int):
            if subscript in range(-self._size, self._size):
                prev_bit = ((self._value & (0x1 << subscript)) >> subscript)
                same_or_not = prev_bit ^ set_value
                self._value ^= (same_or_not << subscript)
            else:
                # TODO: Think of providing some error localization and variable name here
                raise IndexError(f"Index value '{subscript}' is out of range.")

        else:
            # TODO: Think of providing some error localization and variable name here
            raise TypeError(f"Expected type 'int/uint' for subscript, found '{type(subscript)}'.")

        if self._value not in range(0, (0x1 << self._size)):
            raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")

    # TODO: Maybe I can use existing code in `expressions.py`?!
    def __add__(self, other: ty.Any):
        if isinstance(other, int):
            return self._get_ret_type(int(self._value + other))

        if isinstance(other, float):
            return float(self._value + other)

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType)):
            _result = int(self._value + other._value)
            print(f"type: {type(self)}")
            return self._get_ret_type(_result)

        if isinstance(other, SignedIntegerType):
            return SignedIntegerType(self._size, int(self._value + other._value))

        raise InvalidOperation("+", self, other)

    def __sub__(self, other: ty.Any):
        if isinstance(other, int):
            return self._get_ret_type(int(self._value - other))

        if isinstance(other, float):
            return float(self._value - other)

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType)):
            _result = int(self._value - other._value)
            return self._get_ret_type(_result)

        if isinstance(other, SignedIntegerType):
            return SignedIntegerType(self._size, int(self._value - other.value))

        raise InvalidOperation("-", self, other)

    def __mul__(self, other: ty.Any):
        if isinstance(other, int):
            return self._get_ret_type(int(self._value * other))

        if isinstance(other, float):
            return float(self._value * other)

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType)):
            _result = int(self._value * other._value)
            return self._get_ret_type(_result)

        if isinstance(other, SignedIntegerType):
            return SignedIntegerType(self._size, int(self._value * other.value))

        raise InvalidOperation("*", self, other)

    def __truediv__(self, other: ty.Any):
        if isinstance(other, int):
            return self._get_ret_type(int(self._value / other))

        if isinstance(other, float):
            return float(self._value / other)

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType)):
            _result = int(self._value / other._value)
            return self._get_ret_type(_result)

        if isinstance(other, SignedIntegerType):
            return SignedIntegerType(self._size, int(self._value / other.value))

        raise InvalidOperation("/", self, other)

    def __and__(self, other: ty.Any):
        if isinstance(other, int):
            return self._get_ret_type(int(self._value & other))

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType)):
            _result = int(self._value & other._value)
            return self._get_ret_type(_result)

        if isinstance(other, SignedIntegerType):
            return SignedIntegerType(self._size, int(self._value & other.value))

        raise InvalidOperation("&", self, other)

    def __or__(self, other: ty.Any):
        if isinstance(other, int):
            return self._get_ret_type(int(self._value | other))

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType)):
            _result = int(self._value | other._value)
            return self._get_ret_type(_result)

        if isinstance(other, SignedIntegerType):
            return SignedIntegerType(self._size, int(self._value | other.value))

        raise InvalidOperation("|", self, other)

    def __xor__(self, other: ty.Any):
        if isinstance(other, int):
            return self._get_ret_type(int(self._value ^ other))

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType)):
            _result = int(self._value ^ other._value)
            return self._get_ret_type(_result)

        if isinstance(other, SignedIntegerType):
            return SignedIntegerType(self._size, int(self._value ^ other.value))

        raise InvalidOperation("^", self, other)

    def __mod__(self, other: ty.Any):
        if isinstance(other, int):
            return self._get_ret_type(int(self._value % other))

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType)):
            _result = int(self._value % other._value)
            return self._get_ret_type(_result)

        if isinstance(other, SignedIntegerType):
            return SignedIntegerType(self._size, self._value % other.value)

        raise InvalidOperation("%", self, other)

    def __pow__(self, other: ty.Any):
        if isinstance(other, (int, float)):
            return self._get_ret_type(int(self._value ** other))

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            _result = int(self._value ** other._value)
            return self._get_ret_type(_result)

        raise InvalidOperation("**", self, other)

    def __lshift__(self, other: ty.Any):
        if isinstance(other, int):
            return self._get_ret_type(int((self._value << other) % 2**self._size))

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType)):
            _result = int((self._value << other._value) % 2**self._size)
            return self._get_ret_type(_result)

        if isinstance(other, SignedIntegerType):
            if other.value < 0:
                raise ValueError("Negative shift value not allowed for `<<`.")
            _result = int((self._value << other._value) % 2**self._size)
            return self._get_ret_type(_result)

        raise InvalidOperation("<<", self, other)

    def __rshift__(self, other: ty.Any):
        if isinstance(other, int):
            return self._get_ret_type(int(self._value >> other))

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType)):
            _result = int(self._value >> other._value)
            return self._get_ret_type(_result)

        if isinstance(other, SignedIntegerType):
            if other.value < 0:
                raise ValueError("Negative shift value not allowed for `<<`.")
            _result = int(self._value >> other._value)
            return self._get_ret_type(_result)

        raise InvalidOperation(">>", self, other)

    def __neg__(self):
        return SignedIntegerType(self._size, -self._value)

    def __inv__(self):
        _result = int(~self._value)
        return self._get_ret_type(_result)

    def __eq__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value == other

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            if self._size == other.size:
                return self._value == other._value
            return False

        raise InvalidOperation("==", self, other)

    def __ne__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value != other

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            if self._size != other.size:
                return self._value != other._value
            return False

        raise InvalidOperation("!=", self, other)

    def __ge__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value >= other

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            return self._value >= other._value

        raise InvalidOperation(">=", self, other)

    def __le__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value <= other

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            return self._value <= other._value

        raise InvalidOperation("<=", self, other)

    def __gt__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value > other

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            return self._value > other._value

        raise InvalidOperation(">", self, other)

    def __lt__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value < other

        if isinstance(other, (AngleType, BitArrayType, UnsignedIntegerType, SignedIntegerType)):
            return self._value < other._value

        raise InvalidOperation("<", self, other)

UnsignedIntegerType.__name__ = "qasm_uint"


class BitArrayType(UnsignedIntegerType):
    """Class for bit array type
        bit c1; // Single bit register
        bit[3] c2; // 3-bit register
    """
    def __init__(self, size: int, value: str, name: ty.Optional[str]=None):
        if not isinstance(value, str):
            raise ValueError(f"Expected value to be of type `str`, found `{type(value)}`.")
        super().__init__(size, int(value, 2))
        self._register = ClassicalRegister(size=size)
        self._name = self._register.name if name is None else name

    @staticmethod
    def coerce(size: int, var: ty.Any):
        if isinstance(var, str):
            result = int(var, 2)
            if result not in range(0, (0x1 << size)):
                raise OverflowError(f"Not enough bits in the `qasm_uint[{size}]` type to store result.")
            return var

        coerced_val = UnsignedIntegerType.coerce(size, var, BitArrayType.__name__)
        return f"{coerced_val:b}".zfill(size)

    @property
    def register(self) -> ClassicalRegister:
        return self._register

    @register.setter
    def register(self, creg: ClassicalRegister) -> None:
        self._register = creg

    @property
    def value(self) -> str:
        return f"{self._value:b}".zfill(self._size)

    @value.setter
    def value(self, rhs: ty.Any) -> None:
        if isinstance(rhs, str):
            rhs_int = int(rhs, 2)
            if rhs_int > ((2**self._size)-1):
                raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")
            if rhs_int < 0:
                raise ValueError(f"Cannot store negative value in `{type(self).__name__}[{self._size}]` type.")
            self._value = rhs_int

        elif isinstance(rhs, (UnsignedIntegerType, SignedIntegerType, AngleType)):
            raise InvalidTypeAssignment(rhs, self)

        elif isinstance(rhs, BitArrayType):
            if rhs.size > self._size:
                raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")
            self._value = rhs.value

        else:
            raise TypeError(f"Cannot store '{type(rhs).__name__}' type value in `{type(self).__name__}[{self._size}]` type.")

    def __getitem__(self, subscript):
        item = super().__getitem__(subscript)
        return BitArrayType(item._size, f"{item._value:b}".zfill(item._size))

    def __setitem__(self, subscript, value: str) -> None:
        super().__setitem__(subscript, int(value, 2))

    def __repr__(self) -> str:
        return (f"<{type(self).__name__}[{self._size}]: " + f"{self._value:b}".zfill(self._size) + ">")

    def __str__(self) -> str:
        return (f"<{type(self).__name__}[{self._size}]: " + f"{self._value:b}".zfill(self._size) + ">")

BitArrayType.__name__ = "qasm_bit"


class AngleType(UnsignedIntegerType):
    """Class for unsigned integer type
        angle[16] foo;
        angle[24] bar;
        angle[32] baz;
    """
    def __init__(self, size: int, value: int):
        if value > ((2**size)-1):
            raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{size}]` type to store result.")
        if value < 0:
            raise ValueError(f"Cannot store negative value in `{type(self).__name__}[{size}]` type.")
        super().__init__(size, value)

    @staticmethod
    def coerce(size: int, var: ty.Any):
        coerced_val = UnsignedIntegerType.coerce(size, var, AngleType.__name__)
        return coerced_val

    @property
    def value(self) -> float:
        return float(self._value * math.tau / ((0x1 << self._size)-1))

    @value.setter
    def value(self, rhs: ty.Any) -> None:
        if isinstance(rhs, int):
            if rhs > ((2**self._size)-1):
                raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")
            if rhs < 0:
                raise ValueError(f"Cannot store negative value in `{type(self).__name__}[{self._size}]` type.")
            self._value = rhs

        elif isinstance(rhs, (BitArrayType, SignedIntegerType, UnsignedIntegerType)):
            raise InvalidTypeAssignment(rhs, self)

        elif isinstance(rhs, AngleType):
            if rhs.size > self._size:
                raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")
            self._value = rhs.value

        else:
            raise TypeError(f"Cannot store '{type(rhs).__name__}' type value in `{type(self).__name__}[{self._size}]` type.")

    def __getitem__(self, subscript):
        item = super().__getitem__(subscript)
        return AngleType(item.size, item.value)

    def __setitem__(self, subscript, value: str) -> None:
        super().__setitem__(subscript, value)

    def __repr__(self) -> str:
        pi_coeff = 2 * self._value / ((0x1 << self._size)-1)
        return (f"<{type(self).__name__}[{self._size}]: {pi_coeff}π>")

    def __str__(self) -> str:
        pi_coeff = 2 * self._value / ((0x1 << self._size)-1)
        return (f"<{type(self).__name__}[{self._size}]: {pi_coeff}π>")

AngleType.__name__ = "qasm_angle"


def get_type(type_: qasm_ast.ClassicalType):
    """Function to map AST types to Translator types

    :param type_: A type class from the OpenNode AST
    :returns: ClassicalType of the translator
    """
    if isinstance(type_, SingleDesignatorType):
        pass
