import inspect
import typing as ty

from qiskit import QuantumCircuit
from qiskit.circuit.gate import QuantumGate as QiskitQuantumGate
from qiskit.circuit.quantumregister import QuantumRegister

from openqasm.ast import (AliasStatement, AssignmentOperator, BinaryExpression,
                          BinaryOperator, BitType, BitTypeName, BooleanLiteral,
                          Box, BranchingStatement, BreakStatement,
                          CalibrationDefinition, CalibrationGrammarDeclaration,
                          ClassicalArgument, ClassicalAssignment,
                          ClassicalDeclaration, ClassicalType, ComplexType,
                          Concatenation, Constant, ConstantDeclaration,
                          ConstantName, ContinueStatement,
                          ControlDirectiveStatement, DelayInstruction,
                          DoubleDesignatorType, DoubleDesignatorTypeName,
                          DurationLiteral, DurationOf, EndStatement,
                          Expression, ExpressionStatement, ExternDeclaration,
                          ForInLoop, FunctionCall, GateModifierName,
                          Identifier, IndexExpression, IndexIdentifier,
                          IntegerLiteral, IODeclaration, IOIdentifierName,
                          NoDesignatorType, NoDesignatorTypeName, OpenNode,
                          Program, QuantumArgument, QuantumBarrier,
                          QuantumForInLoop, QuantumGate, QuantumGateDefinition,
                          QuantumGateModifier, QuantumInstruction,
                          QuantumMeasurement, QuantumMeasurementAssignment,
                          QuantumPhase, QuantumReset, QuantumStatement,
                          QuantumWhileLoop, Qubit, QubitDeclaration,
                          QubitDeclTypeName, RangeDefinition, RealLiteral,
                          ReturnStatement, Selection, SingleDesignatorType,
                          SingleDesignatorTypeName, Slice, Span, Statement,
                          StringLiteral, SubroutineDefinition, Subscript,
                          TimeUnit, TimingStatement, UnaryExpression,
                          UnaryOperator, WhileLoop)
from openqasm.translator.context import OpenQASMContext
from openqasm.translator.exceptions import UnsupportedFeature
from openqasm.translator.expressions import compute_expression
from openqasm.translator.identifiers import get_identifier
from openqasm.translator.modifiers import apply_modifier


