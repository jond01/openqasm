import math
import typing as ty
from copy import deepcopy
from enum import Enum
from abc import ABC, abstractmethod

from qiskit.circuit.classicalregister import \
    ClassicalRegister as QiskitClassicalRegister
from qiskit.circuit.quantumregister import \
    QuantumRegister as QiskitQuantumRegister

import openqasm.ast as qasm_ast
from openqasm.translator.exceptions import InvalidOperation, InvalidTypeAssignment

"""Implement all the types related to (qu)bit arrays."""

def _get_indices(size: int, indexing: ty.Union[int, ty.List[int], slice]) -> ty.List[int]:
    """Compute the indices represented by the given indexing."""
    # We want the indices as a list of integers.
    # If they are given as a simple integer or a slice, compute the equivalent
    # list of integers.
    if isinstance(indexing, int):
        indexing = [indexing]
    elif isinstance(indexing, slice):
        # WARN: does not throw if stop is larger than the size of the register.
        #       Python native lists have the same behaviour
        start, stop, step = indexing.indices(size)
        indexing = list(range(start, stop, step))
    return indexing


class BaseRegister(ABC):
    """Base type for any register-like class.

    This type defines all the necessary abstract methods that should be defined
    in order to be considered as a "register" type.
    """

    def __init__(self, size: int):
        """Initialise a BaseRegister.

        :param size: number of bits contained in the register. Should be
            stricly positive.
        """
        self._size: int = size

    @property
    def size(self) -> int:
        """Return the size of the underlying register."""
        return self._size

    @abstractmethod
    def __getitem__(self, indices: ty.Union[int, ty.List[int], slice]) -> ty.Any:
        """Recover one or more items from a register.

        This method should be overloaded by the inheriting type to implement
        the expected behaviour.
        """
        pass

    @abstractmethod
    def __setitem__(self, indices: ty.Union[int, ty.List[int], slice], value: ty.Any) -> None:
        """Set one or more items from a register.

        This method should be overloaded by the inheriting type to implement
        the expected behaviour.
        Not all the register types are expected to implement this method. If
        a type does not implement this error, it should raise an informative
        exception.
        """
        pass

    @property
    @abstractmethod
    def bits(self) -> ty.List[ty.Union[QiskitClassicalRegister, QiskitQuantumRegister]]:
        """Recover the underlying bits stored by the BaseRegister."""
        pass


class RegisterView(BaseRegister):
    """Implement a view on any BaseRegister instance."""

    def __init__(self, register: BaseRegister, indices: ty.Union[int, ty.List[int], slice]):
        """Initialise the RegisterView instance.

        :param register: an instance of one of the derived type of BaseRegister
            that implements the abstract interface provided by BaseRegister.
        :param indices: the indices that will be used by the view.
        """
        index_list: ty.List[int] = _get_indices(register.size, indices)
        # Once we have the correct indices, we can start initialising the
        # instance.
        super().__init__(len(index_list))
        self._register: BaseRegister = register
        self._indices: ty.List[int] = index_list

    def _compute_indices(self, indices: ty.Union[int, ty.List[int], slice]) -> ty.List[int]:
        return [self._indices[i] for i in _get_indices(self.size, indices)]

    def __getitem__(self, indices: ty.Union[int, ty.List[int], slice]) -> ty.Any:
        """Recover one or more items from the RegisterView."""
        augmented_indices: ty.List[int] = self._compute_indices(indices)
        return RegisterView(self, augmented_indices)

    def __setitem__(self, indices: ty.Union[int, ty.List[int], slice], value: ty.Any) -> None:
        """Set one or more items from a register."""
        augmented_indices: ty.List[int] = self._compute_indices(indices)
        self._register[augmented_indices] = value

    @property
    def bits(self) -> ty.List[ty.Union[QiskitClassicalRegister, QiskitQuantumRegister]]:
        bits = self._register.bits
        return [bits[i] for i in self._indices]


class RegisterConcatenation(BaseRegister):
    """Concatenation of 2 (potentially overlapping) BaseRegister instances."""

    def __init__(self, lhs: BaseRegister, rhs: BaseRegister):
        """Initialise the RegisterConcatenation instance.

        :param lhs: the register appearing first in the concatenation.
        :param rhs: the register appearing second in the concatenation.
        """
        super().__init__(lhs.size + rhs.size)
        self._lhs = lhs
        self._rhs = rhs
        self._lhs_size: int = lhs.size

    def _get_split_indices(
        self, indices: ty.Union[int, ty.List[int], slice]
    ) -> ty.Tuple[ty.List[int], ty.List[int]]:
        """
        Get the transformed indices to directly index the individual registers.

        :param indices: the indices asked by the caller.
        :return: 2 lists of indices, the first one being indices for the
            left-hand side register of the concatenation and the second one
            being for the right-hand side register of the concatenation.
        """
        transformed_indices: ty.List[int] = _get_indices(self.size, indices)

        return (
            [ti for ti in transformed_indices if ti < self._lhs_size],
            [ti - self._lhs_size for ti in transformed_indices if ti >= self._lhs_size],
        )

    def __getitem__(self, indices: ty.Union[int, ty.List[int], slice]) -> ty.Any:
        """Recover one or more items from the RegisterConcatenation."""
        lhs_indices, rhs_indices = self._get_split_indices(indices)
        return RegisterConcatenation(
            RegisterView(self._lhs, lhs_indices), RegisterView(self._rhs, rhs_indices)
        )

    def __setitem__(self, indices: ty.Union[int, ty.List[int], slice], value: ty.Any) -> None:
        """Set one or more items from a register.

        Warning: if the provided indices is a list of integers or a slice, the
        provided value is assumed to be indexable like "value[i]".
        """
        # Base case: if the provided indices is only a single integer then
        # we modify the correct value.
        if isinstance(indices, int):
            if indices < self._lhs_size:
                self._lhs[indices] = value
            else:
                self._rhs[indices] = value
        # Else, we can recurse by calling the base case.
        else:
            for idx in _get_indices(self.size, indices):
                self[idx] = value[idx]

    @property
    def bits(self) -> ty.List[ty.Union[QiskitClassicalRegister, QiskitQuantumRegister]]:
        return self._lhs.bits + self._rhs.bits


