"""Command line entrypoint for scheduled slide generation."""

from __future__ import annotations

import argparse
import datetime
from io import BytesIO
import os
import shlex
import subprocess
import sys

from openpyxl.workbook.workbook import Workbook

from grii_slide_maker.automation.excel import (
    load_workbook_from_bytes,
    parse_automation_enabled,
    parse_schedule,
    parse_service_order,
)
from grii_slide_maker.automation.schedule import (
    build_cron_block,
    remove_managed_cron_block,
    replace_managed_cron_block,
)
from grii_slide_maker.config import Settings, get_settings
from grii_slide_maker.dates import sunday_date as format_sunday_date
from grii_slide_maker.paths import OUTPUT_DIR, TEMPLATE_FILE
from grii_slide_maker.presentation import build_service_slides
from grii_slide_maker.services.google_drive import (
    download_excel_file_to_memory,
    upload_or_replace_file,
)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="grii-slide-auto",
        description="Generate and schedule GRII Europe service slides from Drive Excel.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="Generate slides and upload them to Drive.")
    generate.set_defaults(func=generate_command)

    print_cron = subparsers.add_parser("print-cron", help="Print the cron expression from Excel.")
    print_cron.add_argument("--command", default=default_generate_command())
    print_cron.set_defaults(func=print_cron_command)

    sync_cron = subparsers.add_parser("sync-cron", help="Update the managed crontab block.")
    sync_cron.add_argument("--command", default=default_generate_command())
    sync_cron.set_defaults(func=sync_cron_command)

    return parser


def generate_command(args: argparse.Namespace) -> int:
    settings = get_settings()
    workbook = _load_automation_workbook(settings)
    service_order = parse_service_order(workbook, settings)

    binary_output_file = BytesIO()
    build_service_slides(
        service_order,
        template_file=TEMPLATE_FILE,
        output_dir=OUTPUT_DIR,
        binary_output_file=binary_output_file,
        sunday_date=sunday_date,
        status_writer=print,
        error_writer=print,
    )

    filename = sunday_date("filename") + ".pptx"
    uploaded_file_id = upload_or_replace_file(
        filename=filename,
        content=binary_output_file.getvalue(),
        folder_id=settings.GOOGLE_DRIVE_OUTPUT_FOLDER_ID,
        mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )
    print(f"Uploaded {filename} to Google Drive as {uploaded_file_id}")
    return 0


def print_cron_command(args: argparse.Namespace) -> int:
    settings = get_settings()
    workbook = _load_automation_workbook(settings)
    schedule = parse_schedule(workbook, settings)
    print(build_cron_block(schedule, args.command))
    return 0


def sync_cron_command(args: argparse.Namespace) -> int:
    settings = get_settings()
    workbook = _load_automation_workbook(settings)
    existing_crontab = read_crontab()

    if not parse_automation_enabled(workbook, settings):
        updated_crontab = remove_managed_cron_block(existing_crontab)
        write_crontab(updated_crontab)
        print("Automation is disabled in Excel; removed managed grii-slide-auto crontab block.")
        return 0

    schedule = parse_schedule(workbook, settings)
    new_block = build_cron_block(schedule, args.command)
    updated_crontab = replace_managed_cron_block(existing_crontab, new_block)
    write_crontab(updated_crontab)
    print("Updated managed grii-slide-auto crontab block.")
    return 0


def _load_automation_workbook(settings: Settings) -> Workbook:
    if not settings.GOOGLE_SHEET_MASTER_WARTA_ID:
        raise ValueError("GOOGLE_SHEET_MASTER_WARTA_ID is required for automation")
    workbook_bytes = download_excel_file_to_memory(settings.GOOGLE_SHEET_MASTER_WARTA_ID)
    return load_workbook_from_bytes(workbook_bytes)


def sunday_date(formatted: str) -> str:
    return format_sunday_date(formatted, today=datetime.date.today())


def default_generate_command() -> str:
    # Build the default shell command used for scheduled execution.
    # It changes the working directory to the repository root and then
    # runs the `grii-slide-auto generate` entrypoint through the UV runtime.
    return f"cd {shlex.quote(os.getcwd())} && uv run grii-slide-auto generate"


def read_crontab() -> str:
    result = subprocess.run(
        ["sudo", "crontab", "-l"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout
    if result.returncode == 1 and not result.stdout and "no crontab" in result.stderr.lower():
        return ""
    if result.returncode == 1 and not result.stdout:
        return ""
    raise RuntimeError(result.stderr.strip() or "Unable to read sudo crontab")


def write_crontab(content: str) -> None:
    subprocess.run(
        ["sudo", "crontab", "-"],
        input=content,
        check=True,
        text=True,
    )


if __name__ == "__main__":
    sys.exit(main())
