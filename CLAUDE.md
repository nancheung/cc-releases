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
- **fetcher.py**: Retrieves GCS_BUCKET URL and manifest.json from official sources
- **changelog.py**: Parses CHANGELOG.md for versions and extracts release notes
- **downloader.py**: Concurrent downloads with SHA256 verification
- **version.py**: Manages version.json index (load/save/compare using `packaging.version`)
- **release.py**: GitHub Release operations via `gh` CLI (create, exists check)

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

### Platform Mapping

Windows binaries have `.exe` extension, all others have no extension:
- `{gcs_bucket}/{version}/win32-x64/claude.exe` → `claude-{version}-win32-x64.exe`
- `{gcs_bucket}/{version}/darwin-arm64/claude` → `claude-{version}-darwin-arm64`

### version.json Schema

```json
{
  "synced": ["2.1.0", "1.0.38", "1.0.37", "..."], 
  "lastRun": "2026-01-09T10:30:00Z",
  "latestSynced": "2.1.0"
}
```

## Known Limitations

- **Git Push per Version**: Currently commits/pushes after each version, creating multiple commits. Consider batching all versions into a single commit.
- **No Retry Logic**: Network requests fail permanently on first error. Consider implementing exponential backoff.
- **Fixed Thread Pool**: MAX_DOWNLOAD_WORKERS=7 even when fewer platforms exist.
- **CHANGELOG Regex**: Pattern assumes standard formatting `## X.Y.Z`. May break with spacing variations.
- **Git Push Failures**: Logged as warnings only, causing version.json desync between local and remote.

## Manual Operations

Manually trigger sync for specific versions via GitHub Actions UI:
```
Workflow: Sync Releases
Input: ["2.1.0","2.1.1","2.1.2"]
```

Manually trigger update check:
```
Workflow: Check for Updates
(no input required)
```
