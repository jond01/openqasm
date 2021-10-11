import inspect
import typing as ty
from copy import deepcopy
from pathlib import Path

from qiskit.circuit import Parameter, QuantumCircuit
from qiskit.circuit.classicalregister import ClassicalRegister
from qiskit.circuit.gate import Gate as QiskitGate
from qiskit.circuit.library import PhaseGate, UGate
from qiskit.circuit.quantumregister import QuantumRegister

import openqasm.translator.types as ttypes
from openqasm.ast import (AliasStatement, AssignmentOperator, BinaryExpression,
                          BinaryOperator, BitType, BooleanLiteral,
                          Box, BranchingStatement, BreakStatement,
                          CalibrationDefinition, CalibrationGrammarDeclaration,
                          Cast, ClassicalArgument, ClassicalAssignment,
                          ClassicalDeclaration, ClassicalType, ComplexType,
                          Concatenation, Constant, ConstantDeclaration,
                          ConstantName, ContinueStatement,
                          ControlDirectiveStatement, DelayInstruction,
                          DurationLiteral, DurationOf, EndStatement,
                          Expression, ExpressionStatement, ExternDeclaration,
                          ForInLoop, FunctionCall, GateModifierName,
                          Identifier, IndexExpression, IndexIdentifier,
                          IntegerLiteral, IODeclaration, IOKeyword,
                          BoolType, DurationType, StretchType, OpenNode,
                          Program, QuantumArgument, QuantumBarrier,
                          QuantumForInLoop, QuantumGate, QuantumGateDefinition,
                          QuantumGateModifier, QuantumInstruction,
                          QuantumMeasurement, QuantumMeasurementAssignment,
                          QuantumPhase, QuantumReset, QuantumStatement,
                          QuantumWhileLoop, Qubit, QubitDeclaration,
                          RangeDefinition, RealLiteral,
                          ReturnStatement, Selection, IntType, UintType,
                          AngleType, FloatType, ComplexType, Slice, Span, Statement,
                          StringLiteral, SubroutineDefinition, Subscript,
                          TimeUnit, TimingStatement, UnaryExpression,
                          UnaryOperator, WhileLoop)
from openqasm.parser.antlr.qasm_parser import parse
from openqasm.translator.context import OpenQASMContext
from openqasm.translator.exceptions import (InvalidIncludePath,
                                            UnsupportedFeature, WrongRange)
from openqasm.translator.expressions import (compute_assignment,
                                             compute_expression)
