from typing import Type, List
from .tb_data import TracebackData
from .typing_info import CauseInfo, Parser

INCLUDED_PARSERS: dict[
    type[AttributeError]
    | type[FileNotFoundError]
    | type[ImportError]
    | type[IndexError]
    | type[KeyError]
    | type[ModuleNotFoundError]
    | type[NameError]
    | type[OSError]
    | type[RuntimeError]
    | type[TypeError]
    | type[UnboundLocalError]
    | type[ValueError]
    | type[ZeroDivisionError],
    str,
]
RUNTIME_MESSAGE_PARSERS: dict[type[BaseException], RuntimeMessageParser]

class RuntimeMessageParser:
    core_parsers: List[Parser]
    custom_parsers: List[Parser]
    parsers: List[Parser]

    def __init__(self) -> None: ...
    def add(self, func: Parser) -> Parser: ...
    def _add(self, func: Parser) -> Parser: ...

def get_parser(exception_type: Type[BaseException]) -> RuntimeMessageParser: ...
def get_likely_cause(
    exception_type: type[Exception], message: str, tb_data: TracebackData
) -> CauseInfo: ...
def get_cause(
    exception_type: type[Exception], message: str, tb_data: TracebackData
) -> CauseInfo: ...
