import math

import friendly_traceback

from friendly_traceback import console_helpers as helpers

#  ====Important: ensure that we have a clean history after each test.


_hint = "Did you mean `pi`?"
_message = "AttributeError: module"
_what = "An `AttributeError` occurs"
_where = "Exception raised on line"
_why = "Perhaps you meant to write"


def test_friendly_tb():
    friendly_traceback.set_stream(redirect="capture")
    helpers.history.clear()
    try:
        math.Pi
    except AttributeError:
        friendly_traceback.explain_traceback(redirect="capture")
        friendly_traceback.get_output()
    helpers.friendly_tb()
    result = friendly_traceback.get_output()
    assert _hint in result
    assert _message in result
    assert "File" in result
    assert friendly_traceback.config.session.recorded_tracebacks
    del helpers.history[-1]
    assert not friendly_traceback.config.session.recorded_tracebacks


def test_hint():
    friendly_traceback.set_stream(redirect="capture")
    helpers.history.clear()
    try:
        math.Pi
    except AttributeError:
        friendly_traceback.explain_traceback(redirect="capture")
        friendly_traceback.get_output()
    helpers.hint()
    result = friendly_traceback.get_output()
    assert _hint in result
    assert _message not in result
    assert "File" not in result
    assert friendly_traceback.config.session.recorded_tracebacks
    del helpers.history[-1]
    assert not friendly_traceback.config.session.recorded_tracebacks


def test_history():
    friendly_traceback.set_stream(redirect="capture")
    helpers.history.clear()
    try:
        a
    except NameError:
        friendly_traceback.explain_traceback(redirect="capture")
        friendly_traceback.get_output()
    helpers.history()
    assert "NameError" in friendly_traceback.get_output()
    assert friendly_traceback.config.session.recorded_tracebacks
    del helpers.history[-1]
    helpers.history()
    assert not friendly_traceback.config.session.recorded_tracebacks


def test_python_tb():
    friendly_traceback.set_stream(redirect="capture")
    helpers.history.clear()
    try:
        math.Pi
    except AttributeError:
        friendly_traceback.explain_traceback(redirect="capture")
        friendly_traceback.get_output()
    helpers.python_tb()
    result = friendly_traceback.get_output()
    assert "Did you mean `pi`" not in result
    assert "AttributeError" in result
    assert "File" in result
    assert friendly_traceback.config.session.recorded_tracebacks
    del helpers.history[-1]
    assert not friendly_traceback.config.session.recorded_tracebacks


def test_what():
    friendly_traceback.set_stream(redirect="capture")
    helpers.history.clear()
    try:
        math.Pi
    except AttributeError:
        friendly_traceback.explain_traceback(redirect="capture")
        friendly_traceback.get_output()
    helpers.what()
    result = friendly_traceback.get_output()
    assert _hint not in result
    assert _message not in result
    assert "File" not in result
    assert _what in result
    assert _where not in result
    assert _why not in result
    assert friendly_traceback.config.session.recorded_tracebacks
    del helpers.history[-1]
    assert not friendly_traceback.config.session.recorded_tracebacks


def test_what_name():
    friendly_traceback.set_stream(redirect="capture")
    helpers.history.clear()
    try:
        math.Pi
    except AttributeError:
        friendly_traceback.explain_traceback(redirect="capture")
        friendly_traceback.get_output()
    helpers.what('NameError')
    result = friendly_traceback.get_output()
    assert _hint not in result
    assert _message not in result
    assert "File" not in result
    assert _what not in result
    assert _where not in result
    assert _why not in result
    assert "NameError" in result
    assert friendly_traceback.config.session.recorded_tracebacks
    del helpers.history[-1]
    assert not friendly_traceback.config.session.recorded_tracebacks


def test_what_type():
    friendly_traceback.set_stream(redirect="capture")
    helpers.history.clear()
    try:
        math.Pi
    except AttributeError:
        friendly_traceback.explain_traceback(redirect="capture")
        friendly_traceback.get_output()
    helpers.what(LookupError)
    result = friendly_traceback.get_output()
    assert _hint not in result
    assert _message not in result
    assert "File" not in result
    assert _what not in result
    assert _where not in result
    assert _why not in result
    assert "LookupError" in result
    assert friendly_traceback.config.session.recorded_tracebacks
    del helpers.history[-1]
    assert not friendly_traceback.config.session.recorded_tracebacks

def test_where():
    friendly_traceback.set_stream(redirect="capture")
    helpers.history.clear()
    try:
        math.Pi
    except AttributeError:
        friendly_traceback.explain_traceback(redirect="capture")
        friendly_traceback.get_output()
    helpers.where()
    result = friendly_traceback.get_output()
    assert _hint not in result
    assert _message not in result
    assert "File" not in result
    assert _what not in result
    assert _where in result
    assert _why not in result
    assert friendly_traceback.config.session.recorded_tracebacks
    del helpers.history[-1]
    assert not friendly_traceback.config.session.recorded_tracebacks


def test_why():
    friendly_traceback.set_stream(redirect="capture")
    helpers.history.clear()
    try:
        math.Pi
    except AttributeError:
        friendly_traceback.explain_traceback(redirect="capture")
        friendly_traceback.get_output()
    helpers.why()
    result = friendly_traceback.get_output()
    assert _hint not in result
    assert _message not in result
    assert "File" not in result
    assert _what not in result
    assert _where not in result
    assert _why in result
    assert friendly_traceback.config.session.recorded_tracebacks
    del helpers.history[-1]
    assert not friendly_traceback.config.session.recorded_tracebacks


# The following are processed in base_formatters.py

def test_why_no_hint():
    friendly_traceback.set_stream(redirect="capture")
    helpers.history.clear()
    try:
        math.PiPiPi
    except AttributeError:
        friendly_traceback.explain_traceback(redirect="capture")
        friendly_traceback.get_output()
    helpers.why()
    result = friendly_traceback.get_output()
    assert "Python tells us" in result
    helpers.hint()
    result = friendly_traceback.get_output()
    assert "I have no suggestion to offer; try `why()`." in result
    assert friendly_traceback.config.session.recorded_tracebacks
    del helpers.history[-1]
    assert not friendly_traceback.config.session.recorded_tracebacks

def test_no_why():
    friendly_traceback.set_stream(redirect="capture")
    helpers.history.clear()
    try:
        raise ArithmeticError("unknown")
    except ArithmeticError:
        friendly_traceback.explain_traceback(redirect="capture")
        friendly_traceback.get_output()
    helpers.why()
    result = friendly_traceback.get_output()
    assert "I have no suggestion to offer." in result
    helpers.hint()
    new_result = friendly_traceback.get_output()
    assert "I have no suggestion to offer." in new_result
    assert friendly_traceback.config.session.recorded_tracebacks
    del helpers.history[-1]
    assert not friendly_traceback.config.session.recorded_tracebacks


def test_no_why_no_message():
    friendly_traceback.set_stream(redirect="capture")
    helpers.history.clear()
    try:
        raise ArithmeticError  # no message
    except ArithmeticError:
        friendly_traceback.explain_traceback(redirect="capture")
        friendly_traceback.get_output()
    why = helpers.why()
    what = helpers.what()
    assert why == what
    assert friendly_traceback.config.session.recorded_tracebacks
    del helpers.history[0]  # to be different
    assert not friendly_traceback.config.session.recorded_tracebacks