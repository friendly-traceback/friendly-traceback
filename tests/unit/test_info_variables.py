import inspect

import friendly_traceback as ft

global_a = 1
global_b = 2
global_and_nonlocal_different = 1


def test_get_variables_in_frame_by_scope():
    # We cannot use pytest for this test as it messes with the frames
    # and generates a RuntimeError.

    get = ft.info_variables.get_variables_in_frame_by_scope
    current_frame = None

    b = 2
    global_and_nonlocal_different = 2

    def outer():
        c = 3
        d = 4

        def inner():
            global global_a
            global global_b
            nonlocal current_frame
            nonlocal c
            e = 5
            global_b += 1
            current_frame = inspect.currentframe()

        inner()

    outer()

    # declaring a variable global and changing (or not) its value
    # does not make it a local variable
    assert "global_a" in get(current_frame, "global")
    assert "global_a" not in get(current_frame, "local")
    assert "global_a" not in get(current_frame, "nonlocal")
    assert "global_b" not in get(current_frame, "local")

    # nonlocal variable two frames removed is the same as one frame removed
    # b: two frames removed
    assert "b" in get(current_frame, "nonlocal")
    assert "b" not in get(current_frame, "local")
    assert "b" not in get(current_frame, "global")
    # d: one frame removed
    assert "d" in get(current_frame, "nonlocal")
    assert "d" not in get(current_frame, "local")
    assert "d" not in get(current_frame, "global")

    # declaring a variable nonlocal makes it also a local variable
    assert "c" in get(current_frame, "local")
    assert "c" in get(current_frame, "nonlocal")
    assert "c" not in get(current_frame, "global")

    assert "e" in get(current_frame, "local")

    assert "global_and_nonlocal_different" in get(current_frame, "nonlocal")
    assert "global_and_nonlocal_different" in get(current_frame, "global")

    # test other function after fixing bug (issue #69)
    get_scopes = ft.info_variables.get_definition_scope
    assert "nonlocal" in get_scopes("global_and_nonlocal_different", current_frame)
    assert "global" in get_scopes("global_and_nonlocal_different", current_frame)
    assert "nonlocal" not in get_scopes("global_a", current_frame)
    assert "global" in get_scopes("global_a", current_frame)
    assert "nonlocal" in get_scopes("b", current_frame)
    assert "global" not in get_scopes("b", current_frame)


def test_simplify_repr():
    import math
    import tkinter

    simplify = ft.info_variables.simplify_repr
    INDENT = ft.info_variables.INDENT

    simplified_math = simplify(repr(math))
    assert simplified_math == "<module math (builtin)>" or (
        "<module math>" in simplified_math and "PYTHON_LIB" in simplified_math
    )
    # replace \ in path so that it works for all OSes
    assert (
        simplify(repr(tkinter)).replace("\\", "/")
        == "<module tkinter> from PYTHON_LIB:/tkinter/__init__.py"
    )
    assert simplify(repr(open)) == "<builtin function open>"
    assert simplify("<class 'AssertionError'>") == "<class AssertionError>"
    assert (
        simplify("<bound method ChainMap.pop of ChainMap({(0, 0): 'origin'}, {})>")
        == "<bound method ChainMap.pop> of ChainMap({(0, 0): 'origin'}, {})"
    )
    assert (
        simplify("<built-in method popitem of dict object at 0x00000267D1C96180>")
        == "<builtin method popitem of dict object>"
    )
    assert (
        simplify("<function test_Generic.<locals>.a at 0x00000267D28B0F70>")
        == "<function a> defined in <function test_Generic>"
    )
    assert (
        simplify(
            "<bound method test_method_got_multiple_argument.<locals>.T.some_method"
            " of <tests.runtime.test_type_error.test_method_got_multiple_argument."
            "<locals>.T object at 0x00000179EE9CD7F0>>"
        )
        == "<bound method T.some_method>"
        + f"\n{INDENT}of <T object>"
        + f"\n{INDENT}defined in <function "
        + "tests.runtime.test_type_error.test_method_got_multiple_argument>"
    )


if __name__ == "__main__":
    test_get_variables_in_frame_by_scope()
