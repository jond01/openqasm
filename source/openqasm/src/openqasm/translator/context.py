import typing as ty
from dataclasses import dataclass

from openqasm.ast import Span
from openqasm.translator.exceptions import UndefinedSymbol, UninitializedSymbol


@dataclass
class _OpenQASMIdentifier:
    """Store the necessary information about any OpenQASM Identifier."""

    name: str
    value: ty.Any
    definition: ty.Optional[Span]


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
        self._symbols: ty.Dict[str, ty.Optional[_OpenQASMIdentifier]] = {}

    def add_symbol(
        self, symbol: str, value: ty.Any, definition_location: ty.Optional[Span]
    ) -> None:
        """Add the given symbol to the context with the provided value.

        :param symbol: identifier of the symbol to add to the context.
        :param value: value of the given symbol. If value is known to be None,
            prefer using the declare_symbol method instead.
        :param definition_location: a location in the source OpenQASM 3 file
            where the symbol is defined.
        """
        self._symbols[symbol] = _OpenQASMIdentifier(symbol, value, definition_location)

    def lookup(self, symbol: str, current_location: ty.Optional[Span] = None) -> ty.Any:
        """Perform a lookup to recover the value of the given symbol.

        :param symbol: identifier of the symbol to recover from the context.
        :param current_location: actual location in the source OpenQASM file.
        :raise UndefinedSymbol: if the symbol has never been added.
        :raise UninitializedSymbol: if the symbol has been defined but its
            value is None.
        """
        if symbol not in self._symbols:
            raise UndefinedSymbol(symbol, current_location)
        openqasm_identifier: _OpenQASMIdentifier = self._symbols[symbol]
        if openqasm_identifier.value is None:
            raise UninitializedSymbol(symbol, openqasm_identifier.definition, current_location)
        return openqasm_identifier.value

    def declare_symbol(self, symbol: str, definition_location: Span) -> None:
        """Declare a symbol without initializing it."""
        self.add_symbol(symbol, None, definition_location)
