"""
test.py ... placeholder for pytest unit test suite
This file currently tests openqasm.translator.types

@author: AbeerVaishnav13 on github.com
@author: jwoehr on github.com
"""

import pytest
import math

from openqasm.translator.types import (
    UnsignedIntegerType,
    BitArrayType,
    SignedIntegerType,
    AngleType,
    ClassicalType,
)

from openqasm.translator.exceptions import InvalidOperation, InvalidTypeAssignment

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

    # expected pass
    c2 = a1 + s2
    assert isinstance(c2, SignedIntegerType)
    assert c2 == SignedIntegerType(4, -1)

    d1 = a1 - s1
    assert isinstance(d1, SignedIntegerType)
    assert d1 == SignedIntegerType(4, -1)

    # expected fail - OverflowError
    with pytest.raises((AssertionError, OverflowError, TypeError, InvalidOperation, InvalidTypeAssignment)):
        c1 = a1 + s1
        assert isinstance(c1, SignedIntegerType)
        assert c1 == SignedIntegerType(4, 11)

    # expected fail - OverflowError
    with pytest.raises((AssertionError, OverflowError, TypeError, InvalidOperation, InvalidTypeAssignment)):
        d2 = a1 - s2
        assert isinstance(d2, SignedIntegerType)
        assert d2 == SignedIntegerType(4, 11)


def test_uint_type_coercion():
    a = UnsignedIntegerType(4, 5)
    s = SignedIntegerType(4, 6)
    a = UnsignedIntegerType.cast(s, a.size)
    assert a == UnsignedIntegerType(4, 6)

    s2 = SignedIntegerType(4, -6)
    a = UnsignedIntegerType.cast(s2, a.size)

    # Should wrap-around (2**n)-1
    assert a == UnsignedIntegerType(4, 10)


def test_int_type_coercion():
    a = UnsignedIntegerType(3, 5)
    s = SignedIntegerType(4, 6)

    s = SignedIntegerType.cast(a, s.size)
    assert s == SignedIntegerType(4, 5)

    a2 = UnsignedIntegerType(4, 14)
    s = SignedIntegerType.cast(a2, s.size)
    assert s == SignedIntegerType(4, -2)

    s2 = SignedIntegerType(5, 6)
    s2 = SignedIntegerType.cast(a2, s2.size)
    assert s2 == SignedIntegerType(5, 14)


def test_int_uint_float_operations():
    s2 = SignedIntegerType(10, 3)
    u2 = UnsignedIntegerType(10, 2)

    pow1 = u2 ** s2
    assert isinstance(pow1, UnsignedIntegerType)
    assert pow1 == UnsignedIntegerType(10, 8)

    pow2 = u2 ** -s2
    assert pow2 == UnsignedIntegerType(10, 0)

    pow3 = u2 ** 0.5
    assert pow3 == UnsignedIntegerType(10, 1)

    pow4 = s2 ** u2
    assert isinstance(pow4, SignedIntegerType)
    assert pow4 == SignedIntegerType(10, 9)

    pow5 = s2 ** -u2
    assert pow5 == SignedIntegerType(10, 0)

    pow6 = s2 ** 0.5
    assert pow6 == SignedIntegerType(10, 1)

    pow7 = 0.5 ** u2.value
    assert pow7 == float(0.25)

    pow8 = 0.5 ** -s2.value
    assert pow8 == float(8)

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
    s = BitArrayType(4, "1101", "my_BitArray")
    assert s.size == 4
    assert s.value == "1101"


def test_BitArrayType_declaration_fails_negative():
    # expected fail -- neg bitvalue
    with pytest.raises((AssertionError, OverflowError, ValueError, InvalidOperation, InvalidTypeAssignment)):
        s = BitArrayType(4, "-1101", "my_BitArray")
        assert s.size == 4
        assert s.value == "-1101"


def test_BitArrayType_declaration_fails_size():
    # expected fail -- too wide
    with pytest.raises((AssertionError, OverflowError, ValueError, InvalidOperation, InvalidTypeAssignment)):
        s = BitArrayType(4, "11101", "my_BitArray")
        assert s.size == 4
        assert s.value == "11101"


def test_BitArrayType_cast_passes():
    # expected pass
    ba = BitArrayType(5, "11010")
    ba = BitArrayType.cast(25.0, ba.size)
    assert ba.size == 5
    assert ba.value == "11001"

    s = SignedIntegerType(4, 5)
    ba = BitArrayType.cast(s, ba.size)
    assert ba.size == 5
    assert ba.value == "00101"


def test_BitArrayType_cast_fails_size():
    # expected fail -- too wide
    with pytest.raises((AttributeError, AssertionError, OverflowError, ValueError, InvalidOperation, InvalidTypeAssignment)):
        ba = BitArrayType(4, "1101")
        ba = BitArrayType.cast("25", ba.size)
        assert ba.size == 4
        assert ba.value == "11001"


def test_BitArrayType_cast_subscript():
    b = BitArrayType(3, '110')
    assert b[:2] == BitArrayType(2, "10")
    assert b[0] == BitArrayType(1, "0")

    b.value = "011"
    assert b == BitArrayType(3, "011")
    assert b[1:] == BitArrayType(2, "01")

def test_AngleType_declaration():
    a = AngleType(4, 3)
    assert a.size == 4
    assert a.value == 3*math.tau/(2**4-1)

def test_AngleType_fails_negative_decl():
    with pytest.raises((AssertionError, OverflowError, TypeError, ValueError, InvalidOperation, InvalidTypeAssignment)):
        a = AngleType(4, -12)
        assert a.size == 4
        assert a.value == -12

def test_AngleType_cast_passes():
    a = AngleType(4, 3)
    a = AngleType.cast(12, a.size)
    assert a == AngleType(4, 12)

    b = BitArrayType(4, "10")
    a = AngleType.cast(b, a.size)
    assert a == AngleType(4, 2)

def test_AngleType_cast_fails():
    a = AngleType(4, 0)
    b = BitArrayType(5, "10")

    # expected fail
    with pytest.raises((AssertionError, OverflowError, TypeError, ValueError, InvalidOperation, InvalidTypeAssignment)):
        # fail reason - TypeError
        a.value = b

        # fail reason - OverflowError
        a = AngleType.cast(b, a.size)
        assert a == AngleType(4, 2)

def test_angle_operations():
    angle = AngleType(4, 3)
    temp = angle << 2

    assert isinstance(temp, AngleType)
    assert temp == AngleType(4, 12)
