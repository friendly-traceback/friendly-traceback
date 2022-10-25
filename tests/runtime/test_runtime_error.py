import friendly_traceback as ft


def test_size_changed_during_iteration():
    squares = {1:1, 2:4, 3:9}
    try:
        for square in squares:
            squares.pop(square)
    except RuntimeError as e:
        ft.explain_traceback(redirect="capture")
    result = ft.get_output()
    assert "RuntimeError" in result
    if ft.get_lang() == "en":
        assert "While you were iterating over the items of `squares` (a dictionary (`dict`))" in result

    numbers = {1, 2, 3}
    try:
        for n in numbers:
            numbers.remove(n)
    except RuntimeError as e:
        message = str(e)
        ft.explain_traceback(redirect="capture")
    result = ft.get_output()
    assert "RuntimeError" in result
    if ft.get_lang() == "en":
        assert "While you were iterating over the items of `numbers` (a `set`)" in result
    if ft._writing_docs:
        return result, message