class Register(BaseRegister):
    """Base class for any actual register."""

    def __getitem__(self, indices: ty.Union[int, ty.List[int], slice]) -> ty.Any:
        """Recover one or more items from a register.

        This method should be overloaded by the inheriting type to implement
        the expected behaviour.
        """
        return RegisterView(self, indices)


class QuantumRegister(Register):
    """Final class representing a QuantumRegister."""

    def __init__(self, qreg: QiskitQuantumRegister):
        """Initialise a QuantumRegister with the given instance.

        :param qreg: qiskit.QuantumRegister instance that will be kept
            internally and used when indexing.
        """
        super().__init__(qreg.size)
        self._register: QiskitQuantumRegister = qreg

    def __setitem__(self, indices: ty.Union[int, ty.List[int], slice], value: ty.Any) -> None:
        """Set one or more items from a register.

        This method should be overloaded by the inheriting type to implement
        the expected behaviour.
        Not all the register types are expected to implement this method. If
        a type does not implement this error, it should raise an informative
        exception.
        """
        raise RuntimeError("QuantumRegister does not support assignement.")

    @property
    def bits(self) -> ty.List[QiskitQuantumRegister]:
        return [self._register[i] for i in range(self.size)]

QuantumRegister.__name__ = "qubit"


class ClassicalType:
    """Base class for all Classical Types in the Translator"""

    def __init__(self, size: int):
        """Initialise a ClassicalType.

        :param size: number of bits contained in the type. Should be
            stricly positive.
        """
        self._size: int = size

    @property
    def size(self) -> int:
        """Return the size of the underlying type."""
        return self._size

    @abstractmethod
    def __repr__(self) -> str:
        """Representation of the ClassicalType while printing the value.

        This method should be overloaded by the inheriting type to implement
        the expected behaviour.
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Stringify the ClassicalType while printing the value.

        This method should be overloaded by the inheriting type to implement
        the expected behaviour.
        """
        pass

    @abstractmethod
    def __getitem__(self, subscript):
        """Get one or more bits from the classical type.

        This method should be overloaded by the inheriting type to implement
        the expected behaviour.
        """
        pass

    def __setitem__(self, subscript, rhs: ty.Any):
        """Set one or more bits in the classical type. Forbidden action."""
        raise RuntimeError(f"'{type(self).__name__}' type does not support assignement.")


class TimingType:
    """Base class for all Timing Types in the Translator"""

    def __init__(self, unit: qasm_ast.TimeUnit):
        self._unit = unit

    @property
    def unit(self) -> qasm_ast.TimeUnit:
        """Return the unit of the underlying type."""
        return self._unit

def _get_type_size(var: ty.Union[int, float, bool, ClassicalType]) -> int:
    """Get the size required to store a value of <type> during cast.

    :param var: variable of the particular Union type for which the
        size has to be calculated.
    """
    if isinstance(var, (int, float)):
        return abs(int(var)).bit_length() + (var < 0)

    if isinstance(var, ClassicalType):
        return var.size


