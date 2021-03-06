import sys

import pytest

import friendly_traceback
from syntax_errors_descriptions import descriptions

friendly_traceback.set_lang("en")


@pytest.mark.parametrize("filename", descriptions.keys())
def test_syntax_errors(filename):
    cause = descriptions[filename]["in cause"]

    try:
        # __import__(filename)
        exec("from . import %s" % filename)
    except Exception:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    if "tab_error" in filename:
        assert "TabError" in result, "TabError identified incorrectly; %s" % filename
    elif "indentation" in filename or "indented" in cause:
        assert "IndentationError" in result, (
            "IndentationError identified incorrectly; %s" % filename
        )
    else:
        assert "SyntaxError" in result or "IndentationError" in result, (
            "SyntaxError identified incorrectly; %s" % filename
        )

    unwrapped_result = " ".join(result.split())

    if "version dependent" in descriptions[filename]:
        causes = descriptions[filename]["version dependent"]
        for cause in causes:
            if cause in unwrapped_result:
                break
        else:
            assert False, "\nExpected to see a version dependent cause in\n%s" % result
    else:
        assert cause in unwrapped_result, "\nExpected to see: %s\nIn: %s" % (cause, result)
        if "also in cause" in descriptions[filename]:
            other_causes = descriptions[filename]["also in cause"]
            for cause in other_causes:
                assert cause in unwrapped_result, "\nExpected to see: %s\nIn: %s" % (
                    cause,
                    result,
                )
        if "not in cause" in descriptions[filename]:
            not_in_cause = descriptions[filename]["not in cause"]
            for cause in not_in_cause:
                assert cause not in unwrapped_result, "\nDid not expect to see: %s\nIn: %s" % (
                    cause,
                    result,
                )
