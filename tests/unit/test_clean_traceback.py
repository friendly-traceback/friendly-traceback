"""In this file, we test to ensure the traceback is properly trimmed
of all ignored files.
"""

import friendly_traceback


def test_uncleaned_traceback():
    """Assert this test filename appear in tracebacks if we don't exclude
    it.
    """
    friendly_traceback.install(redirect="capture")
    old_debug = friendly_traceback.debug_helper.DEBUG
    friendly_traceback.debug_helper.DEBUG = False

    try:
        from . import raise_exception
    except ValueError:
        friendly_traceback.explain_traceback()

    output = friendly_traceback.get_output()
    assert "test_clean_traceback" in output
    assert "André" in output

    # cleanup for other tests
    friendly_traceback.uninstall()
    friendly_traceback.debug_helper.DEBUG = old_debug


def test_cleaned_traceback():
    """Assert this test filename does not appear in tracebacks if we
    exclude it.
    """
    friendly_traceback.install(redirect="capture")
    friendly_traceback.exclude_file_from_traceback(__file__)
    old_debug = friendly_traceback.debug_helper.DEBUG
    friendly_traceback.debug_helper.DEBUG = False

    try:
        from . import raise_exception
    except ValueError:
        friendly_traceback.explain_traceback()

    output = friendly_traceback.get_output()
    assert "test_clean_traceback" not in output
    assert "André" in output

    # cleanup for other tests
    friendly_traceback.path_info.include_file_in_traceback(__file__)
    friendly_traceback.uninstall()
    friendly_traceback.debug_helper.DEBUG = old_debug


if __name__ == "__main__":
    test_uncleaned_traceback()
    test_cleaned_traceback()
