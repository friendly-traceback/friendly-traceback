"""Custom type definitions and shortcuts for annotating ``friendly_traceback``."""

import os
import sys
from types import FrameType
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Tuple, TypeVar, Union

if TYPE_CHECKING:
    from _typeshed import StrPath

    from .core import TracebackData
else:
    StrPath = Union[str, os.PathLike]


_E = TypeVar("_E", bound=BaseException)


if sys.version_info >= (3, 8):
    from typing import Literal, Optional, Protocol, TypedDict

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
        suggest: str
        generic: str
        parsing_error: str
        parsing_error_source: str
        cause: str
        last_call_header: str
        last_call_source: str
        last_call_variables: str
        exception_raised_header: str
        exception_raised_source: str
        exception_raised_variables: str
        lang: str
        _exc_instance: BaseException
        _frame: Optional[FrameType]
        _tb_data: "TracebackData"

    class Formatter(Protocol):
        def __call__(self, info: Info, include: InclusionChoice = ...) -> str:
            ...

    class CauseInfo(TypedDict, total=False):
        cause: str
        suggest: str

    Site = Literal["friendly", "python", "bug", "email", "warnings"]

    ScopeKind = Literal["local", "global", "nonlocal"]

    ObjectsInfo = TypedDict(
        "ObjectsInfo",
        {
            "locals": List[Tuple[str, str, Any]],
            "globals": List[Tuple[str, str, Any]],
            "builtins": List[Tuple[str, str, Any]],
            "expressions": List[Tuple[str, Any]],
            "name, obj": List[Tuple[str, Any]],
        },
    )
    SimilarNamesInfo = TypedDict(
        "SimilarNamesInfo",
        {"locals": List[str], "globals": List[str], "builtins": List[str], "best": Any},
    )

else:
    InclusionChoice = str
    Info = Dict[str, str]
    Formatter = Callable[[Info, InclusionChoice], str]
    Site = str
    CauseInfo = Dict[str, str]
    ScopeKind = str
    ObjectsInfo = Dict[str, List[Any]]
    SimilarNamesInfo = Dict[str, List[str]]


Explain = Callable[[_E, FrameType, "TracebackData"], CauseInfo]
GenericExplain = Callable[[], str]
Parser = Union[
    Callable[[str, FrameType, "TracebackData"], CauseInfo],
    Callable[[_E, FrameType, "TracebackData"], CauseInfo],
]
Translator = Callable[[str], str]
Writer = Callable[[str], None]
