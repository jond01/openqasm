OPENQASM 3.0;

include "stdgates.inc";

gate my_gate a, b, c {
	cx a, b;
	cx b, c;
}

const n = 5;
qubit[3] q;
uint[3] c;

h q;

for i in [0: n] {
	my_gate q[0], q[1], q[2];
	c[0] = measure q[0];
	c[1] = measure q[1];
	c[2] = measure q[2];
}
