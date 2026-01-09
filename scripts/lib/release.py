"""
GitHub Release helpers.

Uses the `gh` CLI to check for and create GitHub Releases.
"""

import subprocess
import logging
from pathlib import Path

log = logging.getLogger(__name__)


def release_exists(version: str) -> bool:
    """
    Check whether a GitHub Release exists for the given version.

    Args:
        version: Version string.

    Returns:
        True if the release already exists.
    """
    tag = f"v{version}"
    result = subprocess.run(
        ["gh", "release", "view", tag],
        capture_output=True,
        text=True
    )
    exists = result.returncode == 0

    if exists:
        log.info(f"Release [{tag}] already exists")
    return exists


def create_release(version: str, notes: str, files: list[Path]) -> None:
    """
    Create a GitHub Release and upload attachments.

    Args:
        version: Version string.
        notes: Release notes (changelog excerpt).
        files: Files to upload.

    Raises:
        RuntimeError: If release creation fails.
    """
    tag = f"v{version}"
    log.info(f"Creating release [{tag}] with [{len(files)}] attachment(s)...")

    cmd = [
        "gh", "release", "create", tag,
        "--title", tag,
        "--notes", notes if notes else f"Release {version}",
    ]

    for f in files:
        cmd.append(str(f))

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        log.error(f"Release creation failed: {result.stderr}")
        raise RuntimeError(f"Release creation failed for [{tag}]: {result.stderr}")

    log.info(f"Release [{tag}] created successfully")


def delete_release(version: str) -> bool:
    """
    Delete a GitHub Release (used to clean up failed publishes).

    Args:
        version: Version string.

    Returns:
        True if deletion succeeded.
    """
    tag = f"v{version}"
    result = subprocess.run(
        ["gh", "release", "delete", tag, "--yes", "--cleanup-tag"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        log.info(f"Release [{tag}] deleted")
        return True
    else:
        log.warning(f"Failed to delete release [{tag}]: {result.stderr}")
        return False
