import os
from typing import Set, TypeVar, Union

StrPath = Union[str, os.PathLike]

EXCLUDED_FILE_PATH: Set[str]
EXCLUDED_DIR_NAMES: Set[str]
SITE_PACKAGES: str
PYTHON_LIB: str
FRIENDLY: str
TESTS: str

def exclude_file_from_traceback(full_path: StrPath) -> None: ...
def exclude_directory_from_traceback(dir_name: StrPath) -> None: ...

dirname: str

def is_excluded_file(full_path: StrPath, python_excluded: bool = True) -> bool: ...
def include_file_in_traceback(full_path: str) -> None: ...

class PathUtil:
    home: str

    def __init__(self) -> None: ...

    MaybeText = TypeVar("MaybeText", str, None)

    def shorten_path(self, path: MaybeText) -> MaybeText: ...

def shorten_jupyter_kernel(path: str) -> str: ...

path_utils: PathUtil

def show_paths() -> None: ...
