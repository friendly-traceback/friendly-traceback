import friendly_traceback


class UnknownException(Exception):
    pass

class UnknownTwo(UnknownException):
    pass


def test_Generic():
    old_debug = friendly_traceback.debug_helper.DEBUG
    friendly_traceback.debug_helper.DEBUG = False

    try:
        raise UnknownTwo("irrelevant message")
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "UnknownException -> Exception" in result

    try:
        raise UnknownException("Some informative message about an unknown exception.")
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "Some informative message" in result
    if friendly_traceback.get_lang() == "en":
        assert "Nothing more specific is known about" in result
    friendly_traceback.debug_helper.DEBUG = old_debug
    if friendly_traceback._writing_docs:
        return result, message


if __name__ == "__main__":
    print(test_Generic()[0])
