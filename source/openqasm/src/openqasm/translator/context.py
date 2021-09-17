import typing as ty

from openqasm.translator.exceptions import UndefinedSymbol, UninitializedSymbol


class OpenQASMContext:
    """Store the necessary context to parse correctly an OpenQASM3 file.

    Some context is needed to parse correctly an OpenQASM3 file, for example to
    store the value associated to a given identifier, in order to be able to
    perform computations on this value or to recover the actual value.

    This OpenQASMContext class provide a dictionary-like structure to store and
    retrieve values and symbols.
    """

    def __init__(self):
        """Initialize an empty context."""
        self._symbols: ty.Dict[str, ty.Any] = {}

    def add_symbol(self, symbol: str, value: ty.Any) -> None:
        """Add the given symbol to the context with the provided value.

        :param symbol: identifier of the symbol to add to the context.
        :param value: value of the given symbol. If value is known to be None,
            prefer using the declare_symbol method instead.
        """
        self._symbols[symbol] = value

    def lookup(self, symbol: str) -> ty.Any:
        """Perform a lookup to recover the value of the given symbol.

        :param symbol: identifier of the symbol to recover from the context.
        :raise UndefinedSymbol: if the symbol has never been added.
        :raise UninitializedSymbol: if the symbol has been defined but its
            value is None.
        """
        if symbol not in self._symbols:
            raise UndefinedSymbol(symbol)
        value = self._symbols[symbol]
        if value is None:
            raise UninitializedSymbol(symbol)
        return value

    def declare_symbol(self, symbol: str) -> None:
        """Declare a symbol without initializing it."""
        self.add_symbol(symbol, None)
