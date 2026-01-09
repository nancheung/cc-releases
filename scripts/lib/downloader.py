"""
File download and verification helpers.

Downloads installer artifacts and verifies SHA256 checksums.
"""

import hashlib
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from .config import DOWNLOAD_TIMEOUT, MAX_DOWNLOAD_WORKERS

log = logging.getLogger(__name__)


def download_file(url: str, dest: Path, expected_sha256: str) -> Path:
    """
    Download a file and verify its SHA256 checksum.

    Args:
        url: Download URL.
        dest: Destination file path.
        expected_sha256: Expected SHA256 checksum.

    Returns:
        The downloaded file path.

    Raises:
        RuntimeError: If the download fails or the checksum does not match.
    """
    log.info(f"Downloading: [{url}]")

    try:
        resp = requests.get(url, timeout=DOWNLOAD_TIMEOUT, stream=True)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Download failed [{url}]: {e}")

    # Stream to disk while computing SHA256 to avoid high memory usage.
    sha256 = hashlib.sha256()
    dest.parent.mkdir(parents=True, exist_ok=True)

    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            sha256.update(chunk)

    actual_sha256 = sha256.hexdigest()
    if actual_sha256.lower() != expected_sha256.lower():
        dest.unlink(missing_ok=True)
        raise RuntimeError(
            f"SHA256 verification failed [{dest.name}]: "
            f"expected [{expected_sha256}], got [{actual_sha256}]"
        )

    file_size = dest.stat().st_size
    log.info(f"Download complete: [{dest.name}], size [{file_size / 1024 / 1024:.1f}MB]")
    return dest


def download_version_files(
    gcs_bucket: str,
    version: str,
    manifest: dict,
    dest_dir: Path
) -> list[Path]:
    """
    Download all platform artifacts for a version in parallel.

    Args:
        gcs_bucket: GCS_BUCKET base URL.
        version: Target version.
        manifest: Parsed `manifest.json` content.
        dest_dir: Destination directory.

    Returns:
        List of downloaded file paths.

    Raises:
        RuntimeError: If any platform download fails.
    """
    platforms = manifest.get("platforms", {})
    if not platforms:
        raise RuntimeError(f"Manifest for version [{version}] contains no platform info")

    log.info(f"Downloading version [{version}] artifacts for [{len(platforms)}] platforms...")

    files = []
    errors = []

    with ThreadPoolExecutor(max_workers=MAX_DOWNLOAD_WORKERS) as executor:
        futures = {}

        for platform, info in platforms.items():
            # Windows artifacts end with `.exe`; other platforms have no extension.
            is_win = platform.startswith("win")
            url = f"{gcs_bucket}/{version}/{platform}/claude"
            if is_win:
                url += ".exe"

            filename = f"claude-{version}-{platform}"
            if is_win:
                filename += ".exe"
            dest = Path(dest_dir) / filename

            checksum = info.get("checksum", "")
            if not checksum:
                log.warning(f"Platform [{platform}] has no checksum; skipping")
                continue

            future = executor.submit(download_file, url, dest, checksum)
            futures[future] = platform

        for future in as_completed(futures):
            platform = futures[future]
            try:
                file_path = future.result()
                files.append(file_path)
            except Exception as e:
                log.error(f"Platform [{platform}] download failed: {e}")
                errors.append(f"{platform}: {e}")

    if errors:
        raise RuntimeError(
            f"Some platform downloads failed for version [{version}]:\n" + "\n".join(errors)
        )

    log.info(f"All platform downloads complete for version [{version}]; total files [{len(files)}]")
    return files
