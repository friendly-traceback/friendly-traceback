from _typeshed import Incomplete

import sys
from typing import Any, Dict, Tuple, Union
from .config import session
from .ft_gettext import current_lang
from .source_cache import cache


def check_syntax(*, source: Incomplete = None, filename: Incomplete = "Fake_filename", path: Incomplete = None, include: Incomplete = None, lang: Incomplete = None) -> Union[bool, Tuple[Any, str]]: ...


def exec_code(*, source: Incomplete = None, path: Incomplete = None, include: Incomplete = None, lang: Incomplete = None) -> Dict: ...
