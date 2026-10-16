import argparse
import platform
import runpy
import sys
import warnings
from importlib import import_module
from pathlib import Path
from . import (
    __version__,
    debug_helper,
    exclude_file_from_traceback,
    explain_traceback,
    ft_console,
    install,
    set_formatter,
)
from .ft_gettext import current_lang

versions: str


def import_function(dotted_path: str) -> type: ...


parser: ArgumentParser


def main() -> None: ...
