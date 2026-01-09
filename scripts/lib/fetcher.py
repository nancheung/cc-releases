"""
Metadata fetch helpers.

Fetches the upstream `GCS_BUCKET` base URL and `manifest.json`.
"""

import re
import json
import logging
import requests

from .config import INSTALL_SCRIPT_URL, REQUEST_TIMEOUT

log = logging.getLogger(__name__)


def get_gcs_bucket() -> str:
    """
    Parse the official install script to extract the `GCS_BUCKET` URL.

    Returns:
        GCS_BUCKET URL (without a trailing slash).

    Raises:
        RuntimeError: If parsing fails.
    """
    log.info("Fetching GCS_BUCKET URL...")

    # `install.sh` may redirect to the actual script.
    resp = requests.get(INSTALL_SCRIPT_URL, timeout=REQUEST_TIMEOUT, allow_redirects=True)
    resp.raise_for_status()

    # Extract `GCS_BUCKET="https://storage.googleapis.com/..."` from the script.
    match = re.search(r'GCS_BUCKET="([^"]+)"', resp.text)
    if not match:
        raise RuntimeError("Failed to parse GCS_BUCKET from install script")

    bucket = match.group(1).rstrip("/")
    log.info(f"GCS_BUCKET: [{bucket}]")
    return bucket


def get_manifest(gcs_bucket: str, version: str) -> dict:
    """
    Fetch `manifest.json` for a given version.
    Returns fallback structure on download failure instead of raising exception.

    Args:
        gcs_bucket: GCS_BUCKET base URL.
        version: Target version.

    Returns:
        Manifest dict containing `platforms`.
        In fallback mode: {"version": "...", "buildDate": null, "platforms": {}, "_fallback_mode": True}
    """
    url = f"{gcs_bucket}/{version}/manifest.json"
    log.info(f"Fetching manifest: [{url}]")

    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        manifest = resp.json()
        log.info(f"Version [{version}] contains [{len(manifest.get('platforms', {}))}] platforms")
        return manifest

    except (requests.RequestException, json.JSONDecodeError) as e:
        log.warning(
            f"Failed to fetch manifest for version [{version}]: {e}. "
            f"Entering fallback mode (no binary downloads)"
        )

        return {
            "version": version,
            "buildDate": None,
            "platforms": {},
            "_fallback_mode": True
        }


def get_latest_version(gcs_bucket: str) -> str:
    """
    Fetch the latest upstream version string.

    Args:
        gcs_bucket: GCS_BUCKET base URL.

    Returns:
        Latest version string.
    """
    url = f"{gcs_bucket}/latest"
    log.info(f"Fetching latest version: [{url}]")

    resp = requests.get(url, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()

    version = resp.text.strip()
    log.info(f"Latest version: [{version}]")
    return version
