# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an automated GitHub Release mirror for Claude Code offline installers. The system periodically checks the official Claude Code repository for new versions and automatically downloads, verifies, and publishes installation packages for all supported platforms.

**Data Sources:**
- Official repository: https://github.com/anthropics/claude-code
- Install script: https://claude.ai/install.sh (provides GCS_BUCKET URL)
- Changelog: https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md

## Development Commands

### Setup
```bash
pip install -r requirements.txt
```

### Local Testing
```bash
# Test update detection
python scripts/check_update.py

# Test syncing specific versions
python scripts/sync_release.py '["2.1.0","2.1.1"]'
```

### GitHub CLI Required
The sync script uses `gh` CLI for Release operations:
```bash
gh release view v2.1.0
gh release create v2.1.0 --title "2.1.0" --notes "..." file1 file2 ...
```

### Dependencies
- Python 3.8+ (workflows use 3.11)
- `requests>=2.28.0` - HTTP client for fetching manifests and binaries
- `packaging>=23.0` - Version comparison and ordering
- `gh` CLI - GitHub Release operations (must be authenticated)

## Architecture

### Workflow Pipeline

The system uses two GitHub Actions workflows that work together:

1. **check-update.yml** (runs every 6 hours)
   - Parses official CHANGELOG.md for version numbers
   - Compares with `version.json` to find unsynced versions
   - Filters versions >= MIN_VERSION (1.0.37)
   - Batches up to MAX_PER_RUN (5) versions
   - Triggers sync-release.yml if updates found

2. **sync-release.yml** (called by check-update or manual trigger)
   - Processes versions serially to avoid conflicts
   - For each version:
     - Fetches manifest.json from GCS
     - Downloads all platform binaries concurrently (7 workers)
     - Verifies SHA256 checksums
     - Creates GitHub Release with changelog notes
     - Updates version.json and commits

### Module Architecture

**Core Modules (scripts/lib/):**

- **config.py**: Constants (MIN_VERSION, timeouts, worker counts)
- **fetcher.py**: Retrieves GCS_BUCKET URL and manifest.json from official sources (supports fallback mode)
- **changelog.py**: Parses CHANGELOG.md for versions and extracts release notes
- **downloader.py**: Concurrent downloads with SHA256 verification (skips downloads in fallback mode)
- **version.py**: Manages version.json index (load/save/compare using `packaging.version`)
- **release.py**: GitHub Release operations via `gh` CLI (create, exists check)
- **metadata.py**: Saves version metadata (changelog.md and manifest.json) to releases/{version}/ directory

**Entry Points:**

- **check_update.py**: Outputs `has_updates` and `versions` to GITHUB_OUTPUT
- **sync_release.py**: Accepts JSON version array, syncs each serially

### Critical Design Decisions

**Idempotency**: `release_exists()` checks prevent duplicate releases if workflow reruns

**Version Ordering**: Processes oldest-to-newest to maintain correct `latestSynced` in version.json

**Batch Limiting**: MAX_PER_RUN=5 prevents GitHub Actions timeout (6 hour limit)

**Concurrent Downloads**: ThreadPoolExecutor with MAX_DOWNLOAD_WORKERS=7 for platform binaries

**SHA256 Streaming**: Calculates hash while downloading to save memory

**Serial Version Processing**: Each version commits version.json separately to avoid Git conflicts (NOTE: This creates multiple commits per run)

**Fallback Mode**: When manifest.json is unavailable, system creates Release without binaries instead of failing

### Platform Mapping

7 platforms supported, binary naming conventions:

**Windows (1 platform):**
- `{gcs_bucket}/{version}/win32-x64/claude.exe` → `claude-{version}-win32-x64.exe`

**macOS (2 platforms):**
- `darwin-arm64` → Apple Silicon (M1/M2/M3)
- `darwin-x64` → Intel

**Linux glibc (2 platforms):**
- `linux-x64` → Standard x64
- `linux-arm64` → ARM64/aarch64

**Linux musl (2 platforms):**
- `linux-x64-musl` → Alpine Linux x64
- `linux-arm64-musl` → Alpine Linux ARM64

Windows binaries have `.exe` extension, all others have no extension.

### version.json Schema

```json
{
  "synced": ["2.1.0", "1.0.38", "1.0.37", "..."],
  "lastRun": "2026-01-09T10:30:00Z",
  "latestSynced": "2.1.0"
}
```

### Metadata Directory Structure

Each synced version creates a `releases/{version}/` directory:

```
releases/
  2.1.0/
    changelog.md    - Release notes extracted from CHANGELOG.md
    manifest.json   - Complete manifest.json from GCS (or fallback structure)
  1.0.38/
    ...
```

These files are committed to Git and provide offline access to version metadata.

## Fallback Mode

When `manifest.json` download fails (HTTP errors, timeouts, JSON parse errors), the system enters **fallback mode** instead of failing completely:

**Behavior:**
- Skips binary downloads (no installer files)
- Creates Release with changelog but no attachments
- Marks version as synced in `version.json`
- Saves metadata with `_fallback_mode: true` flag in manifest.json
- Adds warning to `releases/{version}/changelog.md` and GitHub Release notes

**Detection:**
```python
manifest = get_manifest(gcs_bucket, version)
if manifest.get("_fallback_mode", False):
    # This version entered fallback mode
```

**Manual Recovery:**
If manifest becomes available later, you can re-sync:
```bash
# Delete fallback release
gh release delete vX.Y.Z --yes --cleanup-tag

# Remove version from version.json manually
# Edit version.json, remove "X.Y.Z" from "synced" array

# Re-sync
python scripts/sync_release.py '["X.Y.Z"]'
```

## Known Limitations

- **Git Push per Version**: Currently commits/pushes after each version, creating multiple commits. Consider batching all versions into a single commit.
- **Fixed Thread Pool**: MAX_DOWNLOAD_WORKERS=7 even when fewer platforms exist.
- **CHANGELOG Regex**: Pattern assumes standard formatting `## X.Y.Z`. May break with spacing variations.
- **Git Push Failures**: Logged as warnings only, causing version.json desync between local and remote.
- **Minimum Version**: Only versions >= 1.0.37 are supported (earlier versions lack manifest.json in GCS).
- **No Tests**: The project currently has no unit tests or integration tests. Consider adding tests when modifying core logic.

## Manual Operations

### Trigger Workflows via GitHub UI

**Sync specific versions:**
1. Navigate to Actions → Sync Releases
2. Click "Run workflow"
3. Input JSON array: `["2.1.0","2.1.1","2.1.2"]`

**Check for updates:**
1. Navigate to Actions → Check for Updates
2. Click "Run workflow" (no input required)

### Local Development Workflow

When adding new features or debugging:

1. **Test update detection locally:**
   ```bash
   python scripts/check_update.py
   # Check GITHUB_OUTPUT file or stdout for results
   ```

2. **Test sync process (dry run):**
   ```bash
   # Temporarily comment out git push and gh release create in sync_release.py
   python scripts/sync_release.py '["1.0.37"]'
   ```

3. **Authenticate gh CLI before testing releases:**
   ```bash
   gh auth login
   gh auth status
   ```

4. **Verify version.json changes:**
   ```bash
   git diff version.json
   # Should show new version in "synced" array and updated "latestSynced"
   ```