class BitArray:
    """Base class representing an array of classical bits."""

    def __init__(self, size: int, value: ty.Optional[str]):
        """Initialise a BitArray with the given value.

        :param size: number of bits contained in the array.
        :param value: None if the bit array is not initialised, else the actual
            value held by the classical bit array. Any individual bit can
            potentially be uninitialised.
        """
        if len(value) != size:
            raise ValueError(f"Initial value should be of same length as the size.")

        self._size = size
        # Default value for self._value
        self._value: str = value if value is not None else ("x" * size)

    @property
    def value(self) -> int:
        if "x" in self._value:
            raise ValueError("Uninitialized / partially initialized bit-array cannot have a value.")

        return int(self._value, 2)

    @property
    def bit_value(self) -> str:
        return self._value

    @value.setter
    def value(self, rhs: ty.Optional[str]) -> None:
        if rhs is None:
            self._value = "x" * self._size

        elif isinstance(rhs, str):
            if len(rhs) != self._size:
                raise ValueError(
                    f"The type `{type(self).__name__}[{self._size}]` cannot be assigned value of type `{type(self).__name__}[{len(rhs)}]`."
                )
            self._value = rhs

        elif isinstance(rhs, (ClassicalType, TimingType)):
            raise InvalidTypeAssignment(rhs, self)

        else:
            raise TypeError(
                f"Cannot store '{type(rhs).__name__}' type value in `{type(self).__name__}[{self._size}]` type."
            )

    def __getitem__(
        self, indices: ty.Union[int, ty.List[int], slice]
    ):
        """Get the indexed bits from the bit-array

        :param indices: any indices that are compatible (int/List[int]/slice).
        """
        indexed_value = self._value[indices]

        if isinstance(self, BitRegister):
            return BitRegister(self._register[indices], indexed_value)

        if isinstance(self, BitArray):
            return BitArray(len(indexed_value), indexed_value)


    def __setitem__(
        self, indices: ty.Union[int, ty.List[int], slice], value: ty.Union[int, ty.Sequence[int]]
    ) -> None:
        """Set the indexed bits to the given value.

        :param indices: any indices that is compatible. If only one index is
            provided, the value is supposed to be a boolean. If more than one
            index is provided, the value should be a type that support indexing
            and "value[i]" should return a boolean for any valid value of i.
        :param value:
        """
        transformed_indices: ty.List[int] = _get_indices(len(self._value), indices)
        if len(transformed_indices) == 1 and isinstance(value, int):
            if value not in [0, 1]:
                raise ValueError("The RHS value should be either 0 or 1.")
            self._value[transformed_indices[0]] = str(value)
        elif len(transformed_indices) > 1 and isinstance(value, ty.Sequence):
            for i in transformed_indices:
                if value[i] not in [0, 1]:
                    raise ValueError("The RHS value should be either 0 or 1.")
                self._value[i] = str(value[i])
        else:
            raise RuntimeError(
                f"Incompatible types for indices ({type(indices).__name__}) "
                f"and value ({type(value).__name__})"
            )

    # Additional bitwise operations
    def rotr(self, other):
        if isinstance(other, int):
            rot_value = other
        elif isinstance(other, (Int, Uint, BitArray)):
            rot_value = other.value

        if rot_value < 0:
            return self.rotl(other)
        if rot_value == 0:
            return self
        if rot_value > 0:
            rot_value %= self._size
            mask = self.value & ((0x1 << rot_value) - 1)
            new_value = ((self.value >> rot_value) | (mask << (self._size - rot_value)))
            return BitArray(self._size, f"{new_value:b}".zfill(self._size))

    def rotl(self, other):
        if isinstance(other, int):
            rot_value = other
        elif isinstance(other, (Int, Uint, BitArray)):
            rot_value = other.value

        if rot_value < 0:
            return self.rotr(other)
        if rot_value == 0:
            return self
        if rot_value > 0:
            rot_value %= self._size
            mask = (0x1 << self._size) - 1
            new_value = (((self.value << rot_value) & mask) | (self.value >> (self._size - rot_value)))
            return BitArray(self._size, f"{new_value:b}".zfill(self._size))

    def popcount(self):
        return f"{self.value:b}".count("1")

    # Overloading bitwise operations
    def __and__(self, other):
        if isinstance(other, int):
            return BitArray(self._size, f"{self.value & other:b}".zfill(self._size))

        if isinstance(other, (Int, Uint, BitArray)):
            return BitArray(self._size, f"{self.value & other.value:b}".zfill(self._size))

        raise InvalidOperation("&", self, other)

    def __or__(self, other):
        if isinstance(other, int):
            return BitArray(self._size, f"{self.value | other:b}".zfill(self._size))

        if isinstance(other, (Int, Uint, BitArray)):
            return BitArray(self._size, f"{self.value | other.value:b}".zfill(self._size))

        raise InvalidOperation("|", self, other)

    def __xor__(self, other):
        if isinstance(other, int):
            return BitArray(self._size, f"{self.value ^ other:b}".zfill(self._size))

        if isinstance(other, (Int, Uint, BitArray)):
            return BitArray(self._size, f"{self.value ^ other.value:b}".zfill(self._size))

        raise InvalidOperation("|", self, other)

    def __inv__(self, other):
        return BitArray(self._size, f"{~self.value:b}".zfill(self._size))

    def __lshift__(self, other):
        if isinstance(other, int):
            value = (self.value << other) % (0x1 << self._size)
            return BitArray(self._size, f"{value:b}".zfill(self._size))

        if isinstance(other, (Uint, BitArray)):
            value = (self.value << other.value) % (0x1 << self._size)
            return BitArray(self._size, f"{value:b}".zfill(self._size))

        if isinstance(other, Int):
            if other.value < 0:
                raise ValueError("Negative shift value not allowed for `<<`.")
            value = (self.value << other.value) % (0x1 << self._size)
            return BitArray(self._size, f"{value:b}".zfill(self._size))

        raise InvalidOperation("<<", self, other)

    def __rshift__(self, other):
        if isinstance(other, int):
            value = (self.value >> other)
            return BitArray(self._size, f"{value:b}".zfill(self._size))

        if isinstance(other, (Uint, BitArray)):
            value = (self.value >> other.value)
            return BitArray(self._size, f"{value:b}".zfill(self._size))

        if isinstance(other, Int):
            if other.value < 0:
                raise ValueError("Negative shift value not allowed for `>>`.")
            value = (self.value >> other.value)
            return BitArray(self._size, f"{value:b}".zfill(self._size))

        raise InvalidOperation(">>", self, other)


