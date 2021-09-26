from openqasm.translator.types import UnsignedIntegerType, BitArrayType, SignedIntegerType

# Declaring a signed integer (int)
s = SignedIntegerType(4, 6)
s.value = -3
s[0] = 1
print(f"{s = }")
print(f"{s[0] = }")
print()

b = s[:2]
print(f"{b = }")
print()

a = UnsignedIntegerType(4, 5)
print(f"{a = }")
a.value = 4
print(f"{-a = }")
print()

c = a + s
print(f"{a = }")
print(f"{s = }")
print(f"{c = }")
print()

a.value = UnsignedIntegerType.coerce(a.size, s)
print(f"{a = }")

s.value = SignedIntegerType.coerce(s.size, a)
print(f"{s = }")

s2 = SignedIntegerType(3, 3)
u2 = UnsignedIntegerType(10, 2)

pow1 = u2 ** s2
print(f"{s2 = }")
print(f"{u2 = }")
print(f"{pow1 = }")
print()

pow2 = u2 ** 0.5
print(f"{s2 = }")
print(f"{u2 = }")
print(f"{pow2 = }")
print()

pow3 = 0.5 ** u2.value
print(f"{s2 = }")
print(f"{u2 = }")
print(f"{pow3 = }")
print()

b = BitArrayType(3, '110')
b.value = '111'
print(f"{b[1:] = }")

a.value = b.value
