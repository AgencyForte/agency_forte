from __future__ import annotations

import argparse
from dotenv import load_dotenv

from .config import get_settings
from .db import connect, get_master_counts, get_stage_counts
from .events import dump_guard_breached


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Inspect staged versus master Insuretra data.")
    parser.add_argument("--dry-run", action="store_true", help="Only print counts and dump guard result.")
    args = parser.parse_args()

    settings = get_settings()
    if not settings.database_url:
        raise SystemExit("DATABASE_URL is required.")

    with connect(settings.database_url) as conn:
        stage_counts = get_stage_counts(conn)
        master_counts = get_master_counts(conn)
        breached, delta = dump_guard_breached(stage_counts, master_counts, settings.dump_guard_threshold)
        print({"stage": stage_counts, "master": master_counts, "delta": delta, "dump_guard_breached": breached})
        if not args.dry_run:
            print("Use run_daily to generate events and consolidate master state.")


if __name__ == "__main__":
    main()

