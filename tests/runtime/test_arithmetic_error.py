import friendly_traceback


def test_Generic():
    try:
        # I am not aware of any way in which this error is raised directly
        # Usually, a subclass such as ZeroDivisionError, etc., would
        # likely be raised.
        raise ArithmeticError('error')
    except ArithmeticError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "ArithmeticError" in result
    if friendly_traceback.get_lang() == "en":
        assert "`ArithmeticError` is the base class" in result
    if friendly_traceback._writing_docs:
        return result, message


if __name__ == "__main__":
    print(test_Generic()[0])
