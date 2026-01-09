"""
Entry point for release syncing.

Downloads installer artifacts for requested versions and creates GitHub Releases.
"""

import os
import sys
import json
import logging
import tempfile
import subprocess
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.fetcher import get_gcs_bucket, get_manifest
from lib.downloader import download_version_files
from lib.changelog import fetch_changelog, extract_notes
from lib.version import save_synced
from lib.release import release_exists, create_release
from lib.metadata import save_version_metadata

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)


def git_commit_and_push(version: str) -> None:
    """
    Commit and push the `version.json` and `releases/{version}/` updates.

    Args:
        version: The version that was just synced.
    """
    try:
        # Add version.json
        subprocess.run(
            ["git", "add", "version.json"],
            check=True,
            capture_output=True
        )

        # Add releases/{version}/ directory
        releases_path = f"releases/{version}"
        subprocess.run(
            ["git", "add", releases_path],
            check=True,
            capture_output=True
        )

        commit_msg = f":bookmark: Release version {version}"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            check=True,
            capture_output=True
        )

        subprocess.run(
            ["git", "push"],
            check=True,
            capture_output=True
        )

        log.info(f"Git commit and push succeeded: [{commit_msg}]")

    except subprocess.CalledProcessError as e:
        log.warning(f"Git operation failed: {e.stderr.decode() if e.stderr else str(e)}")


def sync_one_version(
    gcs_bucket: str,
    version: str,
    changelog_content: str
) -> bool:
    """
    Sync a single version.

    Args:
        gcs_bucket: GCS_BUCKET base URL.
        version: Version to sync.
        changelog_content: Full CHANGELOG content.

    Returns:
        True on success, False on failure.
    """
    log.info(f"========== Start syncing version [{version}] ==========")

    try:
        if release_exists(version):
            log.info(f"Release for version [{version}] already exists; skipping")
            save_synced(version)
            return True

        manifest = get_manifest(gcs_bucket, version)

        with tempfile.TemporaryDirectory() as tmpdir:
            files = download_version_files(
                gcs_bucket, version, manifest, Path(tmpdir)
            )

            notes = extract_notes(changelog_content, version)

            # Save version metadata to releases/{version}/
            try:
                save_version_metadata(version, notes, manifest)
            except (IOError, OSError) as e:
                log.error(f"Failed to save metadata for version [{version}]: {e}")
                raise  # Terminate flow on failure

            save_synced(version)

            git_commit_and_push(version)

            create_release(version, notes, files)

        log.info(f"========== Version [{version}] synced successfully ==========")
        return True

    except Exception as e:
        log.error(f"Failed to sync version [{version}]: {e}", exc_info=True)
        return False


def main(versions_json: str) -> int:
    """
    Main entry point.

    Args:
        versions_json: JSON string of versions to sync.

    Returns:
        0 if all versions succeeded, otherwise 1.
    """
    try:
        versions = json.loads(versions_json)
        if not versions:
            log.info("Version list is empty; nothing to do")
            return 0

        log.info(f"Versions to sync: {versions}")

        gcs_bucket = get_gcs_bucket()
        changelog_content = fetch_changelog()

        success_count = 0
        fail_count = 0

        for version in versions:
            if sync_one_version(gcs_bucket, version, changelog_content):
                success_count += 1
            else:
                fail_count += 1

        log.info(f"Sync finished: succeeded [{success_count}], failed [{fail_count}]")

        return 0 if fail_count == 0 else 1

    except json.JSONDecodeError as e:
        log.error(f"Failed to parse versions JSON: {e}")
        return 1
    except Exception as e:
        log.error(f"Sync failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sync_release.py '<json_versions>'")
        print('Example: python sync_release.py \'["1.0.37","1.0.38"]\'')
        sys.exit(1)

    sys.exit(main(sys.argv[1]))
