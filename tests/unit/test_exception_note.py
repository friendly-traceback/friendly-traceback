import sys
import friendly_traceback as ft

def test_exception_note():
    if sys.version_info >= (3, 11):
        try:
            try:
                raise ValueError("This is an exception.")
            except ValueError as exc:
                exc.add_note("This is a note.")
                raise
        except ValueError:
            ft.explain_traceback(redirect="capture")
            result = ft.get_output()
            assert "* This is a note." in result
