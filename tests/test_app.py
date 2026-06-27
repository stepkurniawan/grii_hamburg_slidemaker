import datetime

from grii_slide_maker import app


class FixedDate(datetime.date):
    @classmethod
    def today(cls):
        return cls(2026, 6, 26)


def test_app_sunday_date_delegates_to_date_helper(monkeypatch):
    monkeypatch.setattr(app.datetime, "date", FixedDate)

    assert app.sunday_date("filename") == "20260628"


def test_app_print_helpers_write_to_streamlit_and_stdout(monkeypatch, capsys):
    st_calls = []
    monkeypatch.setattr(app.st, "write", lambda text: st_calls.append(("write", text)))
    monkeypatch.setattr(app.st, "error", lambda text: st_calls.append(("error", text)))

    app.st_print("hello")
    app.st_error_print("oops")

    assert st_calls == [("write", "hello"), ("error", "oops")]
    assert capsys.readouterr().out == "hello\noops\n"