from openqasm.translator.identifiers import get_identifier
from openqasm.translator.modifiers import apply_modifier
from openqasm.translator.types import get_typevar


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

    NODE_PROCESSING_FUNCTIONS_PREFIX: str = "_process_"

    def __init__(self, input_file: Path, include_dirs: ty.List[Path]):
        """Initialize the OpenQASM3Translator.

        :param input_file: The source file containing OpenQASM3 code.
        :param include_dirs: List of include paths for the include files.
        """
        with open(input_file, "r") as f:
            source = f.read()

        self._include_dirs = include_dirs
        self._program_ast = parse(source)

        include_files = [line.split('"')[1] for line in source.split("\n") if "include" in line]

        self._include_asts = []
        for include_file in include_files:
            is_existing_file: bool = True
            for path in include_dirs:
                is_existing_file = (path / include_file).is_file()
                if is_existing_file:
                    file_path: Path = path / include_file
                    with open(file_path, "r") as f:
                        include_source = f.read()
                        self._include_asts.append(parse(include_source))
                    break
            # If we finished the for-loop on a non-existing file, i.e. file not found.
            if not is_existing_file:
                raise InvalidIncludePath(include_file, self._include_dirs)

    def translate(self) -> QuantumCircuit:
        """Translate the given AST to a QuantumCircuit instance.

        :return: the created QuantumCircuit instance.
        :throw UnsupportedFeature: if the AST contains at least one of the
            unsupported features.
        """
        circuit = QuantumCircuit()
        context = OpenQASM3Translator._set_context(OpenQASMContext(), self._include_asts)
        for statement in self._program_ast.statements:
            OpenQASM3Translator._process_Statement(statement, circuit, context)
        return circuit

    @staticmethod
    def _set_context(context: OpenQASMContext, include_asts: ty.List[Program]) -> OpenQASMContext:
        """Generates an OpenQASMContext object and sets the initial context of the translator.

        :param context: An OpenQASMContext instance object.
        :param include_asts: List of AST for each include files.
        :return: The updated context.
        """
        context.add_symbol("U", lambda theta, phi, lambd: UGate(theta, phi, lambd), None)
        for inc in include_asts:
            for statement in inc.statements:
                OpenQASM3Translator._process_Statement(statement, None, context)
        return context

    @staticmethod
    def _process_Statement(
        statement: Statement, circuit: QuantumCircuit, context: OpenQASMContext
    ) -> ty.Any:
        """Process any general statement in the AST."""
        statement_type: ty.Type = type(statement)
        statement_type_name: str = statement_type.__name__
        processing_function_name: str = (
            OpenQASM3Translator.NODE_PROCESSING_FUNCTIONS_PREFIX + statement_type_name
        )
        # If the node is not supported yet, raise an exception.
        if not hasattr(OpenQASM3Translator, processing_function_name):
            raise UnsupportedFeature(statement_type_name)
        # Process the node.
        return getattr(OpenQASM3Translator, processing_function_name)(statement, circuit, context)

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
    def _process_QubitDeclaration(
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
        qubit: Qubit = statement.qubit.name
        size: ty.Optional[Expression] = statement.size

        quantum_register_size: int = 1  # Default value if designator is None
        if size is not None:
            quantum_register_size = compute_expression(size, context)
        register = QuantumRegister(size=quantum_register_size, name=qubit)
        circuit.add_register(register)
        context.add_symbol(qubit, register, statement.span)

    @staticmethod
    def _process_ConstantDeclaration(
        statement: ConstantDeclaration, circuit: QuantumCircuit, context: OpenQASMContext
    ) -> None:
        """Process any ConstantDeclaration node in the AST.

        :param statement: the AST node to process
        :param circuit: the QuantumCircuit instance to modify according to the
            AST node.
        :param context: the parsing context used to perform symbol lookup.
        """
        if statement.init_expression is None:
            context.declare_symbol(statement.identifier.name.name, statement.identifier.span)
        else:
            context.add_symbol(
                statement.identifier.name,
                compute_expression(statement.init_expression, context),
                statement.span,
            )

    @staticmethod
    def _process_ClassicalDeclaration(
        statement: ClassicalDeclaration, circuit: QuantumCircuit, context: OpenQASMContext
    ) -> None:
        """Process any ClassicalDeclaration node in the AST.

        :param statement: the AST node to process
        :param circuit: the QuantumCircuit instance to modify according to the
            AST node.
        :param context: the parsing context used to perform symbol lookup.
        """
        # TODO: is there anything to do with the type?
        type_: ClassicalType = statement.type
        size: int = compute_expression(type_.size, context)
        name: str = statement.identifier.name
        init_expression: ty.Optional[Expression] = statement.init_expression
        if init_expression is None:
            context.add_symbol(name, get_typevar(size, type_), statement.span)
        else:
            rhs_ = compute_expression(init_expression, context)
            context.add_symbol(name, get_typevar(size, type_, rhs_), statement.span)

    @staticmethod
    def _process_ClassicalAssignment(
        statement: ClassicalAssignment, circuit: QuantumCircuit, context: OpenQASMContext
    ) -> None:
        """Process any ClassicalAssignment node in the AST.

        :param statement: the AST node to process
        :param circuit: the QuantumCircuit instance to modify according to the
            AST node.
        :param context: the parsing context used to perform symbol lookup.
        """
        lhs = statement.lvalue
        rhs = compute_expression(statement.rvalue, context)
        compute_assignment(lhs, statement.op, rhs, context)

    @staticmethod
    def _process_QuantumBarrier(
        statement: QuantumBarrier, circuit: QuantumCircuit, context: OpenQASMContext
    ) -> None:
        """Process any QuantumBarrier node in the AST.

        :param statement: the AST node to process
        :param circuit: the QuantumCircuit instance to modify according to the
            AST node.
        :param context: the parsing context used to perform symbol lookup.
        """
        for qubit in statement.qubits:
            # Need a loop here because get_identifier will return a list of
            # results.
            for iden in get_identifier(qubit, context):
                circuit.barrier(iden)

    @staticmethod
    def _process_QuantumReset(
        statement: QuantumReset, circuit: QuantumCircuit, context: OpenQASMContext
    ) -> None:
        """Process any QuantumReset node in the AST.

        :param statement: the AST node to process
        :param circuit: the QuantumCircuit instance to modify according to the
            AST node.
        :param context: the parsing context used to perform symbol lookup.
        """
        for qubit in statement.qubits:
            # Need a loop here because get_identifier will return a list of
            # results.
            for iden in get_identifier(qubit, context):
                circuit.reset(iden)

    @staticmethod
    def _process_QuantumMeasurementAssignment(
        statement: QuantumMeasurementAssignment, circuit: QuantumCircuit, context: OpenQASMContext
    ) -> None:
        """Process any QuantumMeasurementAssignment node in the AST.

        :param statement: the AST node to process
        :param circuit: the QuantumCircuit instance to modify according to the
            AST node.
        :param context: the parsing context used to perform symbol lookup.
        """

        cl_identifier: ty.Union[Identifier, IndexIdentifier] = context.lookup(
            statement.lhs.name, statement.lhs.span
        )

        # TODO: add support for slice and selection as well
        subscript = compute_expression(statement.lhs.index, context)
        cl_register = ClassicalRegister(cl_identifier.size, name=statement.lhs.name)
        qubit = get_identifier(statement.measure_instruction.qubit, context)
        if not circuit.has_register(cl_register):
            circuit.add_register(cl_register)
            cl_identifier.set_register(cl_register)
        circuit.measure(qubit, cl_register[subscript])

    @staticmethod
    def _process_QuantumGate(
        statement: QuantumGate, circuit: QuantumCircuit, context: OpenQASMContext
    ) -> None:
        """Process any QuantumGate node in the AST.

        :param statement: the AST node to process
        :param circuit: the QuantumCircuit instance to modify according to the
            AST node.
        :param context: the parsing context used to perform symbol lookup.
        """
        arguments: ty.List = [compute_expression(arg, context) for arg in statement.arguments]
        quantum_gate: QiskitGate = context.lookup(statement.name.name, statement.span)(*arguments)
        qubits: ty.List = [get_identifier(qubit, context) for qubit in statement.qubits]

        for modifier in statement.modifiers:
            quantum_gate = apply_modifier(quantum_gate, modifier, context)
        circuit.append(quantum_gate, qargs=qubits)

    @staticmethod
    def _process_QuantumGateDefinition(
        statement: QuantumGateDefinition, circuit: QuantumCircuit, context: OpenQASMContext
    ) -> None:
        """Process any QuantumGateDefinition node in the AST.

        :param statement: the AST node to process
        :param circuit: the QuantumCircuit instance to modify according to the
            AST node.
        :param context: the parsing context used to perform symbol lookup.
        """
        argument_number: int = len(statement.arguments)
        quantum_gate_name: str = statement.name.name
        qubit_names: ty.List[str] = [q.name for q in statement.qubits]
        qubit_indices: ty.Dict[str, int] = {qn: qi for qi, qn in enumerate(qubit_names)}

        argument_names: ty.List[str] = [arg.name for arg in statement.arguments]

        # Creating the QuantumCircuit instance that will represent this gate
        # along with the context of the gate.
        gate_definition = QuantumCircuit(len(qubit_names), name=quantum_gate_name)
        gate_definition_context = deepcopy(context)
        for qubit, (qn, qi) in zip(statement.qubits, qubit_indices.items()):
            gate_definition_context.add_symbol(qn, qi, qubit.span)
        for arg, argname in zip(statement.arguments, argument_names):
            gate_definition_context.add_symbol(argname, Parameter(argname), arg.span)
        for st in statement.body:
            OpenQASM3Translator._process_Statement(st, gate_definition, gate_definition_context)

        def quantum_gate(
            *parameters: ty.Any,
            circ=gate_definition,
            argnames=argument_names,
            cont=gate_definition_context,
        ) -> QiskitGate:
            return circ.to_gate(
                {cont.lookup(argnames[i]): pvalue for i, pvalue in enumerate(parameters)}
            )

        context.add_symbol(quantum_gate_name, quantum_gate, statement.span)

    @staticmethod
    def _process_QuantumPhase(
        statement: QuantumPhase, circuit: QuantumCircuit, context: OpenQASMContext
    ) -> None:
        """Process any QuantumPhase node in the AST.

        :param statement: the AST node to process
        :param circuit: the QuantumCircuit instance to modify according to the
            AST node.
        :param context: the parsing context used to perform symbol lookup.
        """
        phase: float = compute_expression(statement.argument, context)
        # Getting the qubits as a list of entries.
        qubits: ty.List = []
        for qubit in statement.qubits:
            identifier = get_identifier(qubit, context)
            if isinstance(identifier, ty.Iterable):
                qubits.extend(identifier)
            else:
                qubits.append(identifier)
        # Applying the gate
        if not qubits:
            # Global phase on all the circuit if there is no qubits.
            circuit.global_phase += phase
        elif len(qubits) == 1:
            # ctrl @ gphase(...)
            # This is a phase gate
            circuit.append(PhaseGate(phase), qargs=qubits)
        else:
            raise UnsupportedFeature(QuantumPhase.__name__, "Too much qubits provided...")

    @staticmethod
    def _get_range(
        range_definition: ty.Union[RangeDefinition, ty.List[Expression], Identifier],
        context: OpenQASMContext,
    ) -> ty.Iterable:
        if isinstance(range_definition, RangeDefinition):
            rdef: RangeDefinition = range_definition
            # Getting the start, end and step values
            # TODO: start and end should not be required in the general setting.
            if rdef.start is None:
                raise WrongRange("start", rdef.span)
            if rdef.end is None:
                raise WrongRange("end", rdef.span)
            start = compute_expression(rdef.start, context)
            end = compute_expression(rdef.end, context)
            step = 1
            if rdef.step is not None:
                step = compute_expression(rdef.step, context)
            # Check that we have integers everywhere, else raise an
            # UnsupportedFeature exception.
            if not isinstance(start, int) or not isinstance(end, int) or not isinstance(step, int):
                raise UnsupportedFeature(
                    RangeDefinition.__name__, "Non integer start, stop or step."
                )
            return range(start, end, step)
        elif isinstance(range_definition, Identifier):
            return get_identifier(range_definition, context)
        else:
            return [compute_expression(expr, context) for expr in range_definition]

    @staticmethod
    def _process_ForInLoop(
        statement: ForInLoop, circuit: QuantumCircuit, context: OpenQASMContext
    ) -> None:
        """Process any ForInLoop node in the AST.

        :param statement: the AST node to process
        :param circuit: the QuantumCircuit instance to modify according to the
            AST node.
        :param context: the parsing context used to perform symbol lookup.
        """
        loop_context: OpenQASMContext = deepcopy(context)
        range_: ty.Iterable = OpenQASM3Translator._get_range(
            statement.set_declaration, loop_context
        )
        loop_context.declare_symbol(statement.loop_variable.name, statement.loop_variable.span)
        for i in range_:
            loop_context.modify_symbol(
                statement.loop_variable.name, i, statement.loop_variable.span
            )
            for st in statement.block:
                OpenQASM3Translator._process_Statement(st, circuit, loop_context)

    # TODO: Will there be any changes between quantum-if and classical-if?
    # quantum-if: qc.x(0).c_if(cr, 1)
    # classical-if: if(c == 1): qc.x(0)
    @staticmethod
    def _process_BranchingStatement(
        statement: BranchingStatement, circuit: QuantumCircuit, context: OpenQASMContext
    ) -> None:
        """Process any BrnahcingStatement node in the AST.

        :param statement: the AST node to process
        :param circuit: the QuantumCircuit instance to modify according to the
            AST node.
        :param context: the parsing context used to perform symbol lookup.
        """
        condition: bool = compute_expression(statement.condition, context)
        if condition:
            for st in statement.if_block:
                OpenQASM3Translator._process_Statement(st, circuit, context)
        elif statement.else_block is not None:
            for st in statement.else_block:
                OpenQASM3Translator._process_Statement(st, circuit, context)