class BitCast(BitArray):
    """A bit array that does not own any classical register."""

    @staticmethod
    def _number_to_bits(num: int):
        size = _get_type_size(num)
        transformed_num = (num + (0x1 << size)) if num < 0 else num
        return f"{transformed_num:b}".zfill(size)

    @staticmethod
    def cast(
        argument: ty.Union[ClassicalType, QuantumRegister, TimingType, float, bool],
        size: ty.Optional[int] = None
    ):
        """Cast the `argument` to a BitCast type"""
        if isinstance(argument, (TimingType, QuantumRegister, float)):
            cast_size = "" if size is None else f"[{size}]"
            raise TypeError(f"`{type(argument).__name__}` type cannot be cast into a `bit{cast_size}` type.")
        if isinstance(argument, ClassicalType):
            bits = BitCast._number_to_bits(argument.value)
            return BitArray(len(bits), bits)
        if isinstance(argument, int):
            bits = BitCast._number_to_bits(argument)
            return BitArray(len(bits), bits)
        if isinstance(argument, bool):
            return BitArray(1, [argument])


class BitRegister(Register, BitArray):
    """A bit array that owns a classical register."""

    def __init__(self, register: QiskitClassicalRegister, value: ty.Optional[str]):
        """Construct a bit array owning a qiskit.ClassicalRegister instance."""
        Register.__init__(self, register.size)
        BitArray.__init__(self, register.size, value)
        self._register: QiskitClassicalRegister = register

    def __getitem__(self, indices: ty.Union[int, ty.List[int], slice]) -> ty.Optional[str]:
        """Get one or more items from a register."""
        return BitArray.__getitem__(self, indices)

    def __setitem__(self, indices: ty.Union[int, ty.List[int], slice], value: ty.Any) -> None:
        """Set one or more items to a register."""
        BitArray.__setitem__(self, indices, value)

    @property
    def bits(self) -> ty.List[QiskitQuantumRegister]:
        return [self._register[i] for i in range(self.size)]

BitRegister.__name__ = "bit"


class Int(ClassicalType):
    """Class for Int type in the Translator"""

    def __init__(self, size: int, value: int):
        """Initialise a Int type.

        :param size: number of bits contained in the type. Should be
            stricly positive.
        :param value: the value to be stored in the Int type.
        """
        if value not in range(-(0x1 << (size - 1)), (0x1 << (size - 1))):
            raise OverflowError(
                f"Not enough bits in the `{type(self).__name__}[{size}]` type to store result."
            )

        super().__init__(size)
        self._value = value

    @property
    def value(self) -> int:
        """Return the value of the underlying type."""
        return self._value

    @value.setter
    def value(self, rhs: ty.Any) -> None:
        """Set the value of the underlying type.

        :param rhs: the RHS value to be stored in Int type object.
        """
        if isinstance(rhs, int):
            if rhs not in range(-(0x1 << (self._size - 1)), (0x1 << (self._size - 1))):
                raise OverflowError(
                    f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result."
                )
            self._value = rhs

        elif isinstance(rhs, Int):
            if rhs.size > self._size:
                raise OverflowError(
                    f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result."
                )
            self._value = rhs.value

        elif isinstance(rhs, (Uint, BitArray)):
            if rhs.size >= self._size:
                raise InvalidTypeAssignment(rhs, self)
            self._value = rhs.value

        else:
            raise TypeError(
                f"Cannot store '{type(rhs).__name__}' type value in `{type(self).__name__}[{self._size}]` type."
            )

    @staticmethod
    def cast(
        argument: ty.Union[ClassicalType, QuantumRegister, TimingType, float, bool],
        size: ty.Optional[int] = None
    ):
        """Cast a particular varible to Int type.

        :param argument: Argument wihin the cast statement.
        :param size: Size of the Int returned
        """

        size = _get_type_size(argument) if size is None else size
        if isinstance(argument, (Angle, TimingType, QuantumRegister)):
            cast_size = "" if size is None else f"[{size}]"
            raise TypeError(
                f"`{type(argument).__name__}` type cannot be cast into a `int{cast_size}` type."
            )

        if isinstance(argument, Int):
            return Int(size, argument.value)

        if isinstance(argument, (Uint, BitArray)):
            new_value = (argument.value
                         if argument.value < (0x1 << (size-1))
                         else (argument.value - (0x1 << size)))
            return Int(size, new_value)

        if isinstance(argument, bool):
            return Int(1, int(argument))

        if isinstance(argument, float):
            return Int(size, int(argument))

        raise TypeError(
            f"Invalid operation 'coercion' for types `int[{size}]` and '{type(argument).__name__}'"
        )

    def __getitem__(self, subscript):
        """Get one or more bits from the classical type.

        :param subscript: int/List[int]/slice for indexing the Int type.
        """
        if isinstance(subscript, int):
            if subscript in range(0, self._size):
                result = (self._value & (0x1 << subscript)) >> subscript
                return Int(2, int(result))
            # TODO: Think of providing some error localization and variable name here
            raise IndexError(f"Index value '{subscript}' is out of range.")

        elif isinstance(subscript, slice):
            bit_str = f"{self._value:b}".zfill(self._size)
            result = bit_str[::-1][subscript][::-1]
            return Int(len(result) + 1, int(result, 2))

        else:
            raise TypeError(
                f"Expected 'int/uint' or 'slice' in subscript, found '{type(subscript)}'."
            )

    def __repr__(self) -> str:
        """Representation of the Int type while printing the value."""
        return f"<{type(self).__name__}[{self._size}]: {self._value}>"

    def __str__(self) -> str:
        """Stringify the Int type while printing the value."""
        return f"<{type(self).__name__}[{self._size}]: {self._value}>"

    # Overloading arithmetic operations
    def __add__(self, other: ty.Any):
        if isinstance(other, int):
            return Int(self._size, int(self._value + other))

        if isinstance(other, float):
            return float(self._value + other)

        if isinstance(other, (Int, Uint, Angle, BitArray)):
            return Int(self._size, int(self._value + other.value))

        raise InvalidOperation("+", self, other)

    def __sub__(self, other: ty.Any):
        if isinstance(other, int):
            return Int(self._size, int(self._value - other))

        if isinstance(other, float):
            return float(self._value - other)

        if isinstance(other, (Int, Uint, Angle, BitArray)):
            return Int(self._size, int(self._value - other.value))

        raise InvalidOperation("-", self, other)

    def __mul__(self, other: ty.Any):
        if isinstance(other, int):
            return Int(self._size, int(self._value * other))

        if isinstance(other, float):
            return float(self._value * other)

        if isinstance(other, (Int, Uint, Angle, BitArray)):
            return Int(self._size, int(self._value * other.value))

        raise InvalidOperation("*", self, other)

    def __truediv__(self, other: ty.Any):
        if isinstance(other, int):
            return Int(self._size, int(self._value / other))

        if isinstance(other, float):
            return float(self._value / other)

        if isinstance(other, (Int, Uint, Angle, BitArray)):
            return Int(self._size, int(self._value / other.value))

        raise InvalidOperation("/", self, other)

    def __mod__(self, other: ty.Any):
        if isinstance(other, int):
            return Int(self._size, int(self._value % other))

        if isinstance(other, float):
            return float(self._value % other)

        if isinstance(other, (Int, Uint, Angle, BitArray)):
            return Int(self._size, int(self._value % other.value))

        raise InvalidOperation("%", self, other)

    def __pow__(self, other: ty.Any):
        if isinstance(other, (int, float)):
            return Int(self._size, int(self._value ** other))

        if isinstance(other, (Int, Uint, Angle, BitArray)):
            return Int(self._size, int(self._value ** other.value))

        raise InvalidOperation("**", self, other)

