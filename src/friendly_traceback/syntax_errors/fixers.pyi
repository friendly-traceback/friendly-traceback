from typing import Literal
from _typeshed import Incomplete

import warnings
from .. import debug_helper, token_utils


def replace_token(tokens: Incomplete, original_token: Incomplete, new_token_string: Incomplete = " ") -> Incomplete: ...


def replace_two_tokens(tokens: Incomplete, first_token: Incomplete, first_string: Incomplete = "", second_token: Incomplete = None, second_string: Incomplete = "") -> Incomplete: ...


def check_statement(statement: Incomplete) -> Incomplete: ...


if_block: Literal['\r\nif True:\r\n    pass\r\n%s\r\n'] = ("""
if True:
    pass
%s
""")
def_block: Literal['\r\ndef test():\r\n    %s\r\n'] = ("""
def test():
    %s
""")
try_block: Literal['\r\ntry:\r\n    pass\r\n%s\r\n'] = ("""
try:
    pass
%s
""")
