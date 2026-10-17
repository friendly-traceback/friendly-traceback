from typing import Callable, Union, TypedDict
from .tb_data import TracebackData

GenericExplain = Callable[[], str]

class CauseInfo(TypedDict, total=False):
    cause: str
    suggest: str

Parser = Union[
    Callable[[str, "TracebackData"], CauseInfo],
    Callable[[type[Exception], "TracebackData"], CauseInfo],
]

Translator = Callable[[str], str]

Writer = Callable[[str], None]
