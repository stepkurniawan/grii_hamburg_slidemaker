def test_insert_annoucement_slides_uses_configured_folder(monkeypatch, image_bytes):
    from grii_slide_maker.slides import announcements

    calls = []
    monkeypatch.setattr(announcements.settings, "ANNOUCEMENT_FOLDER_ID", "folder-1")
    monkeypatch.setattr(
        announcements,
        "save_images_from_google_folder_to_memory",
        lambda folder_id: {"Slide1.JPG": image_bytes},
    )
    monkeypatch.setattr(
        announcements,
        "make_slides_from_imgs",
        lambda prs, images: calls.append({"prs": prs, "images": images}),
    )

    prs = object()
    announcements.insert_annoucement_slides(prs)

    assert calls == [{"prs": prs, "images": [image_bytes]}]
