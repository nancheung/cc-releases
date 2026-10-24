# Claude Code Releases - Offline Installer Archive

**[English](README.md) | [中文](README.zh-CN.md)**

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
| 🪟 **Windows** | x64 | `claude-{version}-win32-x64.exe` | `.\claude-{version}-win32-x64.exe install` |
| 🍎 **macOS** | Apple Silicon (M1/M2/M3) | `claude-{version}-darwin-arm64` | `chmod +x claude-{version}-darwin-arm64 && ./claude-{version}-darwin-arm64 install` |
| 🍎 **macOS** | Intel x64 | `claude-{version}-darwin-x64` | `chmod +x claude-{version}-darwin-x64 && ./claude-{version}-darwin-x64 install` |
| 🐧 **Linux** | x64 (glibc) | `claude-{version}-linux-x64` | [See Linux Offline Install](#linux-offline-install) |
| 🐧 **Linux** | ARM64 (glibc) | `claude-{version}-linux-arm64` | [See Linux Offline Install](#linux-offline-install) |
| 🐧 **Linux** | x64 (musl) | `claude-{version}-linux-x64-musl` | [See Linux Offline Install](#linux-offline-install) |
| 🐧 **Linux** | ARM64 (musl) | `claude-{version}-linux-arm64-musl` | [See Linux Offline Install](#linux-offline-install) |

> **Note:** musl builds are for Alpine Linux and other musl-based distributions

> **Installation Notes:**
> - **Windows**: Run the downloaded `.exe` file with the `install` command
> - **macOS**: Grant execution permission with `chmod +x` before running
> - **Linux**: Follow [Linux Offline Install](#linux-offline-install) below — running `install` directly fails without network access
> - Replace `{version}` with the actual version number (e.g., `1.0.112`)
> - The `install` command sets up shell integration and the `claude` CLI launcher

### Linux Offline Install

Running `./claude-{version}-linux-x64 install` directly needs network access and fails offline. Place the binary into the versions directory first, then activate it with an **explicit version number**:

```bash
mkdir -p ~/.local/share/claude/versions
install -m 755 claude-2.1.310-linux-x64 ~/.local/share/claude/versions/2.1.310
~/.local/share/claude/versions/2.1.310 install 2.1.310
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
claude --version                         # 2.1.310 (Claude Code)
```

- Replace `2.1.310` and `linux-x64` with your actual version and platform (`linux-arm64`, `linux-x64-musl`, `linux-arm64-musl`)
- The version passed to `install` **must** match the file name under `versions/`
- If you use zsh, replace `~/.bashrc` with `~/.zshrc`

**Why it works this way** — inside the `install` subcommand:

- Without an argument, the target defaults to `latest`, which is resolved to a version number online first. Offline, it fails right here: `Failed to fetch version from .../latest`
- It then checks whether `~/.local/share/claude/versions/<version>` exists:
  - **Missing** → `Downloading native installer version <version>`: it re-downloads from downloads.claude.ai into a staging directory, verifies it, and moves it into the versions directory. It does **not** reuse the running binary itself
  - **Present** → it fetches the manifest online to re-verify the file. If the network is unreachable **and** a version was explicitly specified, it takes the `offline, activating as requested` branch and activates directly
- Activation: creates the symlink `~/.local/bin/claude` → `versions/<version>` and writes `installMethod: native`

> **Troubleshooting:** The installer locks the target path before downloading, so a failed offline attempt leaves a **0-byte file** under `versions/`. Check with `ls -l ~/.local/share/claude/versions/`, delete any 0-byte entry, then follow the steps above.

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
