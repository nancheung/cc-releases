"""
Version metadata saving module
Saves changelog and manifest to releases/{version}/ directory
"""

import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)


def save_version_metadata(
    version: str,
    changelog_notes: str,
    manifest: dict,
    base_dir: Path = None
) -> Path:
    """
    Save version metadata to releases/{version}/ directory

    File structure:
    releases/
      {version}/
        changelog.md   - Release notes for this version (current version only)
        manifest.json  - Complete manifest.json

    Args:
        version: Version number (e.g., "1.0.48")
        changelog_notes: Changelog content for this version (extracted via extract_notes)
        manifest: Dictionary object of manifest.json
        base_dir: Base directory path, defaults to repository root

    Returns:
        Path object of the version directory

    Raises:
        IOError: Raised when file write fails
        OSError: Raised when directory creation fails
    """
    # Determine base directory (defaults to repository root)
    if base_dir is None:
        # Navigate from scripts/lib/metadata.py back to repository root
        base_dir = Path(__file__).parent.parent.parent

    # Create version directory
    version_dir = base_dir / "releases" / version

    try:
        # Create directory (overwrite if exists, parents=True auto-creates parent directories)
        version_dir.mkdir(parents=True, exist_ok=True)
        log.info(f"Created version directory: [{version_dir}]")

        # Save changelog.md
        changelog_path = version_dir / "changelog.md"
        with open(changelog_path, "w", encoding="utf-8") as f:
            # Write version title and release content
            f.write(f"# Release {version}\n\n")

            # Add fallback mode warning if applicable
            if manifest.get("_fallback_mode", False):
                f.write("> **Note:** This release has no binary installers due to manifest.json fetch failure.\n")
                f.write("> Please visit the official repository for downloads or wait for updates.\n\n")

            f.write(changelog_notes)

        log.info(f"Saved changelog: [{changelog_path}] ({len(changelog_notes)} characters)")

        # Save manifest.json
        manifest_path = version_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        platforms_count = len(manifest.get("platforms", {}))
        log.info(f"Saved manifest: [{manifest_path}] ({platforms_count} platforms)")

        log.info(f"Version [{version}] metadata saved successfully: [{version_dir}]")
        return version_dir

    except (IOError, OSError) as e:
        log.error(f"Failed to save version [{version}] metadata: {e}")
        raise