Int.__name__ = "int"


class Uint(ClassicalType):
    """Class for Uint type in the Translator"""

    def __init__(self, size: int, value: int):
        """Initialise a Uint type.

        :param size: number of bits contained in the type. Should be
            stricly positive.
        :param value: the value to be stored in the Uint type.
        """
        if value not in range(0, (0x1 << size)):
            raise OverflowError(
                f"Not enough bits in the `{type(self).__name__}[{size}]` type to store result."
            )

        super().__init__(size)
        self._value = value

    @property
    def value(self) -> int:
        """Return the value of the underlying type."""
        return self._value

    @value.setter
    def value(self, rhs: ty.Any) -> None:
        """Set the value of the underlying type.

        :param rhs: the RHS value to be stored in Uint type object.
        """
        if isinstance(rhs, int):
            if rhs not in range(0, (0x1 << self._size)):
                raise OverflowError(
                    f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result."
                )
            self._value = rhs

        elif isinstance(rhs, (Uint, BitArray)):
            if rhs.size > self._size:
                raise OverflowError(
                    f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result."
                )
            self._value = rhs.value

        elif isinstance(rhs, Int):
            raise InvalidTypeAssignment(rhs, self)

        else:
            raise TypeError(
                f"Cannot store '{type(rhs).__name__}' type value in `{type(self).__name__}[{self._size}]` type."
            )

    @staticmethod
    def cast(
        argument: ty.Union[ClassicalType, QuantumRegister, TimingType, float, bool],
        size: ty.Optional[int] = None
    ):
        """Cast a particular varible to Uint type.

        :param argument: Argument wihin the cast statement.
        :param size: Size of the Uint returned
        """

        size = _get_type_size(argument) if size is None else size
        if isinstance(argument, (Angle, TimingType, QuantumRegister)):
            cast_size = "" if size is None else f"[{size}]"
            raise TypeError(
                f"`{type(argument).__name__}` type cannot be cast into a `uint{cast_size}` type."
            )

        if isinstance(argument, (Uint, BitArray)):
            return Uint(size, argument.value)

        if isinstance(argument, Int):
            new_value = (argument.value
                         if argument.value > 0
                         else (argument.value + (0x1 << size)))
            return Uint(size, new_value)

        if isinstance(argument, bool):
            return Uint(1, int(argument))

        if isinstance(argument, float):
            new_value = (int(argument)
                         if argument > 0
                         else (int(argument) + (0x1 << size)))
            return Uint(size, new_value)

        raise TypeError(
            f"Invalid operation 'coercion' for types `uint[{size}]` and '{type(argument).__name__}'"
        )

    def __getitem__(self, subscript):
        """Get one or more bits from the classical type.

        :param subscript: int/List[int]/slice for indexing the Uint type.
        """
        if isinstance(subscript, int):
            if subscript in range(0, self._size):
                result = (self._value & (0x1 << subscript)) >> subscript
                return Uint(2, int(result))
            # TODO: Think of providing some error localization and variable name here
            raise IndexError(f"Index value '{subscript}' is out of range.")

        elif isinstance(subscript, slice):
            bit_str = f"{self._value:b}".zfill(self._size)
            result = bit_str[::-1][subscript][::-1]
            return Uint(len(result) + 1, int(result, 2))

        else:
            raise TypeError(
                f"Expected 'int/uint' or 'slice' in subscript, found '{type(subscript)}'."
            )

    def __repr__(self) -> str:
        """Representation of the Uint type while printing the value."""
        return f"<{type(self).__name__}[{self._size}]: {self._value}>"

    def __str__(self) -> str:
        """Stringify the Uint type while printing the value."""
        return f"<{type(self).__name__}[{self._size}]: {self._value}>"

    # Overloading arithmetic operations
    def __add__(self, other: ty.Any):
        if isinstance(other, int):
            return Uint(self._size, int(self._value + other))

        if isinstance(other, float):
            return float(self._value + other)

        if isinstance(other, (Uint, Angle, BitArray)):
            return Uint(self._size, int(self._value + other.value))

        if isinstance(other, Int):
            return Int(self._size, int(self._value + other.value))

        raise InvalidOperation("+", self, other)

    def __sub__(self, other: ty.Any):
        if isinstance(other, int):
            return Uint(self._size, int(self._value - other))

        if isinstance(other, float):
            return float(self._value - other)

        if isinstance(other, (Uint, Angle, BitArray)):
            return Uint(self._size, int(self._value - other.value))

        if isinstance(other, Int):
            return Int(self._size, int(self._value - other.value))

        raise InvalidOperation("-", self, other)

    def __mul__(self, other: ty.Any):
        if isinstance(other, int):
            return Uint(self._size, int(self._value * other))

        if isinstance(other, float):
            return float(self._value * other)

        if isinstance(other, (Uint, Angle, BitArray)):
            return Uint(self._size, int(self._value * other.value))

        if isinstance(other, Int):
            return Int(self._size, int(self._value * other.value))

        raise InvalidOperation("*", self, other)

    def __truediv__(self, other: ty.Any):
        if isinstance(other, int):
            return Uint(self._size, int(self._value / other))

        if isinstance(other, float):
            return float(self._value / other)

        if isinstance(other, (Uint, Angle, BitArray)):
            return Uint(self._size, int(self._value / other.value))

        if isinstance(other, Int):
            return Int(self._size, int(self._value / other.value))

        raise InvalidOperation("/", self, other)

    def __mod__(self, other: ty.Any):
        if isinstance(other, int):
            return Uint(self._size, int(self._value % other))

        if isinstance(other, float):
            return float(self._value % other)

        if isinstance(other, (Uint, Angle, BitArray)):
            return Uint(self._size, int(self._value % other.value))

        if isinstance(other, Int):
            return Int(self._size, int(self._value % other.value))

        raise InvalidOperation("%", self, other)

    def __pow__(self, other: ty.Any):
        if isinstance(other, (int, float)):
            return Uint(self._size, int(self._value ** other))

        if isinstance(other, (Int, Uint, Angle, BitArray)):
            return Uint(self._size, int(self._value ** other.value))

        raise InvalidOperation("**", self, other)

