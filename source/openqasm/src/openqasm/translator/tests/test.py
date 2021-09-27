"""
test.py ... placeholder for pytest unit test suite
This file currently tests openqasm.translator.types

@author: AbeerVaishnav13 on github.com
@author: jwoehr on github.com
"""

import pytest

from openqasm.translator.types import (
    UnsignedIntegerType,
    BitArrayType,
    SignedIntegerType,
    AngleType,
    ClassicalType,
)

# Declaring a signed integer (int)
def test_SignedIntegerType_declaration():
    s = SignedIntegerType(4, 6)
    assert s.size == 4
    assert s.value == 6

    s = SignedIntegerType(4, -6)
    assert s.size == 4
    assert s.value == -6


def test_SignedIntegerType_assignment():
    s = SignedIntegerType(4, 6)
    s.value = -3
    assert s.value == -3

    s[0] = 0
    assert s[0] == 0
    assert s == SignedIntegerType(4, -4)


def test_SignedIntegerType_subscript():
    s = SignedIntegerType(4, 6)
    b = s[2]
    assert b == SignedIntegerType(2, 1)

    b = s[:2]
    assert b == SignedIntegerType(3, 2)


def test_UnsignedIntegerType_declaration():
    a = UnsignedIntegerType(4, 5)
    assert a.size == 4
    assert a.value == 5


def test_UnsignedIntegerType_assignment():
    a = UnsignedIntegerType(4, 5)
    a.value = 4
    assert a.value == 4

    a[1] = 1
    assert a.value == 6


def test_UnsignedIntegerType_subscript():
    a = UnsignedIntegerType(4, 6)
    b = a[2]
    assert b == UnsignedIntegerType(1, 1)

    b = a[:2]
    assert b == UnsignedIntegerType(2, 2)


def test_int_uint_operations():
    a1 = UnsignedIntegerType(4, 5)
    s1 = SignedIntegerType(4, 6)
    s2 = SignedIntegerType(4, -6)
    c1 = a1 + s1
    assert c1 == SignedIntegerType(5, 11)

    c2 = a1 + s2
    assert c2 == SignedIntegerType(5, -1)

    d1 = a1 - s1
    assert d1 == SignedIntegerType(5, -1)

    d2 = a1 - s2
    assert d2 == SignedIntegerType(5, 11)


def test_uint_type_coercion():
    a = UnsignedIntegerType(4, 5)
    s = SignedIntegerType(4, 6)
    a.value = a.coerce(s)
    assert a == UnsignedIntegerType(4, 6)

    s2 = SignedIntegerType(4, -6)
    a.value = a.coerce(s2)

    # Should wrap-around (2**n)-1
    assert a == UnsignedIntegerType(4, 10)


def test_int_type_coercion():
    a = UnsignedIntegerType(3, 5)
    s = SignedIntegerType(4, 6)

    s.value = s.coerce(a)
    assert s == SignedIntegerType(5, 5)

    a2 = UnsignedIntegerType(4, 14)
    s.value = s.coerce(a2)
    assert s == SignedIntegerType(5, -2)

    s2 = SignedIntegerType(5, 6)
    s2.value = s2.coerce(a2)
    assert s2 == SignedIntegerType(5, 14)


# 2021-09-26 jwoehr
# Test base class
#################
def test_ClassicalType():
    ct = ClassicalType(4, 4)
    assert ct.size == 4
    assert ct._value == 4  # no @property defined


# 2021-09-26 jwoehr
# Test bit array class
######################


def test_BitArrayType_declaration_passes():
    # expected pass
    s = BitArrayType(
        4,
        "1101",
        "my_BitArray",
    )
    assert s.size == 4
    assert int(s.value, 2) == 0b1101


def test_BitArrayType_declaration_fails_negative():
    # expected fail -- neg bitvalue
    with pytest.raises((AssertionError, OverflowError, ValueError)):
        s = BitArrayType(4, "-1101", "my_BitArray")
        assert s.size == 4
        assert int(s.value, 2) == -0b1101


def test_BitArrayType_declaration_fails_size():
    # expected fail -- too wide
    with pytest.raises((AssertionError, OverflowError, ValueError)):
        s = BitArrayType(4, "11101", "my_BitArray")
        assert s.size == 4
        assert int(s.value, 2) == 0b11101


def test_BitArrayType_coerce_passes():
    # expected pass
    # EXPECTED FAIL FOR WRONG REASON currently, code broken
    with pytest.raises((AttributeError, AssertionError, OverflowError, ValueError)):
        ba = BitArrayType.coerce(4, 25.0)
        assert ba.size == 5
        assert int(ba.value, 2) == 0b11001


def test_BitArrayType_coerce_fails_size():
    # expected fail -- too wide
    # FAILS FOR WRONG REASON
    with pytest.raises((AttributeError, AssertionError, OverflowError, ValueError)):
        ba = BitArrayType.coerce(4, "25")
        assert ba.size == 4
        assert int(ba.value, 2) == 0b11001


# s2 = SignedIntegerType(3, 3)
# u2 = UnsignedIntegerType(10, 2)
#
# pow1 = u2 ** s2
# print(f"{s2 = }")
# print(f"{u2 = }")
# print(f"{pow1 = }")
# print()
#
# pow2 = u2 ** 0.5
# print(f"{s2 = }")
# print(f"{u2 = }")
# print(f"{pow2 = }")
# print()
#
# pow3 = 0.5 ** u2.value
# print(f"{s2 = }")
# print(f"{u2 = }")
# print(f"{pow3 = }")
# print()
#
# b = BitArrayType(3, '110')
# b.value = '011'
# print(f"{b = }")
# print(f"{u2[1:]}")
# print(f"{b[1:] = }")
# print()
#
# a.value = UnsignedIntegerType.coerce(a.size, b)
#
# angle = AngleType(4, 3)
# print(f"{angle = }")
# print()
#
# temp = angle << 2
# print(f"{temp = }")
# print()
