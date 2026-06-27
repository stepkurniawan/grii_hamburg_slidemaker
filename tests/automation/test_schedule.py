import pytest

from grii_slide_maker.automation.schedule import (
    AutomationSchedule,
    build_cron_block,
    remove_managed_cron_block,
    replace_managed_cron_block,
)


def test_schedule_maps_three_letter_day_to_cron_expression():
    schedule = AutomationSchedule(day="Sun", hour=9, minute=30)

    assert schedule.cron_expression() == "30 9 * * 0"


def test_schedule_rejects_invalid_values():
    with pytest.raises(ValueError, match="Hour"):
        AutomationSchedule(day="Sun", hour=24, minute=0).cron_expression()

    with pytest.raises(ValueError, match="Day"):
        AutomationSchedule(day="Bad", hour=9, minute=0).cron_expression()


def test_build_cron_block_adds_managed_markers():
    block = build_cron_block(
        AutomationSchedule(day="Mon", hour=7, minute=5),
        "cd /repo && uv run grii-slide-auto generate",
    )

    assert block == (
        "# BEGIN grii-slide-auto\n"
        "5 7 * * 1 cd /repo && uv run grii-slide-auto generate\n"
        "# END grii-slide-auto"
    )


def test_replace_managed_cron_block_preserves_unrelated_entries():
    existing = (
        "0 1 * * * backup\n"
        "# BEGIN grii-slide-auto\n"
        "0 8 * * 0 old-command\n"
        "# END grii-slide-auto\n"
        "0 2 * * * cleanup\n"
    )
    new_block = "# BEGIN grii-slide-auto\n30 9 * * 0 new-command\n# END grii-slide-auto"

    updated = replace_managed_cron_block(existing, new_block)

    assert updated == (
        "0 1 * * * backup\n"
        "# BEGIN grii-slide-auto\n"
        "30 9 * * 0 new-command\n"
        "# END grii-slide-auto\n"
        "0 2 * * * cleanup\n"
    )


def test_replace_managed_cron_block_appends_when_missing():
    new_block = "# BEGIN grii-slide-auto\n30 9 * * 0 new-command\n# END grii-slide-auto"

    updated = replace_managed_cron_block("0 1 * * * backup\n", new_block)

    assert updated == (
        "0 1 * * * backup\n"
        "\n"
        "# BEGIN grii-slide-auto\n"
        "30 9 * * 0 new-command\n"
        "# END grii-slide-auto\n"
    )


def test_remove_managed_cron_block_preserves_unrelated_entries():
    existing = (
        "0 1 * * * backup\n"
        "# BEGIN grii-slide-auto\n"
        "30 9 * * 0 generate-command\n"
        "# END grii-slide-auto\n"
        "0 2 * * * cleanup\n"
    )

    updated = remove_managed_cron_block(existing)

    assert updated == "0 1 * * * backup\n0 2 * * * cleanup\n"
