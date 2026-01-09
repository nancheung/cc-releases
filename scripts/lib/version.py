"""
Version index management.

Loads, updates, and compares versions using `packaging.version`.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from packaging.version import Version

from .config import MIN_VERSION, VERSION_FILE

log = logging.getLogger(__name__)


def load_synced() -> list[str]:
    """
    Load the synced version list from `version.json`.

    Returns:
        Synced versions (empty if the file does not exist).
    """
    version_path = Path(VERSION_FILE)

    if not version_path.exists():
        log.info(f"Version index file [{VERSION_FILE}] does not exist; returning empty list")
        return []

    try:
        with open(version_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        synced = data.get("synced", [])
        log.info(f"Loaded [{len(synced)}] synced version(s)")
        return synced
    except (json.JSONDecodeError, IOError) as e:
        log.error(f"Failed to read version index: {e}")
        return []


def save_synced(version: str) -> None:
    """
    Add a version to `version.json` and update metadata.

    The list is kept sorted by version (newest to oldest), and `latestSynced`
    is set to the newest version.

    Args:
        version: Newly synced version string.
    """
    version_path = Path(VERSION_FILE)

    if version_path.exists():
        with open(version_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"synced": []}

    synced = data.get("synced", [])
    if version not in synced:
        synced.append(version)
        synced.sort(key=lambda v: Version(v), reverse=True)

    data["synced"] = synced
    data["lastRun"] = datetime.now(timezone.utc).isoformat()
    data["latestSynced"] = synced[0] if synced else ""

    with open(version_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    log.info(f"Version [{version}] added to index; total versions [{len(synced)}]")


def get_pending(all_versions: list[str], synced: list[str]) -> list[str]:
    """
    Compute the list of versions that still need syncing.

    Args:
        all_versions: All versions found upstream.
        synced: Versions already synced.

    Returns:
        Pending versions (>= MIN_VERSION), sorted oldest to newest.
    """
    synced_set = set(synced)
    min_ver = Version(MIN_VERSION)

    pending = [
        v for v in all_versions
        if v not in synced_set and Version(v) >= min_ver
    ]

    pending.sort(key=lambda v: Version(v))

    log.info(
        f"All versions [{len(all_versions)}], "
        f"synced [{len(synced)}], "
        f"pending [{len(pending)}]"
    )

    return pending


def compare(v1: str, v2: str) -> int:
    """
    Compare two version strings.

    Args:
        v1: Version 1.
        v2: Version 2.

    Returns:
        -1 if v1 < v2, 0 if v1 == v2, 1 if v1 > v2.
    """
    ver1 = Version(v1)
    ver2 = Version(v2)

    if ver1 < ver2:
        return -1
    elif ver1 > ver2:
        return 1
    else:
        return 0
