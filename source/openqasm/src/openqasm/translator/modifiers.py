from qiskit.circuit.gate import Gate as QiskitGate

from openqasm.ast import GateModifierName, QuantumGateModifier
from openqasm.translator.context import OpenQASMContext
from openqasm.translator.exceptions import MissingExpression
from openqasm.translator.expressions import compute_expression


def apply_modifier(
    gate: QiskitGate, modifier: QuantumGateModifier, context: OpenQASMContext
) -> QiskitGate:
    """Apply the given modifier to the given quantum gate."""
    modifier_name: GateModifierName = modifier.modifier
    if modifier_name in {GateModifierName.ctrl, GateModifierName.negctrl}:
        number_of_ctrl: int = 1
        if modifier.argument is not None:
            number_of_ctrl = compute_expression(modifier.argument, context)
        ctrl_state = "1" if modifier_name == GateModifierName.ctrl else "0"
        return gate.control(num_ctrl_qubits=number_of_ctrl, ctrl_state=ctrl_state * number_of_ctrl)
    elif modifier_name == GateModifierName.inv:
        return gate.inverse()
    elif modifier_name == GateModifierName.pow:
        if modifier.argument is None:
            raise MissingExpression("pow modifier")
        power: float = compute_expression(modifier.argument, context)
        return gate.power(power)
    else:
        raise RuntimeError(f"Gate modifier '{modifier_name.name}' unknown.")
