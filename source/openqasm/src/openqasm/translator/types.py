import typing as ty
import math
from qiskit.circuit.classicalregister import ClassicalRegister
from openqasm.translator.exceptions import InvalidOperation
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

class SignedIntegerType(ClassicalType):
    """Class for unsigned integer type
        int[16] foo;
        int[24] bar;
        int[32] baz;
    """
    def __init__(self, size: int, value: int):
        if value not in range(-(0x1 << (size-1)), (0x1 << (size-1))):
            raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{size}]` type to store result.")
        super().__init__(size)
        self._value = value

    @staticmethod
    def _get_type_size(var: ty.Any) -> int:
        if isinstance(var, int):
            var_len = len(bin(var)[2:]) if var >= 0 else (len(bin(var)[3:])+1)
            return var_len

        # TODO: Do I need to add more python types here?!
        else:
            return SignedIntegerType._get_type_size(int(var))

    @staticmethod
    def coerce(size: int, var: ty.Any):
        if isinstance(var, int):
            if var not in range(-(0x1 << (size-1)), (0x1 << (size-1))):
                raise OverflowError(f"Not enough bits in the `int[{size}]` type to store result.")
            return SignedIntegerType(size, var)

        elif isinstance(var, float):
            result = int(var)
            if result not in range(-(0x1 << (size-1)), (0x1 << (size-1))):
                raise OverflowError(f"Not enough bits in the `int[{size}]` type to store result.")
            return SignedIntegerType(size, result)

        elif isinstance(var, SignedIntegerType):
            if var.size > size:
                raise OverflowError(f"Not enough bits in the `int[{size}]` type to store result.")
            return SignedIntegerType(size, var.value)

        elif isinstance(var, (UnsignedIntegerType, BitArrayType)):
            if var.size == size:
                return SignedIntegerType(size, var.value - (0x1 << size))
            elif var.size < size:
                return SignedIntegerType(size, var.value)
            else:
                raise OverflowError(f"Not enough bits in the `int[{size}]` type to store result.")

        # TODO: Not sure what to do of this one
        # Should it be invalid coercion
        # or just coerce into corresponding bits?
        elif isinstance(var, AngleType):
            pass

        else:
            raise TypeError(f"Invalid operation 'coercion' for types 'int[{size}]' and '{type(var).__name__}'")

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, rhs: ty.Any) -> None:
        if isinstance(rhs, int):
            if rhs not in range(-(0x1 << (self._size-1)), (0x1 << (self._size-1))):
                raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")
            self._value = rhs

        if isinstance(rhs, SignedIntegerType):
            if rhs.size > self._size:
                raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")
            self._value = rhs.value

        elif isinstance(rhs, (UnsignedIntegerType, BitArrayType)):
            if rhs.size < self._size:
                self._value = rhs.value
            elif rhs.size == self._size:
                self._value = (rhs.value - (0x1 << self._size))
            else:
                raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")

        # TODO: Not sure what to do of this one
        # Should it be invalid coercion
        # or just coerce into corresponding bits?
        elif isinstance(rhs, AngleType):
            pass

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
            int_len = SignedIntegerType._get_type_size(other)
            new_size = (self._size+1) if self._size >= int_len else (int_len+1)
            return SignedIntegerType(new_size, self._value + other)

        if isinstance(other, float):
            return float(self._value + other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            new_size = (self._size+1) if self._size >= other.size else (other.size+1)

            if isinstance(other, (UnsignedIntegerType, BitArrayType)):
                return SignedIntegerType(new_size, self._value + other.value)
            else:
                return SignedIntegerType(new_size+1, self._value + other.value)

        raise InvalidOperation("+", self, other)

    def __sub__(self, other: ty.Any):
        if isinstance(other, int):
            int_len = SignedIntegerType._get_type_size(other)
            new_size = (self._size+1) if self._size >= int_len else (int_len+1)
            return SignedIntegerType(new_size, self._value - other)

        if isinstance(other, float):
            return float(self._value - other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            new_size = (self._size+1) if self._size >= other.size else (other.size+1)

            if isinstance(other, (UnsignedIntegerType, BitArrayType)):
                return SignedIntegerType(new_size, self._value - other.value)
            else:
                return SignedIntegerType(new_size+1, self._value - other.value)

        raise InvalidOperation("-", self, other)

    def __mul__(self, other: ty.Any):
        if isinstance(other, int):
            int_len = SignedIntegerType._get_type_size(other)
            new_size = self._size + int_len
            return SignedIntegerType(new_size, self._value * other)

        if isinstance(other, float):
            return float(self._value * other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            new_size = int(self._size + other.size)

            if isinstance(other, (UnsignedIntegerType, BitArrayType)):
                return SignedIntegerType(new_size, self._value * other.value)
            else:
                return SignedIntegerType(new_size+1, self._value * other.value)

        raise InvalidOperation("*", self, other)

    def __truediv__(self, other: ty.Any):
        if isinstance(other, int):
            int_len = SignedIntegerType._get_type_size(other)
            new_size = self._size - int_len
            return SignedIntegerType(new_size, self._value / other)

        if isinstance(other, float):
            return float(self._value / other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            new_size = int(math.fabs(self._size - other.size))

            if isinstance(other, (UnsignedIntegerType, BitArrayType)):
                return SignedIntegerType(new_size, self._value / other.value)
            else:
                return SignedIntegerType(new_size+1, self._value / other.value)

        raise InvalidOperation("/", self, other)

    def __and__(self, other: ty.Any):
        if isinstance(other, int):
            int_len = SignedIntegerType._get_type_size(other)
            new_size = self._size if self._size > int_len else int_len
            return SignedIntegerType(self._size, self._value & other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            new_size = self._size if self._size > other.size else other.size
            return SignedIntegerType(new_size, self._value & other.value)

        raise InvalidOperation("&", self, other)

    def __or__(self, other: ty.Any):
        if isinstance(other, int):
            int_len = SignedIntegerType._get_type_size(other)
            new_size = self._size if self._size > int_len else int_len
            return SignedIntegerType(self._size, self._value | other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            new_size = self._size if self._size > other.size else other.size
            return SignedIntegerType(new_size, self._value | other.value)

        raise InvalidOperation("|", self, other)

    def __xor__(self, other: ty.Any):
        if isinstance(other, int):
            int_len = SignedIntegerType._get_type_size(other)
            new_size = self._size if self._size > int_len else int_len
            return SignedIntegerType(self._size, self._value ^ other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            new_size = self._size if self._size > other.size else other.size
            return SignedIntegerType(new_size, self._value ^ other.value)

        raise InvalidOperation("^", self, other)

    def __mod__(self, other: ty.Any):
        if isinstance(other, int):
            return SignedIntegerType(self._size, self._value % other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            return SignedIntegerType(self._size, self._value % other.value)

        raise InvalidOperation("%", self, other)

    def __pow__(self, other: ty.Any):
        if isinstance(other, int):
            int_len = SignedIntegerType._get_type_size(other)
            new_size = int(self._size * int_len)
            return SignedIntegerType(new_size, self._value ** other)

        if isinstance(other, float):
            return float(self._value ** other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            new_size = int(self._size * other.size)
            return SignedIntegerType(new_size, self._value ** other.value)

        raise InvalidOperation("**", self, other)

    def __lshift__(self, other: ty.Any):
        if isinstance(other, int):
            return SignedIntegerType(self._size, (self._value << other) % (2**(self._size-1)))

        if isinstance(other, (UnsignedIntegerType, BitArrayType)):
            return SignedIntegerType(self._size, (self._value << other.value) % (2**(self._size-1)))

        if isinstance(other, (SignedIntegerType, AngleType)):
            if other.value < 0:
                raise ValueError("Negative shift value not allowed for `<<`.")
            return SignedIntegerType(self._size, (self._value << other.value) % (2**(self._size-1)))

        raise InvalidOperation("<<", self, other)

    def __rshift__(self, other: ty.Any):
        if isinstance(other, int):
            return SignedIntegerType(self._size, (self._value >> other))

        if isinstance(other, (UnsignedIntegerType, BitArrayType)):
            return SignedIntegerType(self._size, (self._value >> other.value))

        if isinstance(other, (SignedIntegerType, AngleType)):
            if other.value < 0:
                raise ValueError("Negative shift value not allowed for `>>`.")
            return SignedIntegerType(self._size, (self._value >> other.value))

        raise InvalidOperation(">>", self, other)

    def __neg__(self):
        return SignedIntegerType(self._size, -self._value)

    def __inv__(self):
        return SignedIntegerType(self._size, ~self._value)

    def __eq__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value == other

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            return self._value == other.value

        raise InvalidOperation("==", self, other)

    def __ne__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value != other

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            return self._value != other.value

        raise InvalidOperation("!=", self, other)

    def __ge__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value >= other
        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            return self._value >= other.value

        raise InvalidOperation(">=", self, other)

    def __le__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value <= other
        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            return self._value <= other.value

        raise InvalidOperation("<=", self, other)

    def __gt__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value > other
        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            return self._value > other.value

        raise InvalidOperation(">", self, other)

    def __lt__(self, other: ty.Any) -> bool:
        if isinstance(other, (int, float)):
            return self._value < other
        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            return self._value < other.value

        raise InvalidOperation("<", self, other)

    def __repr__(self) -> str:
        return str(self._value)

    def __str__(self) -> str:
        return str(self._value)

SignedIntegerType.__name__ = "int"

class UnsignedIntegerType(SignedIntegerType):
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

        # TODO: Do I need to add more python types here?!
        else:
            return UnsignedIntegerType._get_type_size(int(var))

    @staticmethod
    def coerce(size: int, var: ty.Any):
        if isinstance(var, int):
            if var not in range(0, (0x1 << size)):
                raise OverflowError(f"Not enough bits in the `uint[{size}]` type to store result.")
            return UnsignedIntegerType(size, var)

        elif isinstance(var, float):
            result = int(var)
            if result not in range(0, (0x1 << size)):
                raise OverflowError(f"Not enough bits in the `uint[{size}]` type to store result.")
            return UnsignedIntegerType(size, result)

        elif isinstance(var, SignedIntegerType):
            if var.size > size:
                raise OverflowError(f"Not enough bits in the `uint[{size}]` type to store result.")
            new_value = var.value if var.value > 0 else (var.value + (0x1 << var.size))
            return SignedIntegerType(size, new_value)

        elif isinstance(var, BitArrayType):
            if var.size <= size:
                return UnsignedIntegerType(size, int(var.value, 2))
            else:
                raise OverflowError(f"Not enough bits in the `uint[{size}]` type to store result.")

        elif isinstance(var, UnsignedIntegerType):
            if var.size <= size:
                return UnsignedIntegerType(size, var.value)
            else:
                raise OverflowError(f"Not enough bits in the `uint[{size}]` type to store result.")

        # TODO: Not sure what to do of this one
        # Should it be invalid coercion
        # or just coerce into corresponding bits?
        elif isinstance(var, AngleType):
            pass

        else:
            raise TypeError(f"Invalid operation 'coercion' for types `int[{size}]` and '{type(var).__name__}'")

    @value.setter
    def value(self, rhs: ty.Any) -> None:
        if isinstance(rhs, int):
            if rhs not in range(0, (0x1 << self._size)):
                raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")
            self._value = rhs

        if isinstance(rhs, SignedIntegerType):
            if rhs.size > self._size:
                raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")
            new_value = rhs.value if rhs.value > 0 else (rhs.value + (0x1 << rhs.size))
            self._value = new_value

        elif isinstance(rhs, BitArrayType):
            if rhs.size > self._size:
                raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")
            self._value = int(rhs.value, 2)

        elif isinstance(rhs, UnsignedIntegerType):
            if rhs.size > self._size:
                raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")
            self._value = rhs.value

        # TODO: Not sure what to do of this one
        # Should it be invalid coercion
        # or just coerce into corresponding bits?
        elif isinstance(rhs, AngleType):
            pass

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
            bit_str = f"{self._value}".zfill(self._size)
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
            int_len = UnsignedIntegerType._get_type_size(other)
            new_size = (self._size+1) if self._size >= int_len else (int_len+1)
            return UnsignedIntegerType(new_size, self._value + other)

        if isinstance(other, float):
            return float(self._value + other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            new_size = (self._size+1) if self._size >= other.size else (other.size+1)

            if isinstance(other, (UnsignedIntegerType, BitArrayType)):
                return UnsignedIntegerType(new_size, self._value + other.value)
            else:
                return SignedIntegerType(new_size+1, self._value + other.value)

        raise InvalidOperation("+", self, other)

    def __sub__(self, other: ty.Any):
        if isinstance(other, int):
            int_len = UnsignedIntegerType._get_type_size(other)
            new_size = (self._size+1) if self._size >= int_len else (int_len+1)
            return UnsignedIntegerType(new_size, self._value - other)

        if isinstance(other, float):
            return float(self._value - other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            new_size = (self._size+1) if self._size >= other.size else (other.size+1)

            if isinstance(other, (UnsignedIntegerType, BitArrayType)):
                return UnsignedIntegerType(new_size, self._value - other.value)
            else:
                return SignedIntegerType(new_size+1, self._value - other.value)

        raise InvalidOperation("-", self, other)

    def __mul__(self, other: ty.Any):
        if isinstance(other, int):
            int_len = UnsignedIntegerType._get_type_size(other)
            new_size = self._size + int_len
            return UnsignedIntegerType(new_size, self._value * other)

        if isinstance(other, float):
            return float(self._value * other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            new_size = int(self._size + other.size)

            if isinstance(other, (UnsignedIntegerType, BitArrayType)):
                return UnsignedIntegerType(new_size, self._value * other.value)
            else:
                return SignedIntegerType(new_size+1, self._value * other.value)

        raise InvalidOperation("*", self, other)

    def __truediv__(self, other: ty.Any):
        if isinstance(other, int):
            int_len = UnsignedIntegerType._get_type_size(other)
            new_size = self._size - int_len
            return UnsignedIntegerType(new_size, self._value / other)

        if isinstance(other, float):
            return float(self._value / other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            new_size = int(math.fabs(self._size - other.size))

            if isinstance(other, (UnsignedIntegerType, BitArrayType)):
                return UnsignedIntegerType(new_size, self._value / other.value)
            else:
                return SignedIntegerType(new_size+1, self._value / other.value)

        raise InvalidOperation("/", self, other)

    def __and__(self, other: ty.Any):
        if isinstance(other, int):
            int_len = UnsignedIntegerType._get_type_size(other)
            new_size = self._size if self._size > int_len else int_len
            return UnsignedIntegerType(self._size, self._value & other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            new_size = self._size if self._size > other.size else other.size
            if isinstance(other, (UnsignedIntegerType, BitArrayType)):
                return UnsignedIntegerType(new_size, self._value & other.value)
            else:
                return SignedIntegerType(new_size, self._value & other.value)

        raise InvalidOperation("&", self, other)

    def __or__(self, other: ty.Any):
        if isinstance(other, int):
            int_len = UnsignedIntegerType._get_type_size(other)
            new_size = self._size if self._size > int_len else int_len
            return UnsignedIntegerType(self._size, self._value | other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            new_size = self._size if self._size > other.size else other.size
            if isinstance(other, (UnsignedIntegerType, BitArrayType)):
                return UnsignedIntegerType(new_size, self._value | other.value)
            else:
                return SignedIntegerType(new_size, self._value | other.value)

        raise InvalidOperation("|", self, other)

    def __xor__(self, other: ty.Any):
        if isinstance(other, int):
            int_len = UnsignedIntegerType._get_type_size(other)
            new_size = self._size if self._size > int_len else int_len
            return UnsignedIntegerType(self._size, self._value ^ other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            new_size = self._size if self._size > other.size else other.size
            if isinstance(other, (UnsignedIntegerType, BitArrayType)):
                return UnsignedIntegerType(new_size, self._value ^ other.value)
            else:
                return SignedIntegerType(new_size, self._value ^ other.value)

        raise InvalidOperation("^", self, other)

    def __mod__(self, other: ty.Any):
        if isinstance(other, int):
            int_len = UnsignedIntegerType._get_type_size(other)
            new_size = int(math.fabs(self._size - int_len))
            return UnsignedIntegerType(new_size, self._value % other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            new_size = int(math.fabs(self._size - other.size))

            if isinstance(other, (UnsignedIntegerType, BitArrayType)):
                return UnsignedIntegerType(new_size, self._value % other.value)
            else:
                return SignedIntegerType(new_size, self._value % other.value)

        raise InvalidOperation("%", self, other)

    def __pow__(self, other: ty.Any):
        if isinstance(other, int):
            int_len = UnsignedIntegerType._get_type_size(other)
            new_size = int(self._size * int_len)
            return UnsignedIntegerType(new_size, self._value ** other)

        if isinstance(other, float):
            return float(self._value ** other)

        if isinstance(other, (UnsignedIntegerType, BitArrayType, SignedIntegerType, AngleType)):
            new_size = int(self._size * other.size)
            return UnsignedIntegerType(new_size, self._value ** other.value)

        raise InvalidOperation("**", self, other)

    def __lshift__(self, other: ty.Any):
        if isinstance(other, int):
            return UnsignedIntegerType(self._size, (self._value << other) % (2**self._size))

        if isinstance(other, (UnsignedIntegerType, BitArrayType)):
            return UnsignedIntegerType(self._size, (self._value << other.value) % (2**self._size))

        if isinstance(other, (SignedIntegerType, AngleType)):
            if other.value < 0:
                raise ValueError("Negative shift value not allowed for `<<`.")
            return UnsignedIntegerType(self._size, (self._value << other.value) % (2**self._size))

        raise InvalidOperation("<<", self, other)

    def __rshift__(self, other: ty.Any):
        if isinstance(other, int):
            return UnsignedIntegerType(self._size, (self._value << other))

        if isinstance(other, (UnsignedIntegerType, BitArrayType)):
            return UnsignedIntegerType(self._size, (self._value << other.value))

        if isinstance(other, (SignedIntegerType, AngleType)):
            if other.value < 0:
                raise ValueError("Negative shift value not allowed for `>>`.")
            return UnsignedIntegerType(self._size, (self._value << other.value))

        raise InvalidOperation(">>", self, other)

    def __neg__(self):
        return SignedIntegerType(self._size+1, -self._value)

    def __inv__(self):
        return UnsignedIntegerType(self._size, ~self._value)

UnsignedIntegerType.__name__ = "uint"


class BitArrayType(UnsignedIntegerType):
    """Class for bit array type
        bit c1;
        bit[3] c2;
    """
    def __init__(self, size: int, value: str, name: str):
        if not isinstance(value, str):
            raise ValueError(f"Expected value to be of type `str`, found `{type(value)}`.")
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
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        int_value = int(value, 2)
        if int_value > ((2**self._size)-1):
            raise OverflowError(f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result.")
        if int_value < 0:
            raise ValueError(f"Cannot store negative result value in `{type(self).__name__}[{self._size}]` type.")
        self._value = int_value

    def __getitem__(self, subscript):
        item = super().__getitem__(subscript)
        if isinstance(subscript, int):
            bit_str = str(item)
            return BitArrayType(item.size, bit_str, (self._name+f"[{subscript}]"))

        if isinstance(subscript, slice):
            str_start = 0 if subscript.start is None else subscript.start
            str_stop = self._size if subscript.stop is None else subscript.stop
            str_len = int(math.fabs(str_stop - str_start))
            bit_str = f"{item.value:b}".zfill(str_len)
            return BitArrayType(str_len, bit_str, (self._name+f"[{subscript.start}:{subscript.stop}:{subscript.step}]"))

        # TODO: Think of providing some error localization and variable name here
        raise TypeError(f"Expected 'int/uint' or 'slice' in subscript, found '{type(subscript)}'.")

    def __setitem__(self, subscript, value: str) -> None:
        super().__setitem__(subscript, int(value, 2))

    def __repr__(self) -> str:
        return f"{self._value:b}".zfill(self._size)

    def __str__(self) -> str:
        return f"{self._value:b}".zfill(self._size)

BitArrayType.__name__ = "bit"

class AngleType(UnsignedIntegerType):
    """Class for unsigned integer type
        angle[16] foo;
        angle[24] bar;
        angle[32] baz;
    """
    def __init__(self, size: int, value: int):
        pass

# TODO: Study more about this
# class FixedType(ClassicalType):
#     """Class for unsigned integer type
#         fixed[16, 10] foo;
#         fixed[24, 11] bar;
#         fixed[32, 12] baz;
#     """
#     pass

def get_type(type_: qasm_ast.ClassicalType) -> ClassicalType:
    """Function to map AST types to Translator types

    :param type_: A type class from the OpenNode AST
    :returns: ClassicalType of the translator
    """
    pass
