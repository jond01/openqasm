import typing as ty

from openqasm.ast import Identifier, IndexIdentifier
from openqasm.translator.context import OpenQASMContext
from openqasm.translator.exceptions import UnsupportedFeature


def get_identifier(
    identifier: ty.Union[Identifier, IndexIdentifier], context: OpenQASMContext
) -> ty.Any:
    if isinstance(identifier, Identifier):
        return context.lookup(identifier.name)
    elif isinstance(identifier, IndexIdentifier):
        raise UnsupportedFeature(IndexIdentifier.__name__)
