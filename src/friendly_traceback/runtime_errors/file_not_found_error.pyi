from ..message_parser import RuntimeMessageParser, CauseInfo
from ..tb_data import TracebackData

parser: RuntimeMessageParser

@parser._add
def no_such_file_or_directory(message: str, _tb_data: TracebackData) -> CauseInfo: ...
