from typing import Dict
from ..message_parser import RuntimeMessageParser, CauseInfo
from ..tb_data import TracebackData

parser: RuntimeMessageParser

@parser._add
def object_assignment_out_of_range(
    message: str, tb_data: TracebackData
) -> CauseInfo: ...
def cannot_identify_object(obj_type: str, bad_line: str) -> Dict: ...
@parser._add
def index_out_of_range(message: str, tb_data: TracebackData) -> CauseInfo: ...
