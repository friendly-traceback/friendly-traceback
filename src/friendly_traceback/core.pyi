import types
from typing import List, Type, Tuple, TypedDict
from .frame_info import FrameInfo
from .tb_data import TracebackData

class Info(TypedDict, total=False):
    header: str
    message: str
    original_python_traceback: str
    simulated_python_traceback: str
    shortened_traceback: str
    exception_notes_intro: List[str]
    exception_notes: str
    suggest: str
    generic: str
    parsing_error: str
    parsing_error_source: str
    cause: str
    detailed_tb: List[str]
    last_call_header: str
    last_call_source: str
    last_call_variables: str
    exception_raised_header: str
    exception_raised_source: str
    exception_raised_variables: str
    warning_message: str
    warning_location_header: str
    warning_source: str
    warning_variables: str
    additional_variable_warning: str
    lang: str
    _tb_data: "TracebackData"

class FriendlyTraceback:
    info: Info
    message: str
    suppressed: list[str]
    tb: types.TracebackType
    tb_data: TracebackData

    def __init__(
        self, etype: Type[Exception], value: BaseException, tb: types.TracebackType
    ) -> None: ...
    def assign_message(
        self, etype: type[BaseException], value: BaseException
    ) -> str: ...
    def compile_info(self) -> None: ...
    def recompile_info(self) -> None: ...
    def add_exception_note(self) -> None: ...
    def assign_cause(self) -> None: ...
    def set_cause_runtime(self) -> None: ...
    def set_cause_syntax(self) -> None: ...
    def assign_generic(self) -> None: ...
    def assign_location(self) -> None: ...
    def locate_exception_raised(self, record: FrameInfo) -> None: ...
    def locate_last_call(
        self, record: FrameInfo, partial_source: str, var_info: str
    ) -> None: ...
    def get_detailed_stack_info(self) -> List[Tuple[str, str, str]]: ...
    def locate_parsing_error(self) -> None: ...
    def assign_tracebacks(self) -> None: ...
    def shorten(self, tb: List[str]) -> List[str]: ...
    def create_traceback(self, records: List[FrameInfo]) -> List[str]: ...

def process_exception_chain(etype: Type[Exception], value: Exception) -> str: ...
def cannot_analyze_stdin() -> str: ...
