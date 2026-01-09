# Claude Code Releases - Offline Installer Archive

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://github.com/nancheung/cc-releases/blob/main/LICENSE)
[![CC release](https://img.shields.io/github/v/release/anthropics/claude-code?label=CC%20release)](https://github.com/anthropics/claude-code/releases)
[![CCR release](https://img.shields.io/github/v/release/nancheung/cc-releases?label=CCR%20release)](https://github.com/nancheung/cc-releases/releases)
[![Sync Status](https://img.shields.io/github/actions/workflow/status/nancheung/cc-releases/check-update.yml?branch=main&label=sync)](https://github.com/nancheung/cc-releases/actions)

Automated mirror of [Claude Code](https://github.com/anthropics/claude-code) offline installers for all supported platforms. This repository automatically detects new releases, downloads official binaries, verifies integrity, and publishes them as GitHub Releases for easy access.

## ✨ Features

- 🤖 **Fully Automated** - GitHub Actions checks for updates every 6 hours
- 🌍 **Cross-Platform** - Supports Windows, macOS (Intel & Apple Silicon), and Linux (x64, ARM64, musl)
- 🔒 **Integrity Verified** - SHA256 checksums validated for all downloads
- 📦 **Version Archive** - Access any version >= 1.0.37 from a single location
- 🚀 **Fast Downloads** - Concurrent downloads from official Google Cloud Storage
- 📝 **Changelog Included** - Each release includes official release notes

## 📥 Quick Start

### Download Latest Version

**[→ Go to Releases Page](../../releases/latest)** to download installers for your platform.

### Platform Support

| Platform | Architecture | File Pattern | Installation |
|----------|-------------|--------------|--------------|
| 🪟 **Windows** | x64 | `claude-{version}-win32-x64.exe` | Run executable |
| 🍎 **macOS** | Apple Silicon (M1/M2/M3) | `claude-{version}-darwin-arm64` | Refer to [official docs](https://github.com/anthropics/claude-code) |
| 🍎 **macOS** | Intel x64 | `claude-{version}-darwin-x64` | Refer to [official docs](https://github.com/anthropics/claude-code) |
| 🐧 **Linux** | x64 (glibc) | `claude-{version}-linux-x64` | Refer to [official docs](https://github.com/anthropics/claude-code) |
| 🐧 **Linux** | ARM64 (glibc) | `claude-{version}-linux-arm64` | Refer to [official docs](https://github.com/anthropics/claude-code) |
| 🐧 **Linux** | x64 (musl) | `claude-{version}-linux-x64-musl` | Refer to [official docs](https://github.com/anthropics/claude-code) |
| 🐧 **Linux** | ARM64 (musl) | `claude-{version}-linux-arm64-musl` | Refer to [official docs](https://github.com/anthropics/claude-code) |

> **Note:** musl builds are for Alpine Linux and other musl-based distributions

### Browse All Versions

Visit **[Releases](../../releases)** to download specific versions or explore the full version history.

## 🔄 How It Works

This repository uses a two-stage GitHub Actions pipeline:

### 1. Update Detection (Every 6 Hours)

The [`check-update.yml`](.github/workflows/check-update.yml) workflow:
- Parses the [official CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) for version numbers
- Compares discovered versions against `version.json` (our local index)
- Filters versions >= 1.0.37 (minimum supported version)
- Batches up to 5 versions per run to respect API rate limits
- Triggers the sync workflow if new versions are found

### 2. Release Synchronization (On-Demand)

The [`sync-release.yml`](.github/workflows/sync-release.yml) workflow:
1. Fetches `manifest.json` from official Google Cloud Storage bucket
2. Downloads all platform binaries concurrently (7 parallel workers)
3. Verifies each download against SHA256 checksums from manifest
4. Creates GitHub Release with changelog notes and verified binaries
5. Updates `version.json` index and commits changes

### Data Sources

- **Official Repository:** [anthropics/claude-code](https://github.com/anthropics/claude-code)
- **Install Script:** [claude.ai/install.sh](https://claude.ai/install.sh) (provides GCS bucket URL)
- **Changelog:** [CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)

## 🛠️ Manual Operations

You can manually trigger synchronization via GitHub Actions:

### Trigger Update Check

1. Go to **[Actions → Check for Updates](../../actions/workflows/check-update.yml)**
2. Click **Run workflow** → **Run workflow**

### Sync Specific Versions

1. Go to **[Actions → Sync Releases](../../actions/workflows/sync-release.yml)**
2. Click **Run workflow**
3. Enter JSON array of versions (e.g., `["2.1.0","2.1.1"]`)
4. Click **Run workflow**

## 📚 Technical Details

<details>
<summary><strong>Project Structure</strong></summary>

```
cc-releases/
├── .github/workflows/
│   ├── check-update.yml    # Scheduled update detection
│   └── sync-release.yml    # Release synchronization
├── scripts/
│   ├── check_update.py     # Update detection entry point
│   ├── sync_release.py     # Sync entry point
│   └── lib/                # Core modules
│       ├── config.py       # Constants and settings
│       ├── fetcher.py      # GCS bucket and manifest fetching
│       ├── changelog.py    # CHANGELOG.md parsing
│       ├── downloader.py   # Concurrent downloads with verification
│       ├── version.py      # version.json management
│       └── release.py      # GitHub Release operations
├── version.json            # Synced versions index
└── README.md
```

</details>

<details>
<summary><strong>Version Index Schema</strong></summary>

`version.json` tracks synchronized releases:

```json
{
  "synced": ["2.1.0", "1.0.38", "1.0.37"],
  "lastRun": "2026-01-09T10:30:00Z",
  "latestSynced": "2.1.0"
}
```

**Fields:**
- `synced`: Array of synchronized versions, sorted newest → oldest
- `lastRun`: ISO 8601 UTC timestamp of last synchronization
- `latestSynced`: Latest synchronized version (first element of `synced` array)

</details>

<details>
<summary><strong>Development Setup</strong></summary>

**Prerequisites:** Python 3.8+, [GitHub CLI](https://cli.github.com/)

```bash
# Install dependencies
pip install -r requirements.txt

# Test update detection
python scripts/check_update.py

# Test syncing specific versions
python scripts/sync_release.py '["2.1.0","2.1.1"]'
```

</details>

## ❓ FAQ

<details>
<summary><strong>Why are versions older than 1.0.37 not available?</strong></summary>

Earlier versions do not have `manifest.json` files in the official Google Cloud Storage bucket, making automated integrity verification impossible.

</details>

<details>
<summary><strong>How often are new versions synced?</strong></summary>

The update checker runs every 6 hours. Manual synchronization is also available via GitHub Actions.

</details>

<details>
<summary><strong>Are these official binaries?</strong></summary>

Yes. All binaries are downloaded directly from Anthropic's official Google Cloud Storage bucket and verified using SHA256 checksums from official manifests.

</details>

<details>
<summary><strong>Can I download older versions?</strong></summary>

Yes. All versions >= 1.0.37 are archived in the [Releases](../../releases) section.

</details>

## 🔗 Related Links

- [Claude Code Official Repository](https://github.com/anthropics/claude-code)
- [Claude Code Documentation](https://github.com/anthropics/claude-code#readme)
- [Official Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
- [Report Issues](https://github.com/anthropics/claude-code/issues)

## 📄 License

This repository is licensed under the [AGPL v3 License](LICENSE).

**Note:** Claude Code itself is distributed under its own license terms. Please refer to the [official repository](https://github.com/anthropics/claude-code) for Claude Code licensing information.

---

<p align="center">
  <sub>Maintained by automated workflows • Not affiliated with Anthropic</sub>
</p>