Uint.__name__ = "uint"


class Angle(ClassicalType):
    """Class for Angle type in the Translator"""

    def __init__(self, size: int, value: float):
        """Initialise a Angle type.

        :param size: number of bits contained in the type. Should be
            stricly positive.
        :param value: the value to be stored in the Angle type.
        """
        if value < 0 or value > 2*math.pi:
            raise OverflowError(
                f"Not enough bits in the `{type(self).__name__}[{size}]` type to store result."
            )

        super().__init__(size)
        self._value = self._to_bits(value)

    def _to_bits(self, value):
        """Helper function to convert from float representation to bit representation

        :param value: Value to be converted.
        """
        return int((value % (2*math.pi)) * ((0x1 << self._size)-1) / (2 * math.pi))

    def _to_angle(self, value):
        """Helper function to convert from bit representation to float representation

        :param value: Value to be converted.
        """
        return value * (2 * math.pi) / ((0x1 << self._size)-1)

    @property
    def value(self) -> float:
        """Return the value of the underlying type."""
        return self._to_angle(self._value)

    @value.setter
    def value(self, rhs: ty.Any) -> None:
        """Set the value of the underlying type.

        :param rhs: the RHS value to be stored in Angle type object.
        """
        if isinstance(rhs, (int, float)):
            if rhs < 0 or rhs > 2*math.pi:
                raise OverflowError(
                    f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result."
                )
            self._value = self._to_bits(rhs)

        elif isinstance(rhs, Angle):
            if rhs.size > self._size:
                raise OverflowError(
                    f"Not enough bits in the `{type(self).__name__}[{self._size}]` type to store result."
                )
            self._value = rhs.value

        else:
            raise TypeError(
                f"Cannot store '{type(rhs).__name__}' type value in `{type(self).__name__}[{self._size}]` type."
            )

    @staticmethod
    def cast(
        argument: ty.Union[ClassicalType, QuantumRegister, TimingType, float, bool],
        size: ty.Optional[int] = None
    ):
        """Cast a particular varible to Angle type.

        :param argument: Argument wihin the cast statement.
        :param size: Size of the Int returned
        """

        size = _get_type_size(argument) if size is None else size
        if isinstance(argument, (Int, Uint, TimingType, QuantumRegister)):
            cast_size = "" if size is None else f"[{size}]"
            raise TypeError(
                f"`{type(argument).__name__}` type cannot be cast into a `angle{cast_size}` type."
            )

        if isinstance(argument, BitArray):
            return Angle(size, argument.value)

        if isinstance(argument, Angle):
            return Angle(size, argument.value)

        if isinstance(argument, float):
            new_value = (int(argument)
                         if argument > 0
                         else (int(argument) + (0x1 << size)))
            return Angle(size, new_value)

        raise TypeError(
            f"Invalid operation 'coercion' for types `angle[{size}]` and '{type(argument).__name__}'"
        )

    def __getitem__(self, subscript):
        """Get one or more bits from the classical type.

        :param subscript: int/List[int]/slice for indexing the Angle type.
        """
        if isinstance(subscript, int):
            if subscript in range(0, self._size):
                result = (self._value & (0x1 << subscript)) >> subscript
                return Angle(2, int(result))
            # TODO: Think of providing some error localization and variable name here
            raise IndexError(f"Index value '{subscript}' is out of range.")

        elif isinstance(subscript, slice):
            bit_str = f"{self._value:b}".zfill(self._size)
            result = bit_str[::-1][subscript][::-1]
            return Angle(len(result) + 1, int(result, 2))

        else:
            raise TypeError(
                f"Expected 'int/uint' or 'slice' in subscript, found '{type(subscript)}'."
            )

    def __repr__(self) -> str:
        """Representation of the Angle type while printing the value."""
        pi_coeff = 2 * self._value / ((0x1 << self._size) - 1)
        return f"<{type(self).__name__}[{self._size}]: {pi_coeff}π>"

    def __str__(self) -> str:
        """Stringify the Angle type while printing the value."""
        pi_coeff = 2 * self._value / ((0x1 << self._size) - 1)
        return f"<{type(self).__name__}[{self._size}]: {pi_coeff}π>"

    # Overloading arithmetic operations
    def __add__(self, other: ty.Any):
        if isinstance(other, int):
            return Angle(self._size, int(self._value + other))

        if isinstance(other, float):
            return float(self._value + other)

        if isinstance(other, (Int, Uint, Angle, BitArray)):
            return Angle(self._size, int(self._value + other.value))

        raise InvalidOperation("+", self, other)

    def __sub__(self, other: ty.Any):
        if isinstance(other, int):
            return Angle(self._size, int(self._value - other))

        if isinstance(other, float):
            return float(self._value - other)

        if isinstance(other, (Int, Uint, Angle, BitArray)):
            return Angle(self._size, int(self._value - other.value))

        raise InvalidOperation("-", self, other)

    def __mul__(self, other: ty.Any):
        if isinstance(other, int):
            return Angle(self._size, int(self._value * other))

        if isinstance(other, float):
            return float(self._value * other)

        if isinstance(other, (Int, Uint, Angle, BitArray)):
            return Angle(self._size, int(self._value * other.value))

        raise InvalidOperation("*", self, other)

    def __truediv__(self, other: ty.Any):
        if isinstance(other, int):
            return Angle(self._size, int(self._value / other))

        if isinstance(other, float):
            return float(self._value / other)

        if isinstance(other, (Int, Uint, Angle, BitArray)):
            return Angle(self._size, int(self._value / other.value))

        raise InvalidOperation("/", self, other)

    def __mod__(self, other: ty.Any):
        if isinstance(other, int):
            return Angle(self._size, int(self._value % other))

        if isinstance(other, float):
            return float(self._value % other)

        if isinstance(other, (Int, Uint, Angle, BitArray)):
            return Angle(self._size, int(self._value % other.value))

        raise InvalidOperation("%", self, other)

    def __pow__(self, other: ty.Any):
        if isinstance(other, (int, float)):
            return Angle(self._size, int(self._value ** other))

        if isinstance(other, (Int, Uint, Angle, BitArray)):
            return Angle(self._size, int(self._value ** other.value))

        raise InvalidOperation("**", self, other)

