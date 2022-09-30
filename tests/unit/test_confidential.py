import friendly_traceback as ft

def test_confidential():
    confidential = ft.info_variables.confidential
    confidential.hide_confidential_information(patterns=["password", "secret.*"])
    secret_names = ["password", "secret1", "secret_2"]
    for name in secret_names:
        assert confidential.redact_confidential(name, "anything") == confidential.redacted

    safe_names = ["password_1", "Python", "not_secret"]
    for name in safe_names:
        assert confidential.redact_confidential(name, "anything") != confidential.redacted

def test_confidential_api():
    confidential = ft.info_variables.confidential
    ft.hide_secrets(patterns=["password", "secret.*"])
    secret_names = ["password", "secret1", "secret_2"]
    for name in secret_names:
        assert ft.test_secrets(name, "anything") == confidential.redacted

    safe_names = ["password_1", "Python", "not_secret"]
    for name in safe_names:
        assert ft.test_secrets(name, "anything") != confidential.redacted

    assert ft.test_secrets("anything", "confidential password") == confidential.redacted
