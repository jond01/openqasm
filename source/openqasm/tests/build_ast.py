from pathlib import Path

from openqasm.ast import ForInLoop
from openqasm.parser.antlr.qasm_parser import parse

HERE_DIR = Path("__file__").parent.absolute()
EXAMPLE_DIR = HERE_DIR.parent.parent.parent / "examples"

try_translation = True
pretty_print = False
verbose = True

if try_translation:
    from openqasm.translator.translator import OpenQASM3Translator

    translator = OpenQASM3Translator(EXAMPLE_DIR/"ipe.qasm", [EXAMPLE_DIR])
    circuit = translator.translate()
    print(circuit.draw())


ast = translator.program_ast

if pretty_print:
    from openqasm.ast_printer import pretty_print
    pretty_print(ast)


if verbose:
    print(f"Found {len(ast.statements)} statements.")
    print(f"Found OpenQASM version {ast.version['major']}.{ast.version['minor']}.")

    for i, statement in enumerate(ast.statements):
        print(f"Statement {i} is of type {type(statement).__name__}.")

    print("Listing for-loops...")
    for i, statement in enumerate(ast.statements):
        if not isinstance(statement, ForInLoop):
            continue
        # We have the first for-loop
        print(f"For-loop {i} body:")
        for j, node in enumerate(statement.block):
            print(f"  {j:>2} {type(node).__name__}")
