import friendly_traceback

def test_With_exec():
    try:
        exec("1/0")
    except ZeroDivisionError:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    if friendly_traceback.get_lang() == "en":
        assert "<string> is not a regular Python file" in result
    else:
        assert "<string>" in result


def test_With_fake_file():
    code = compile("1/0", "<fake>", "exec")
    try:
        exec(code)
    except ZeroDivisionError:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "<fake>" in result
    if friendly_traceback.get_lang() == "en":
        assert "<fake> is not a regular Python file" in result
        assert "Internal error" not in result
