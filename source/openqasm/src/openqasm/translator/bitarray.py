"""Implement all the types related to (qu)bit arrays."""

import typing as ty
from abc import ABC, abstractmethod

from qiskit.circuit.classicalregister import \
    ClassicalRegister as QiskitClassicalRegister
from qiskit.circuit.quantumregister import \
    QuantumRegister as QiskitQuantumRegister


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


BitArrayValueType = ty.Optional[ty.List[ty.Optional[bool]]]


class BaseBitArray:
    """Base class representing an array of classical bits."""

    def __init__(self, size: int, value: BitArrayValueType):
        """Initialise a BaseBitArray with the given value.

        :param size: number of bits contained in the array.
        :param value: None if the bit array is not initialised, else the actual
            value held by the classical bit array. Any individual bit can
            potentially be uninitialised.
        """
        self._size = size
        # Default value for self._value
        self._value: ty.List[ty.Optional[bool]] = value if value is not None else []
        # Pad with None if needed
        self._value += [None for _ in range(size - len(self._value))]

    @property
    def value(self) -> BitArrayValueType:
        return self._value

    def __setitem__(
        self, indices: ty.Union[int, ty.List[int], slice], value: ty.Union[bool, ty.Sequence[bool]]
    ) -> None:
        """Set the indexed bits to the given value.

        :param indices: any indices that is compatible. If only one index is
            provided, the value is supposed to be a boolean. If more than one
            index is provided, the value should be a type that support indexing
            and "value[i]" should return a boolean for any valid value of i.
        :param value:
        """
        transformed_indices: ty.List[int] = _get_indices(len(self._value), indices)
        if len(transformed_indices) == 1 and isinstance(value, bool):
            self._value[transformed_indices[0]] = value
        elif len(transformed_indices) > 1 and isinstance(value, ty.Sequence):
            for i in transformed_indices:
                self._value[i] = value[i]
        else:
            raise RuntimeError(
                f"Incompatible types for indices ({type(indices).__name__}) "
                f"and value ({type(value).__name__})"
            )


class NonOwningBitArray(BaseBitArray):
    """A bit array that does not own any classical register."""


class OwningBitArray(Register, BaseBitArray):
    """A bit array that owns a classical register."""

    def __init__(self, register: QiskitClassicalRegister, value: BitArrayValueType):
        """Construct a bit array owning a qiskit.ClassicalRegister instance."""
        Register.__init__(self, register.size)
        BaseBitArray.__init__(self, register.size, value)
        self._register: QiskitClassicalRegister = register

    def __setitem__(self, indices: ty.Union[int, ty.List[int], slice], value: ty.Any) -> None:
        """Set one or more items from a register."""
        BaseBitArray.__setitem__(self, indices, value)

    @property
    def bits(self) -> ty.List[QiskitQuantumRegister]:
        return [self._register[i] for i in range(self.size)]
