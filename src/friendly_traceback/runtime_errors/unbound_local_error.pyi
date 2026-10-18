from ..message_parser import RuntimeMessageParser
from ..tb_data import TracebackData
from typing import List, TypedDict

class CauseInfo(TypedDict, total=False):
    cause: str
    suggest: str

parser: RuntimeMessageParser
SimilarNamesInfo = TypedDict(
    "SimilarNamesInfo",
    {"locals": List[str], "globals": List[str], "builtins": List[str], "best": str},
)

@parser._add
def local_variable_referenced(message: str, tb_data: TracebackData) -> CauseInfo: ...
def format_similar_names(unknown_name: str, similar: SimilarNamesInfo) -> str: ...
