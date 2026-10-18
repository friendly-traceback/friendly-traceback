from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Sequence,
    Protocol,
    Union,
    TypedDict,
)
import os

from friendly_traceback.__about__ import version as __version__
from friendly_traceback.base_formatters import InclusionChoice
from friendly_traceback.tb_data import TracebackData

Writer = Callable[[str], None]

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

StrPath = Union[str, os.PathLike]

class Formatter(Protocol):
    def __call__(self, info: Info, include: InclusionChoice = ...) -> str: ...

valid_version: bool

def add_ignored_warnings(do_not_show_warning: Callable[[Any], bool]) -> None: ...
def add_other_attribute_names(attributes: dict) -> None: ...
def add_other_module_names_synonyms(synonyms: dict) -> None: ...
def add_other_set_lang(func: Callable[[str], None]) -> None: ...
def exclude_file_from_traceback(full_path: str) -> None: ...
def exclude_directory_from_traceback(dir_name: str) -> None: ...
def explain_traceback(redirect: str | None = None) -> None: ...
def hide_secrets(patterns: list[str] | None = None) -> None: ...
def test_secrets(name: str = "") -> str | None: ...
def get_output(flush: bool = True) -> str: ...
def install(
    lang: str | None = None,
    redirect: str | None = None,
    include: InclusionChoice = "explain",
    _debug: bool = False,
) -> None: ...
def is_installed() -> bool: ...
def uninstall() -> None: ...
def run(
    filename: StrPath,
    lang: str = "en",
    include: InclusionChoice | None = None,
    args: Sequence[str] | None = None,
    console: bool = True,
    formatter: str | Formatter | None = "repl",
    redirect: str | Writer | None = None,
    ipython_prompt: bool = True,
) -> Dict[str, Any] | None: ...
def set_formatter(formatter: str | Formatter | None = None) -> None: ...
def start_console(
    local_vars: Mapping[str, Any] | None = None,
    formatter: str | Formatter | None = None,
    include: InclusionChoice = "friendly_tb",
    lang: str = "en",
    banner: str | None = None,
    displayhook: Callable[[object], Any] | None = None,
    ipython_prompt: bool = True,
) -> None: ...
def set_lang(lang: str = "en") -> List[str] | None: ...
def get_lang() -> str: ...
def set_include(include: InclusionChoice) -> None: ...
def get_include() -> InclusionChoice: ...
def set_stream(redirect: str | Writer | None = None) -> None: ...
def get_stream() -> Writer: ...
