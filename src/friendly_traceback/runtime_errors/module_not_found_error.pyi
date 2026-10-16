from ..message_parser import RuntimeMessageParser
from ..tb_data import TracebackData
from ..typing_info import CauseInfo

parser: RuntimeMessageParser

@parser._add
def is_not_a_package(message: str, _tb_data: TracebackData) -> CauseInfo: ...
def curses_no_found() -> CauseInfo: ...
@parser._add
def no_module_named(message: str, _tb_data: TracebackData) -> CauseInfo: ...
