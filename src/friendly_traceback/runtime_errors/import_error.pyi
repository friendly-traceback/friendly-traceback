from typing import List, Optional, Tuple
from ..message_parser import RuntimeMessageParser
from ..tb_data import TracebackData
from ..typing_info import CauseInfo

parser: RuntimeMessageParser

@parser._add
def partially_initialized_module(message: str, tb_data: TracebackData) -> CauseInfo: ...
def cannot_import_name_from(
    name: str, module: str, tb_data: TracebackData, add_circular_hint: bool = True
) -> CauseInfo: ...
def cannot_import_name(name: str, tb_data: TracebackData) -> CauseInfo: ...

Modules = List[Tuple[str, str]]

def extract_import_data_from_traceback(tb_data: TracebackData) -> Modules: ...
def find_circular_import(modules_imported: Modules) -> Optional[str]: ...
