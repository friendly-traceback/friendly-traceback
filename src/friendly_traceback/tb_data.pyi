from typing import Literal
from _typeshed import Incomplete

from types import FrameType, TracebackType
from typing import Generic, List, Type
from .frame_info import FrameInfo
from friendly_traceback.syntax_errors import source_info

STR_FAILED: Literal["<exception str() failed>"] = "<exception str() failed>"

def convert_value_to_message(value: BaseException) -> str: ...
def retrieve_message(
    etype: Type[BaseException], value: BaseException, tb: TracebackType
) -> str: ...

class TracebackData:
    bad_line: str
    exception_frame: FrameType | None
    exception_instance: BaseException | None
    exception_name: str
    exception_type: type[BaseException]
    filename: str
    formatted_tb: list[str]
    full_message: str
    message: str
    node: Incomplete
    node_range: tuple[int, int] | None
    node_text: str
    original_bad_line: str
    program_stopped_bad_line: str
    program_stopped_frame: FrameType | None
    program_stopped_node_range: Incomplete
    python_records: list[FrameInfo]
    records: list[FrameInfo]
    simulated_python_traceback: str | None
    statement: source_info.Statement | None
    value: BaseException

    def __init__(
        self, etype: Type[Exception], value: BaseException, tb: TracebackType
    ) -> None: ...
    def get_records(
        self, tb: TracebackType, python_excluded: bool = True
    ) -> List[FrameInfo]: ...
    def get_source_info(self) -> None: ...
    def locate_error(self) -> None: ...
