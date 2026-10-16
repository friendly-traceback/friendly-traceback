import ast
import difflib
import types
import uuid
from typing import Any, Dict, Iterable, List, Tuple
import pure_eval
from .tb_data import TracebackData


def unique_variable_name() -> str: ...


def eval_expr(expr: str, frame: types.FrameType) -> Any: ...


def get_similar_words(word_with_typo: str, words: Iterable[str]) -> List[str]: ...


def list_to_string(list_: Iterable[str], sep: str = ", ") -> str: ...


def expected_in_result(expected: str, result: str) -> Tuple[bool, str]: ...


def get_bad_statement(tb_data: TracebackData) -> str: ...


def to_code_block(code: str) -> str: ...


def get_highlighting_ranges(lines: List[str]) -> Dict[int, List[Tuple[int, int]]]: ...


def get_single_line_highlighting_ranges(line: str) -> List[Tuple[int, int]]: ...


def create_caret_highlighted(caret_line: List[Tuple[int, int]]) -> str: ...
