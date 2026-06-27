"""Cron schedule parsing for the automated slide generator."""

from dataclasses import dataclass


DAY_TO_CRON = {
    "sun": 0,
    "mon": 1,
    "tue": 2,
    "wed": 3,
    "thu": 4,
    "fri": 5,
    "sat": 6,
}

MANAGED_CRON_BEGIN = "# BEGIN grii-slide-auto"
MANAGED_CRON_END = "# END grii-slide-auto"


@dataclass(frozen=True)
class AutomationSchedule:
    day: str
    hour: int
    minute: int

    @property
    def cron_weekday(self) -> int:
        normalized_day = self.day.strip().lower()[:3]
        try:
            return DAY_TO_CRON[normalized_day]
        except KeyError as error:
            valid_days = ", ".join(day.title() for day in DAY_TO_CRON)
            raise ValueError(f"Day must be one of: {valid_days}") from error

    def cron_expression(self) -> str:
        if not 0 <= self.hour <= 23:
            raise ValueError("Hour must be between 0 and 23")
        if not 0 <= self.minute <= 59:
            raise ValueError("Minute must be between 0 and 59")

        return f"{self.minute} {self.hour} * * {self.cron_weekday}"


def build_cron_block(schedule: AutomationSchedule, command: str) -> str:
    """Build a managed cron block from a schedule and command.

    Input:
    - schedule: AutomationSchedule instance containing day, hour, and minute.
    - command: shell command to run on the cron schedule.

    Output:
    - A string containing the managed cron block with begin/end markers.
    """
    return "\n".join(
        [
            MANAGED_CRON_BEGIN,
            f"{schedule.cron_expression()} {command}",
            MANAGED_CRON_END,
        ]
    )


def replace_managed_cron_block(existing_crontab: str, new_block: str) -> str:
    """Replace or append a managed cron block in a crontab string.

    Input:
    - existing_crontab: the current crontab content as a string.
    - new_block: the managed cron block to insert or replace.

    Output:
    - Updated crontab content as a string, with the managed block replaced if present,
      otherwise appended to the end.
    """
    lines = existing_crontab.splitlines()
    output_lines = []
    inside_managed_block = False
    replaced = False

    for line in lines:
        if line.strip() == MANAGED_CRON_BEGIN:
            if not replaced:
                output_lines.extend(new_block.splitlines())
                replaced = True
            inside_managed_block = True
            continue

        if inside_managed_block:
            if line.strip() == MANAGED_CRON_END:
                inside_managed_block = False
            continue

        output_lines.append(line)

    if not replaced:
        if output_lines and output_lines[-1] != "":
            output_lines.append("")
        output_lines.extend(new_block.splitlines())

    return "\n".join(output_lines).rstrip() + "\n"


def remove_managed_cron_block(existing_crontab: str) -> str:
    """Remove a managed cron block from a crontab string.

    Input:
    - existing_crontab: the current crontab content as a string.

    Output:
    - Updated crontab content as a string with the managed block removed.
    """
    lines = existing_crontab.splitlines()
    output_lines = []
    inside_managed_block = False

    for line in lines:
        if line.strip() == MANAGED_CRON_BEGIN:
            inside_managed_block = True
            continue

        if inside_managed_block:
            if line.strip() == MANAGED_CRON_END:
                inside_managed_block = False
            continue

        output_lines.append(line)

    return "\n".join(output_lines).rstrip() + "\n" if output_lines else ""
