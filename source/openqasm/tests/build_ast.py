from pathlib import Path
import sys

from openqasm.ast import ForInLoop
from openqasm.parser.antlr.qasm_parser import parse

def verbose(ast):
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

def pprint_ast(ast):
    from openqasm.ast_printer import pretty_print
    pretty_print(ast)

def translate(input_file, include_dirs):
    from openqasm.translator.translator import OpenQASM3Translator

    translator = OpenQASM3Translator(input_file, include_dirs)
    circuit = translator.translate()
    print(circuit.draw())
    return translator.program_ast

def main():
    args = sys.argv
    input_file = args[1]
    include_dirs = []

    for i, arg in enumerate(args):
        if arg in ['-I', '--include-dir']:
            include_dirs.append(Path(args[i+1]))

    ast = translate(input_file, include_dirs)

    if '-v' in args or '--verbose' in args:
        verbose(ast)

    if '-pp' in args or '--pprint-ast' in args:
        pprint_ast(ast)


if __name__ == "__main__":
    main()
