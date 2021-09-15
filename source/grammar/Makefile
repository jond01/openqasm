all: antlr4 install


antlr4:
	antlr4 -o openqasm_reference_parser/ -Dlanguage=Python3 qasm3.g4

install: antlr4
	python -m pip install -e .[all]
