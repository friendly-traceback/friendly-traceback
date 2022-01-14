import pytest

import friendly_traceback
from friendly_traceback.console_helpers import _get_info
from ..syntax_errors_formatting_cases import descriptions

friendly_traceback.set_lang("en")

where = "parsing_error_source"
cause = "cause"

@pytest.mark.parametrize("filename", descriptions.keys())
def test_syntax_errors(filename):
    expected = descriptions[filename]
    try:
        exec("from . import %s" % filename)
    except SyntaxError:
        friendly_traceback.explain_traceback(redirect="capture")
    info = _get_info()

    assert expected[where] == info[where]  # noqa
    assert expected[cause] in info[cause]  # noqa
