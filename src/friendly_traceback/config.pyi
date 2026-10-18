from typing import Callable, List, Protocol, Type, Any, TypedDict
from types import TracebackType
from friendly_traceback.base_formatters import InclusionChoice
from friendly_traceback.core import FriendlyTraceback
from friendly_traceback.tb_data import TracebackData

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
    _tb_data: TracebackData

class Formatter(Protocol):
    def __call__(self, info: Info, include: InclusionChoice = ...) -> str: ...

class State:
    _captured: List[str]
    write_err: Callable[[str], str | None] | None
    installed: bool
    formatter: Formatter
    recorded_tracebacks = List[FriendlyTraceback]
    include: InclusionChoice
    lang: str
    other_set_lang: List[str]
    suggest_console: str
    ipython_prompt: bool
    exception_before_import: bool
    sys_last_type: Type[Exception] | None
    sys_last_value: Exception
    use_rich: bool
    rich_add_vspace: bool
    rich_width: int | None
    rich_tb_width: int | None
    is_jupyter: bool
    jupyter_button_style: str
    old_excepthook: None | Callable[[Type[Exception], Exception, TracebackType], None]
    include_chained_exception: bool

    def __init__(self) -> None: ...
    def show_traceback_info_again(self, index: int = -1) -> None: ...
    def capture(self, txt: str) -> None: ...
    def get_captured(self, flush: bool = True) -> str: ...
    def set_lang(self, lang: str) -> None: ...
    def install_gettext(self, lang: str) -> None: ...
    def set_include(self, include: InclusionChoice) -> None: ...
    def get_include(self) -> InclusionChoice: ...
    def set_formatter(self, formatter: Formatter | None = None) -> None: ...
    def install(
        self,
        lang: str | None = None,
        redirect: Callable[[str], Any] | None = None,
        include: InclusionChoice | None = None,
    ): ...
    def uninstall(self) -> None: ...
    def set_redirect(self, redirect: Callable[[str], Any] | None = None): ...
    def explain_traceback(self, redirect: Callable[[str], Any] | None = None): ...
    def exception_hook(
        self,
        etype: Type[Exception],
        value: Exception,
        tb: TracebackType,
        redirect: Callable[[str], Any] | None = None,
    ) -> None: ...
    def output_info(
        self, info: Info, redirect: Callable[[str], Any] | None = None
    ) -> None: ...
    def get_traceback_info(
        self,
        etype: Type[Exception],
        value: Exception,
        tb: TracebackType,
    ) -> Info: ...

def did_exception_occur_before() -> bool: ...

session: State
