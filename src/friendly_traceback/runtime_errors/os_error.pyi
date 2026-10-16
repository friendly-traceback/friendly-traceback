from ..message_parser import RuntimeMessageParser
from ..tb_data import TracebackData
from ..typing_info import CauseInfo

parser: RuntimeMessageParser

@parser._add
def handle_connection_error(_message: OSError, tb_data: TracebackData) -> CauseInfo: ...
@parser._add
def invalid_argument(message: str, tb_data: TracebackData) -> CauseInfo: ...
