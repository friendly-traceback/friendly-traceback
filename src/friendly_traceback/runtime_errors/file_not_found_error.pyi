from ..message_parser import RuntimeMessageParser
from ..tb_data import TracebackData
from ..typing_info import CauseInfo

parser: RuntimeMessageParser

@parser._add
def no_such_file_or_directory(
    value: FileNotFoundError, _tb_data: TracebackData
) -> CauseInfo: ...
