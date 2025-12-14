from typing import TypeVar


class Command:
    pass


class Query:
    pass


TMessage = TypeVar("TMessage", bound=Command | Query)
TResult = TypeVar("TResult")
