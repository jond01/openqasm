OPENQASM 3.0;

include "stdgates.inc";

gate my_gate a, b, c {
	cx a, b;
	cx b, c;
}

const n = 5;
qubit[n] q;
uint[n] c;

h q;

for i in [0: n-2] {
	my_gate q[i], q[i+1], q[i+2];
	h q[i];
	for j in [0: n] { c[j] = measure q[j]; }
}
