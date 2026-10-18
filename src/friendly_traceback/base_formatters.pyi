from typing import Dict, List, Set, TypedDict, Literal
from friendly_traceback.tb_data import TracebackData

from typing import Literal

InclusionChoice = Literal[
    "message",
    "hint",
    "what",
    "why",
    "where",
    "friendly_tb",
    "python_tb",
    "debug_tb",
    "explain",
    "no_tb",
]

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

items_in_order: list[str]
repl_indentation: dict[str, str]

def repl(info: Info, include: InclusionChoice = "friendly_tb") -> str: ...
def detailed_tb(info: Info) -> str: ...
def docs(info: Info, include: InclusionChoice = "friendly_tb") -> str: ...
def no_result(info: Info, include: InclusionChoice) -> str: ...

items_groups: Dict[InclusionChoice, Set[str]]

def select_items(group_name: InclusionChoice) -> List[str]: ...
