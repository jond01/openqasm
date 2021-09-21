import typing as ty


class ClassicalType:
    def __init__(self, size: int):
        self._size: int = size

    @property
    def size(self) -> int:
        return self._size


class BitArrayType(ClassicalType):
    def __init__(self, size: int, value: str):
        super().__init__(size)
        # TODO check that this is little-endian
        self._value: ty.List[bool] = [v == "1" for v in reversed(value)]

    def __getitem__(self, index: int) -> bool:
        return self._value[index]

    def __setitem__(self, index: int, value: bool) -> None:
        self._value[index] = value


class NumericType(ClassicalType):
    def __init__(self, size: int, value: ty.Union[int, float]):
        super().__init__(size)
        self._value: ty.Union[int, float] = value

    @property
    def value(self) -> ty.Union[int, float]:
        return self._value

    # TODO: define the operators for all the numeric types here?


class SignedIntType(NumericType):
    def __init__(self, size: int, value: int):
        super().__init__(size, value)
        self._value: int = value


class UnsignedIntType(NumericType):
    def __init__(self, size: int, value: int):
        super().__init__(size, value)


class FloatingPointType(NumericType):
    def __init__(self, size: int, value: float):
        super().__init__(size, value)


class FixedPointAngleType(NumericType):
    def __init__(self, size: int, value: float):
        super().__init__(size, value)


class ComplexNumberType(ClassicalType):
    def __init__(
        self,
        type_: ty.Type[ClassicalType],
        size: int,
        real_part: ClassicalType,
        complex_part: ClassicalType,
    ):
        pass