Angle.__name__ = "angle"


ComplexValueType = ty.Optional[ty.Union[ClassicalType, float]]

class Complex:
    """Class for Complex type in the Translator"""

    def __init__(
        self, real: ComplexValueType = None, imag: ComplexValueType = None
    ):
        """Initialise a Complex type.

        :param real: Real part of the complex number
        :param imag: Imaginary part of the complex number
        """
        self._type = type(real) if real is not None else (type(imag) if imag is not None else float)
        self._real: ComplexValueType = real if real is not None else self._type(0)
        self._imag: ComplexValueType = imag if imag is not None else self._type(0)

    @property
    def real(self) -> ComplexValueType:
        """Return the real part of the complex number."""
        return self._real

    @property
    def imag(self) -> ComplexValueType:
        """Return the imaginary part of the complex number."""
        return self._imag

    def __repr__(self) -> str:
        """Representation of the complex type while printing the value."""
        return f"<{type(self).__name__}[{self._type.__name__}]: {self._real}+{self._imag}im>"

    def __str__(self) -> str:
        """Stringify the complex type while printing the value."""
        return f"<{type(self).__name__}[{self._type.__name__}]: {self._real}+{self._imag}im>"

    # Overload arithmetic operations
    def __add__(self, other: Complex):
        res_real = self._real + other.real
        res_imag = self._imag + other.imag
        return Complex(res_real, res_imag)

    def __sub__(self, other: Complex):
        res_real = self._real - other.real
        res_imag = self._imag - other.imag
        return Complex(res_real, res_imag)

    def __mul__(self, other: Complex):
        res_real = self._real * other.real - self._imag * other.imag
        res_imag = self._imag * other.real + self._real * other.imag
        return Complex(res_real, res_imag)

    def __truediv__(self, other: Complex):
        other_conj = Complex(other.real, -other.imag)
        res = self * other_conj
        mag2 = other * other_conj
        return Complex(res.real/mag2, res.imag/mag2)

