import pytest
import friendly_traceback


def test_Urllib_error():
    from urllib import request, error
    try:
        request.urlopen("http://does_not_exist")
    except error.URLError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "URLError" in result
    if friendly_traceback.get_lang() == "en":
        assert "An exception of type `URLError` is a subclass of `OSError`." in result
        assert "I suspect that you are trying to connect to a server" in result
    return result, message


def test_no_information():
    # simulate an unknown OSError
    # We silence the message about a new case to consider
    old_debug = friendly_traceback.debug_helper.DEBUG
    friendly_traceback.debug_helper.DEBUG = False
    try:
        raise OSError("Some unknown message")
    except OSError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    lines = friendly_traceback.ft_gettext.no_information().split("\n")
    if friendly_traceback.get_lang() == "en":
        for line in lines:
            assert line in result
    friendly_traceback.debug_helper.DEBUG = old_debug
    return result, message


def test_invalid_argument():
    import os
    if os.name != "nt":
        return "Windows test only", "No result"
    try:
        open("c:\test.txt")
    except OSError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")

    result = friendly_traceback.get_output()
    assert "Invalid argument" in result
    if friendly_traceback.get_lang() == "en":
        assert "front of the filename or path, or replace all single backslash" in result
    return result, message
