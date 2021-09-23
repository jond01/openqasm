from pathlib import Path
import sys

from openqasm.ast import ForInLoop
from openqasm.parser.antlr.qasm_parser import parse
from openqasm.translator.translator import OpenQASM3Translator
from openqasm.ast_printer import pretty_print

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

def translate(input_file, include_dirs, trans=False, print_circuit=True):
    translator = OpenQASM3Translator(input_file, include_dirs)
    if trans:
        circuit = translator.translate()
        if print_circuit:
            print(circuit.draw())

    return translator.program_ast

def main():
    args = sys.argv
    include_dirs = []
    print_circuit = True
    trans = False

    if '-h' in args or '--help' in args:
        print("usage: python build_ast.py [args] [opts?] ...")
        print()
        print("Arguments (corresponding to 'args'):")
        print("[-i | --input-file] </file/>\t: The OpenQASM3 source file.")
        print("[-I | --include-dir] </path/>\t: Path to include files mentioned in the OpenQASM3 source file.")
        print()
        print("Options (corresponding to 'opts')")
        print("[-h | --help]\t\t\t: Display this help message. (Works without passing any 'args')")
        print("[-t | --translate]\t\t: Flag to enable translation into QuantumCircuit object.")
        print("[-no-circ | --no-print-circuit]\t: Flag to not print the  generated circuit.")
        print("[-v | --verbose]\t\t: Print debug messages for visiting each AST node.")
        print("[-pp | --pprint-ast]\t\t: Pretty print the generated AST.")
        sys.exit(-1)

    if '-i' in args or '--input-file' in args:
        input_index = args.index('-i' if '-i' in args else '--input')
        input_file = args[input_index+1]
    else:
        input_file = args[1]

    for i, arg in enumerate(args):
        if arg in ['-I', '--include-dir']:
            include_dirs.append(Path(args[i+1]))

    if '-no-circ' in args or '--no-print-circuit' in args:
        print_circuit = False

    if '-t' in args or '--translate' in args:
        trans = True

    ast = translate(input_file, include_dirs, trans, print_circuit)

    if '-v' in args or '--verbose' in args:
        verbose(ast)

    if '-pp' in args or '--pprint-ast' in args:
        pretty_print(ast)

if __name__ == "__main__":
    main()
