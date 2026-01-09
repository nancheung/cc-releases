"""
Entry point for update checks.

Emits the pending version list for GitHub Actions.
"""

import os
import sys
import json
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.config import MAX_PER_RUN
from lib.changelog import fetch_changelog, parse_versions
from lib.version import load_synced, get_pending

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)


def set_output(name: str, value: str) -> None:
    """
    Set a GitHub Actions output variable.

    Args:
        name: Output variable name.
        value: Output variable value.
    """
    # Newer GitHub Actions runners use the GITHUB_OUTPUT file.
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"{name}={value}\n")
    else:
        print(f"::set-output name={name}::{value}")


def main() -> int:
    """
    Main entry point.

    Returns:
        0 on success, 1 on failure.
    """
    try:
        log.info("Starting update check...")

        content = fetch_changelog()
        all_versions = parse_versions(content)

        if not all_versions:
            log.warning("No versions parsed from CHANGELOG")
            set_output("has_updates", "false")
            return 0

        synced = load_synced()

        pending = get_pending(all_versions, synced)

        if not pending:
            log.info("No pending versions")
            set_output("has_updates", "false")
            return 0

        batch = pending[:MAX_PER_RUN]
        log.info(f"Versions to process in this run: {batch}")

        set_output("has_updates", "true")
        set_output("versions", json.dumps(batch))

        log.info(f"Update check complete; pending versions in this batch: [{len(batch)}]")
        return 0

    except Exception as e:
        log.error(f"Update check failed: {e}", exc_info=True)
        set_output("has_updates", "false")
        return 1


if __name__ == "__main__":
    sys.exit(main())
