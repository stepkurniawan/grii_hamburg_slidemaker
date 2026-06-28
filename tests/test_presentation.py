from grii_slide_maker.presentation import (
    SlideDeckActions,
    add_bible_reading_with_status,
    add_song_with_status,
)


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


def test_add_bible_reading_with_status_reports_error_when_insert_fails():
    calls = []

    def fail_insert(prs, bible_reference):
        raise RuntimeError("BibleSuperSearch unavailable")

    actions = SlideDeckActions(add_bible_reading_page=fail_insert)

    add_bible_reading_with_status(
        "prs",
        "Romans 12:17-21",
        error_writer=lambda text: calls.append(("error", text)),
        actions=actions,
    )

    assert calls == [
        (
            "error",
            "Error: Cannot add Bible reading Romans 12:17-21: BibleSuperSearch unavailable",
        )
    ]
