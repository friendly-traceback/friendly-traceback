import friendly_traceback


class MyException(Exception):
    pass


def test_Generic():
    old_debug = friendly_traceback.debug_helper.DEBUG
    friendly_traceback.debug_helper.DEBUG = False
    try:
        raise MyException("Some informative message about an unknown exception.")
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "Some informative message" in result
    if friendly_traceback.get_lang() == "en":
        assert "No information is known about this exception." in result
    friendly_traceback.debug_helper.DEBUG = old_debug
    return result, message


if __name__ == "__main__":
    print(test_Generic()[0])
