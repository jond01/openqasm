import argparse
import sys
from pathlib import Path

from openqasm.ast import ForInLoop
from openqasm.ast_printer import pretty_print
from openqasm.parser.antlr.qasm_parser import parse
from openqasm.translator.translator import OpenQASM3Translator


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

    argparser = argparse.ArgumentParser(description="Build the AST and perform operations on it.")

    argparser.add_argument(
        "input_file",
        # "-i",
        # "--input-file",
        type=Path,
        help="The OpenQASM3 source file to parse",
    )
    argparser.add_argument(
        "-I",
        "--include-dir",
        type=Path,
        nargs="*",
        help="Path(s) used to search for included files in the OpenQASM3 source.",
    )
    argparser.add_argument(
        "-t",
        "--translate",
        action="store_true",
        help="Flag to enable translation into QuantumCircuit object",
    )
    argparser.add_argument(
        "--no-circ",
        "--no-print-circuit",
        action="store_true",
        help="Flag to not print the generated circuit",
    )
    argparser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print debug messages for visiting each AST node",
    )
    argparser.add_argument(
        "--pprint-ast", "--pp", action="store_true", help="If provided, the AST is pretty printed"
    )

    args = argparser.parse_args()

    ast = translate(args.input_file, args.include_dir, args.translate, not args.no_circ)

    if args.verbose:
        verbose(ast)

    if args.pprint_ast:
        pretty_print(ast)


if __name__ == "__main__":
    main()
