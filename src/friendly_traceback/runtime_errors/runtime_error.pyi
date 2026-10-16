from ..tb_data import TracebackData
from ..typing_info import CauseInfo
from ..message_parser import RuntimeMessageParser

parser: RuntimeMessageParser

@parser._add
def container_changed_size_during_iteration(
    message: str, tb_data: TracebackData
) -> CauseInfo: ...
