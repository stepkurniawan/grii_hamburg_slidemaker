from grii_slide_maker.presentation import SlideDeckActions, add_song_with_status


def test_add_song_with_status_inserts_song_and_writes_status():
    calls = []
    actions = SlideDeckActions(
        insert_song_slides_drive_folder=lambda prs, song_number: calls.append(
            ("song", prs, song_number)
        )
    )

    add_song_with_status(
        "prs",
        "161",
        status="Adding song",
        error="Error adding song",
        status_writer=lambda text: calls.append(("status", text)),
        error_writer=lambda text: calls.append(("error", text)),
        actions=actions,
    )

    assert calls == [("status", "Adding song"), ("song", "prs", "161")]


def test_add_song_with_status_reports_error_when_insert_fails():
    calls = []

    def fail_insert(prs, song_number):
        raise RuntimeError("Drive failed")

    actions = SlideDeckActions(insert_song_slides_drive_folder=fail_insert)

    add_song_with_status(
        "prs",
        "161",
        status="Adding song",
        error="Error adding song",
        status_writer=lambda text: calls.append(("status", text)),
        error_writer=lambda text: calls.append(("error", text)),
        actions=actions,
    )

    assert calls == [("status", "Adding song"), ("error", "Error adding song")]
