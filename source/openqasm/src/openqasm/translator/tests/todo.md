# Changes TODO in the code
## Remove `get_register`
- Potential changes:
	- Generate new instance of `ClassicalRegister` in the `_process_QuantumMeasurementAssignment`
	- Perform `circuit.add_register()`
	- Perform `cl_identifier.add_register()`
- Will make the syntax for measurement operation easier and constant with the other things that use `get_identifier` instead.
- **Problems:**
	- Need some way to not process `IndexIdentifier`, and perform indexing/selection/slicing on the `ClassicalRegister` instead.
	- Conflict with language specification as it gives a way to add register to types other than `BitArrayType` as well.

## BranchingStatement
- Determine if the condition is a measurement result that is stored in a `ClassicalRegister` object using `ClassicalType.get_register()`.
- **If** register is **None**, then go for `_process_Statement`
- **Else** use `c_if` with the quantum gates inside the if-else block.

## ForInLoop
- Determine is loop is constant time unrollable or not.
- Have to look ahead in the AST for evaluating unrollability.

- **Unrollable:**
	- Only consisting of quantum gates.
	- Just unroll the loop into a serial set of quantum gates.

- **Non-unrollable:**
	- Consisting of measurements, classical operations, etc.
	- Generate a separate quantum circuit for the loop block and then use `qc.compose()` to join initial circuit with circuit for each iter.
	- **Problem:** The number of circuits will grow exponentially for nested loops.

## All `attrs`
- Accept a list of `QuantumCircuit` objects.
	- **First instance:** main circuit.
	- **Subsequenct instances:** circuit for each iteration.

## translate()
- Return a list of `QuantumCircuit` objects.