class OpenQASM3Translator:
    """Translates an OpenQASM 3.0 AST into an instance of QuantumCircuit.

    The translation is still a work in progress. Any encountered unsupported
    feature will throw an exception that will describe what the issue was.

    In this class, a "feature" is one of the possible type for the AST nodes.
    An unsupported feature is then an AST node that cannot be processed because
    the processing code has not been implemented.

    Supported features (node types) can be listed using the
    OpenQASM3Translator.supported_features() static method.
    """

    NODE_PROCESSING_FUNCTIONS_PREFIX: str = "process_"

    def __init__(self, ast: Program):
        self._ast: Program = ast
        self._circuit: QuantumCircuit = QuantumCircuit()

    def translate(self) -> QuantumCircuit:
        """Translate the given AST to a QuantumCircuit instance.

        :return: the created QuantumCircuit instance.
        :throw UnsupportedFeature: if the AST contains at least one of the
            unsupported features.
        """
        circuit = QuantumCircuit()
        context = OpenQASMContext()
        for statement in self._ast.statements:
            statement_type: ty.Type = type(statement)
            statement_type_name: str = statement_type.__name__
            processing_function_name: str = (
                OpenQASM3Translator.NODE_PROCESSING_FUNCTIONS_PREFIX + statement_type_name
            )
            # If the node is not supported yet, raise an exception.
            if not hasattr(OpenQASM3Translator, processing_function_name):
                raise UnsupportedFeature(statement_type_name)
            # Process the node.
            getattr(OpenQASM3Translator, processing_function_name)(statement, circuit, context)
        return circuit

    @staticmethod
    def supported_features() -> ty.List[str]:
        """Return a list of the supported AST node types names."""
        prefix: str = OpenQASM3Translator.NODE_PROCESSING_FUNCTIONS_PREFIX
        return [
            method_name[len(prefix) :]
            for method_name, method in inspect.getmembers(
                OpenQASM3Translator, predicate=inspect.isfunction
            )
            if method_name.startswith(prefix)
        ]

    @staticmethod
    def process_QubitDeclaration(
        statement: QubitDeclaration, circuit: QuantumCircuit, context: OpenQASMContext
    ) -> None:
        """Process any QubitDeclaration node in the AST.

        The QubitDeclTypeName is not used because it is only used to make the
        AST retro-compatible with OpenQASM2, providing a way to distinguish
        between "qreg" and "qubit".

        :param statement: the AST node to process
        :param circuit: the QuantumCircuit instance to modify according to the
            AST node.
        :param context: the parsing context used to perform symbol lookup.
        """
        qubit: Qubit = statement.qubit
        designator: ty.Optional[Expression] = statement.designator

        quantum_register_size: int = 1  # Default value if designator is None
        if designator is not None:
            quantum_register_size = compute_expression(designator, context)
        register = QuantumRegister(size=quantum_register_size, name=qubit.name)
        circuit.add_register(register)
        context.add_symbol(qubit.name, register)

    @staticmethod
    def process_ConstantDeclaration(
        statement: ConstantDeclaration, circuit: QuantumCircuit, context: OpenQASMContext
    ) -> None:
        """Process any ConstantDeclaration node in the AST.

        :param statement: the AST node to process
        :param circuit: the QuantumCircuit instance to modify according to the
            AST node.
        :param context: the parsing context used to perform symbol lookup.
        """
        if statement.init_expression is None:
            context.declare_symbol(statement.identifier.name)
        else:
            context.add_symbol(
                statement.identifier.name, compute_expression(statement.init_expression, context)
            )

    @staticmethod
    def process_ClassicalDeclaration(
        statement: ClassicalDeclaration, circuit: QuantumCircuit, context: OpenQASMContext
    ) -> None:
        """Process any ClassicalDeclaration node in the AST.

        :param statement: the AST node to process
        :param circuit: the QuantumCircuit instance to modify according to the
            AST node.
        :param context: the parsing context used to perform symbol lookup.
        """
        type_: ClassicalType = statement.type
        name: str = statement.identifier.name
        init_expression: ty.Optional[Expression] = statement.init_expression
        raise UnsupportedFeature(
            ClassicalType.__name__,
            "Processing of the different ClassicalType is not implemented yet.",
        )

    @staticmethod
    def process_QuantumReset(
        statement: QuantumReset, circuit: QuantumCircuit, context: OpenQASMContext
    ) -> None:
        """Process any QuantumReset node in the AST.

        :param statement: the AST node to process
        :param circuit: the QuantumCircuit instance to modify according to the
            AST node.
        :param context: the parsing context used to perform symbol lookup.
        """
        for qubit in statement.qubits:
            circuit.reset(get_identifier(qubit, context))

    @staticmethod
    def process_QuantumGate(
        statement: QuantumGate, circuit: QuantumCircuit, context: OpenQASMContext
    ) -> None:
        """Process any QuantumGate node in the AST.

        :param statement: the AST node to process
        :param circuit: the QuantumCircuit instance to modify according to the
            AST node.
        :param context: the parsing context used to perform symbol lookup.
        """
        arguments: ty.List = [compute_expression(arg, context) for arg in statement.arguments]
        quantum_gate: QiskitQuantumGate = context.lookup(statement.name)(*arguments)
        qubits: ty.List = [get_identifier(qubit, context) for qubit in statement.qubits]

        for modifier in statement.modifiers:
            quantum_gate = apply_modifier(quantum_gate, modifier, context)

        circuit.append(quantum_gate, qargs=qubits)