Complex.__name__ = "complex"


class Duration(TimingType):
    def __init__(self, value: ty.Union[int, float], unit: qasm_ast.TimeUnit):
        super().__init__(unit)
        self._value = value

    @staticmethod
    def _convert_units(src_unit: qasm_ast.TimeUnit, dest_unit: qasm_ast.TimeUnit):
        unit_conversion_dict = {
            qasm_ast.TimeUnit.ns: 1,
            qasm_ast.TimeUnit.us: 10**3,
            qasm_ast.TimeUnit.ms: 10**6,
            qasm_ast.TimeUnit.s: 10**9
        }

        if src_unit == dest_unit:
            return 1
        if src_unit == qasm_ast.TimeUnit.dt and dest_unit != qasm_ast.TimeUnit.dt:
            raise TypeError("Time units cannot be matched.")
        if dest_unit == qasm_ast.TimeUnit.dt and src_unit != qasm_ast.TimeUnit.dt:
            raise TypeError("Time units cannot be matched.")

        return unit_conversion_dict[src_unit] / unit_conversion_dict[dest_unit]


    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, rhs: ty.Union[int, float]) -> None:
        """Set the value of the underlying type.

        :param rhs: the RHS value to be stored in Duration type object.
        """
        if isinstance(rhs, (int, float)):
            self._value = rhs

        else:
            raise TypeError(
                f"Cannot store '{type(rhs).__name__}' type value in `{type(self).__name__}<{self._unit}>` type."
            )

    def __repr__(self) -> str:
        """Representation of the complex type while printing the value."""
        return f"<{type(self).__name__}: {self._value}{self._unit.__name__}>"

    def __str__(self) -> str:
        """Stringify the complex type while printing the value."""
        return f"<{type(self).__name__}: {self._value}{self._unit.__name__}>"

    # Overloading arithmetic operations
    def __add__(self, other):
        if isinstance(other, TimingType):
            conversion_factor = self._convert_units(other.unit, self._unit)
            converted_other = other.value * conversion_factor
            return Duration(self._value + converted_other, self._unit)

        raise InvalidOperation("+", self, other)

    def __sub__(self, other):
        if isinstance(other, TimingType):
            conversion_factor = self._convert_units(other.unit, self._unit)
            converted_other = other.value * conversion_factor
            return Duration(self._value - converted_other, self._unit)

        raise InvalidOperation("-", self, other)

    def __mul__(self, other):
        if isinstance(other, (ClassicalType, int, float)):
            conversion_factor = self._convert_units(other.unit, self._unit)
            converted_other = other * conversion_factor
            return Duration(self._value * converted_other, self._unit)

        raise InvalidOperation("*", self, other)

    def __truediv__(self, other):
        if isinstance(other, (ClassicalType, int, float)):
            conversion_factor = self._convert_units(other.unit, self._unit)
            converted_other = other * conversion_factor
            return Duration(self._value / converted_other, self._unit)

        if isinstance(other, TimingType):
            conversion_factor = self._convert_units(other.unit, self._unit)
            converted_other = other.value * conversion_factor
            return float(self._value / converted_other)

        raise InvalidOperation("/", self, other)


class Stretch(TimingType):
    def __init__(self, unit: qasm_ast.TimeUnit):
        # Not implemented because the usage not clear.
        raise NotImplementedError("Stretch type is not implemented yet.")

# TODO list:
# 1. BitArray: List[Optional[bool]] --> Optional[str]                             [√]
# 2. BitArray.value returns int                                                   [√]
# 3. BitArray bitwise operations implementation (including rotr, rotl, popcount)  [√]
# 4. Logical and comparison operators (&&, ||, ==, !=, etc) overloading           [ ]
# 5. Fix operations between Angle and other ClassicalTypes                        [ ]
# 6. Duration: Casting to `machine-precision` float (Let OpenPulse handle that)   [√]
# 7. Stretch: How should we do this... (Not Implemented)                          [√]
