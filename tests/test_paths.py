import os

from grii_slide_maker import paths


def test_get_resource_path_uses_current_dir_without_pyinstaller(monkeypatch):
    monkeypatch.delattr(paths.sys, "_MEIPASS", raising=False)
    monkeypatch.setattr(paths, "CURRENT_DIR", "/app")

    assert paths.get_resource_path("template.pptx") == os.path.join(
        "/app", "template.pptx"
    )


def test_get_resource_path_uses_pyinstaller_temp_dir(monkeypatch):
    monkeypatch.setattr(paths.sys, "_MEIPASS", "/tmp/bundle", raising=False)

    assert paths.get_resource_path("template.pptx") == os.path.join(
        "/tmp/bundle", "template.pptx"
    )
