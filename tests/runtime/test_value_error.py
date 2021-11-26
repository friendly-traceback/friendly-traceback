import friendly_traceback


def test_Not_enough_values_to_unpack():
    d = (1,)
    try:
        a, b, *c = d
    except ValueError:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert (
        "ValueError: not enough values to unpack (expected at least 2, got 1)" in result
    )
    if friendly_traceback.get_lang() == "en":
        assert "a `tuple` of length 1" in result

    try:
        for x, y, z in enumerate(range(3)):
            pass
    except ValueError:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "ValueError: not enough values to unpack (expected 3, got 2)" in result

    d = "ab"
    try:
        a, b, c = d
    except ValueError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "ValueError: not enough values to unpack (expected 3, got 2)" in result
    if friendly_traceback.get_lang() == "en":
        assert "a string (`str`) of length 2" in result
    return result, message


def test_Too_many_values_to_unpack():
    c = [1, 2, 3]
    try:
        a, b = c
    except ValueError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "ValueError: too many values to unpack (expected 2)" in result
    if friendly_traceback.get_lang() == "en":
        assert "a `list` of length 3" in result
    return result, message


def test_Date_invalid_month():
    from datetime import date
    try:
        d = date(2021, 13, 1)
    except ValueError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "month must be in 1..12" in result
    if friendly_traceback.get_lang() == "en":
        assert "Valid values are integers, from 1 to 12" in result
    return result, message


def test_slots_conflicts_with_class_variable():
    try:
        class F:
            __slots__ = ["a", "b"]
            a = 1
    except ValueError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "'a' in __slots__ conflicts with class variable" in result
    if friendly_traceback.get_lang() == "en":
        assert "is used both as the name of a class variable" in result
    return result, message


def test_time_strptime_incorrect_format():  # issue 78
    import os

    # For some reason, this test takes a long time on github.
    # This should have been fixed by requiring stack_data >= 0.1.3
    # but it apparently has not.
    if "andre" not in os.getcwd():
        print("test for issue #78 skipped")
        return

    import time
    try:
        time.strptime("2020-01-01", "%d %m %Y")
    except ValueError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "time data '2020-01-01' does not match format '%d %m %Y'" in result
    if friendly_traceback.get_lang() == "en":
        assert "The value you gave for the time is not in the format you specified." in result

    return result, message


def test_Convert_to_int():
    english = friendly_traceback.get_lang() == "en"
    try:
        int('13a', base=0)
    except ValueError:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "ValueError: invalid literal for int() with base" in result
    if english:
        assert "When base `0` is specified, `int()` expects" in result

    try:
        int("13x", base=16)
    except ValueError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "ValueError: invalid literal for int() with base" in result
    if english:
        assert "The following characters are not allowed: `x`" in result

    try:
        int("1898", base=5)
    except ValueError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "ValueError: invalid literal for int() with base" in result
    if english:
        assert "The following characters are not allowed: `8, 9`" in result

    try:
        int('1e6')
    except ValueError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "ValueError: invalid literal for int() with base" in result
    if english:
        assert "needs to be first converted using `float()`" in result

    try:
        int('13a')
    except ValueError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "ValueError: invalid literal for int() with base" in result
    if english:
        assert "The following characters are not allowed: `a`" in result

    return result, message


def test_int_base_not_in_range():
    try:
        int('18', base=37)
    except ValueError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "int() base must be >= 2 and <= 36, or 0" in result
    if friendly_traceback.get_lang() == "en":
        assert "You wrote 37 which is not allowed." in result

    return result, message



if __name__ == "__main__":
    print(test_Too_many_values_to_unpack()[0])
