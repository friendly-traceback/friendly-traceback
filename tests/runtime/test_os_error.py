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
    with pytest.raises(OSError) as exc_info:
        raise OSError

    ft_tb = friendly_traceback.core.FriendlyTraceback(exc_info.type, exc_info.value, exc_info.tb)
    ft_tb.compile_info()
    assert ft_tb.info["cause"] == friendly_traceback.ft_gettext.no_information()


if __name__ == "__main__":
    print(test_Generic()[0])
