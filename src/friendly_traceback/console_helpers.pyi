from typing import Callable, ClassVar, Literal
from _typeshed import Incomplete

import types
from typing import Any, Callable, Dict, List, Type, Union
from friendly_traceback.typing_info import InclusionChoice, Site

def disable() -> None: ...
def enable() -> None: ...
def explain(index: int = -1, include: InclusionChoice = "explain") -> None: ...
def friendly_tb(index: int = -1) -> None: ...
def hint(index: int = -1) -> None: ...

class History:
    __name__: ClassVar[Literal["history"]] = "history"

    def __call__(self) -> Incomplete: ...
    def __repr__(self) -> Incomplete: ...
    def clear(self) -> Incomplete: ...
    def pop(self, index: Incomplete = -1) -> Incomplete: ...

history: History

def python_tb(index: int = -1) -> None: ...
def what(
    exception_or_index: Union[
        Type[BaseException], str, bytes, types.CodeType, int, None
    ] = None,
    pre: bool = False,
) -> None: ...
def where(index: int = -1, more: Incomplete = False) -> None: ...
def why(index: int = -1) -> None: ...
def www(site_or_index: Union[Site, int] = -1) -> None: ...
def set_debug(flag: bool = True) -> None: ...

get_lang: Callable[[], str]
set_lang: Callable[..., list[str] | None]
get_include: Callable[
    [],
    Literal[
        "debug_tb",
        "explain",
        "friendly_tb",
        "hint",
        "message",
        "no_tb",
        "python_tb",
        "what",
        "where",
        "why",
    ],
]
set_include: Callable[
    [
        Literal[
            "debug_tb",
            "explain",
            "friendly_tb",
            "hint",
            "message",
            "no_tb",
            "python_tb",
            "what",
            "where",
            "why",
        ]
    ],
    None,
]
set_formatter: Callable[..., None]
helpers: Dict[str, Callable[..., None]]
debug_helper_methods: Dict[str, Callable[..., Any]]

class FriendlyHelpers:
    version: ClassVar[str]
    helpers: Incomplete

    def __init__(self) -> None: ...
    def add_helper(self, function: Callable) -> None: ...
    def remove_helper(self, name: str) -> None: ...
    def __dir__(self) -> List[str]: ...
    def __repr__(self) -> str: ...
    def true_repr(self) -> str: ...

Friendly: FriendlyHelpers
