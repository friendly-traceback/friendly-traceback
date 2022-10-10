import sys
import friendly_traceback as ft


def test_exception_note():
    exc = ValueError("This is an exception.")
    if sys.version_info >= (3, 11):
        exc.add_note("This is a note.")
        try:
            raise exc
        except ValueError:
            ft.explain_traceback(redirect="capture")
            result = ft.get_output()
            assert "* This is a note." in result
    else:
        try:
            exc.add_note("This is a note.")
        except AttributeError:
            ft.explain_traceback(redirect="capture")
            result = ft.get_output()
            if ft.get_lang() == "en":
                assert (
                    "`add_note()` is only allowed for Python version 3.11 and newer."
                    in result
                )
