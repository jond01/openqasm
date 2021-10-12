import pytest
import math
from qiskit.circuit.classicalregister import ClassicalRegister as QiskitClassicalRegister
from qiskit.circuit.quantumregister import QuantumRegister as QiskitQuantumRegister

from openqasm.translator.bitarray import (
    RegisterView, RegisterConcatenation, QuantumRegister,
    BaseBitArray, OwningBitArray, NonOwningBitArray
)

def test_owningbitarray_decl():
    cr = QiskitClassicalRegister(4, name='cr1')
    value_str = "1101"
    value = [True if i == '1' else False for i in reversed(value_str)]
    b = OwningBitArray(cr, value)

    assert b.size == 4
    assert b.value == value

def test_owningbitarray_indexing():
    cr = QiskitClassicalRegister(4, name='cr1')
    value_str = "1101"
    value = [True if i == '1' else False for i in reversed(value_str)]
    b = OwningBitArray(cr, value)

    b_idx = b[0]
    assert b_idx.size == 1
    assert b_idx._indices == [0]
    assert b_idx._register == b

    b_idxs = b[[1, 2]]
    assert b_idxs.size == 2
    assert b_idxs._indices == [1, 2]
    assert b_idxs._register == b

    b_slice = b[0:3]
    assert b_slice.size == 3
    assert b_slice._indices == [0, 1, 2]
    assert b_slice._register == b
