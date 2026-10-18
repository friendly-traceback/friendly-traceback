from ..message_parser import RuntimeMessageParser
from ..tb_data import TracebackData

from typing import TypedDict

parser: RuntimeMessageParser

class CauseInfo(TypedDict, total=False):
    cause: str
    suggest: str

@parser._add
def handle_connection_error(_message: str, tb_data: TracebackData) -> CauseInfo: ...
@parser._add
def invalid_argument(message: str, tb_data: TracebackData) -> CauseInfo: ...
