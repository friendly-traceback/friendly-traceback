import friendly_traceback


def multiple_choices():
    try:
        from math import bsin
    except ImportError:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "ImportError: cannot import name 'bsin'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean one of the following:" in result
        assert "sin, asin" in result or "asin, sin" in result


def no_suggestion():
    try:
        from math import alphabet_alphabet
    except ImportError:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "ImportError: cannot import name 'alphabet_alphabet'" in result
    if friendly_traceback.get_lang() == "en":
        assert "could not be imported is `alphabet_alphabet`" in result


def multiple_import_on_same_line():
    try:
        import circular_a, circular_b
    except ImportError:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "cannot import name 'a'" in result
    if friendly_traceback.get_lang() == "en":
        assert "likely caused by what is known as a 'circular import'." in result


def wrong_case():
    try:
        from math import PI
    except ImportError:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `pi`" in result



def test_Simple_import_error():
    multiple_choices()  # do not record in documentation
    no_suggestion()
    multiple_import_on_same_line()
    wrong_case()

    try:
        from math import Pi
    except ImportError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "ImportError: cannot import name 'Pi'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `pi`" in result
    if friendly_traceback._writing_docs:
        return result, message


# The following test has become unreliable when running under pytest.
# def test_Circular_import():
#
#     try:
#         import circular_a
#     except ImportError as e:
#         message = str(e)
#         friendly_traceback.explain_traceback(redirect="capture")
#     else:
#         message = "Message was never set."
#     result = friendly_traceback.get_output()
#     # The actual message varies a lot depending on Python version.
#
#     if friendly_traceback.get_lang() == "en":
#         assert friendly_traceback.utils.expected_in_result("what is known as a 'circular import'", result)
#
#     if friendly_traceback._writing_docs:
        return result, message


if __name__ == "__main__":
    print(test_Simple_import_error()[0])
