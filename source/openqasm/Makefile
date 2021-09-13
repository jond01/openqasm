all: antlr4 install


antlr4:
	cd ../grammar/ && antlr4 -o ../openqasm/src/openqasm3/parser/antlr -Dlanguage=Python3 -visitor qasm3.g4 && cd ../openqasm/

install: antlr4
	python -m pip install -e .[all]
