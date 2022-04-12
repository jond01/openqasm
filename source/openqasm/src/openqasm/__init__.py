if __name__ == "__main__":
    from pathlib import Path

    from openqasm.translator.translator import OpenQASM3Translator

    trns = OpenQASM3Translator(Path("../../../../examples/adder.qasm"), [Path("../../../../examples")])
    qc = trns.translate()
    print(qc.draw())
