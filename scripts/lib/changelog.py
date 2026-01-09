"""
CHANGELOG parsing helpers.

Fetches and parses `CHANGELOG.md` from the upstream repository.
"""

import re
import logging

import requests

from .config import CHANGELOG_URL, REQUEST_TIMEOUT

log = logging.getLogger(__name__)


def fetch_changelog() -> str:
    """
    Fetch the raw `CHANGELOG.md` content.

    Returns:
        The `CHANGELOG.md` text.

    Raises:
        requests.HTTPError: If the request fails.
    """
    log.info(f"Fetching CHANGELOG: [{CHANGELOG_URL}]")

    resp = requests.get(CHANGELOG_URL, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()

    content = resp.text
    log.info(f"CHANGELOG fetched successfully; length [{len(content)}] chars")
    return content


def parse_versions(content: str) -> list[str]:
    """
    Parse all versions from CHANGELOG content.

    Version format: second-level heading `## x.y.z`.

    Args:
        content: The `CHANGELOG.md` text.

    Returns:
        Version list in appearance order (usually newest to oldest).
    """
    # Matches `## 1.2.3` or `## 1.2.3-beta.1`, etc.
    pattern = r"^## (\d+\.\d+\.\d+(?:-[\w.]+)?)\s*$"
    versions = re.findall(pattern, content, re.MULTILINE)

    log.info(f"Parsed [{len(versions)}] versions from CHANGELOG")
    return versions


def extract_notes(content: str, version: str) -> str:
    """
    Extract release notes for a given version from the CHANGELOG.

    Args:
        content: The `CHANGELOG.md` text.
        version: Target version.

    Returns:
        Release notes for that version, or an empty string if not found.
    """
    # Escape special characters in the version string.
    escaped_version = re.escape(version)

    # Match content from this version heading up to the next version heading.
    pattern = rf"^## {escaped_version}\s*\n(.*?)(?=^## \d+\.\d+\.\d+|\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

    if not match:
        log.warning(f"No release notes found for version [{version}]")
        return ""

    notes = match.group(1).strip()
    log.info(f"Release notes for version [{version}] length [{len(notes)}] chars")
    return notes
