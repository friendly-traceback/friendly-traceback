import friendly_traceback

def test_No_exception(capsys):
    if friendly_traceback.get_lang() == "en":
        friendly_traceback.explain_traceback()
        captured = capsys.readouterr()
        assert "Nothing to show: no exception recorded." in captured.out
