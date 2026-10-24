# Claude Code 离线安装包存档

**[English](README.md) | [中文](README.zh-CN.md)**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://github.com/nancheung/cc-releases/blob/main/LICENSE)
[![CC release](https://img.shields.io/github/v/release/anthropics/claude-code?label=CC%20release)](https://github.com/anthropics/claude-code/releases)
[![CCR release](https://img.shields.io/github/v/release/nancheung/cc-releases?label=CCR%20release)](https://github.com/nancheung/cc-releases/releases)
[![Sync Status](https://img.shields.io/github/actions/workflow/status/nancheung/cc-releases/check-update.yml?branch=main&label=sync)](https://github.com/nancheung/cc-releases/actions)

[Claude Code](https://github.com/anthropics/claude-code) 离线安装包的自动化镜像，支持所有平台。本仓库会自动检测新版本发布，下载官方二进制文件，验证完整性，并将其发布为 GitHub Release，方便访问。

## ✨ 特性

- 🤖 **全自动化** - GitHub Actions 每 6 小时检查一次更新
- 🌍 **跨平台支持** - 支持 Windows、macOS（Intel 和 Apple Silicon）、Linux（x64、ARM64、musl）
- 🔒 **完整性验证** - 所有下载都经过 SHA256 校验和验证
- 📦 **版本存档** - 从单一位置访问任何 >= 1.0.37 的版本
- 🚀 **快速下载** - 从官方 Google Cloud Storage 并发下载
- 📝 **包含更新日志** - 每个发布版本都包含官方发布说明

## 📥 快速开始

### 下载最新版本

**[→ 前往 Releases 页面](../../releases/latest)** 下载适合你平台的安装包。

### 平台支持

| 平台 | 架构 | 文件格式 | 安装方式 |
|----------|-------------|--------------|--------------|
| 🪟 **Windows** | x64 | `claude-{version}-win32-x64.exe` | `.\claude-{version}-win32-x64.exe install` |
| 🍎 **macOS** | Apple Silicon (M1/M2/M3) | `claude-{version}-darwin-arm64` | `chmod +x claude-{version}-darwin-arm64 && ./claude-{version}-darwin-arm64 install` |
| 🍎 **macOS** | Intel x64 | `claude-{version}-darwin-x64` | `chmod +x claude-{version}-darwin-x64 && ./claude-{version}-darwin-x64 install` |
| 🐧 **Linux** | x64 (glibc) | `claude-{version}-linux-x64` | [见 Linux 离线安装](#linux-离线安装) |
| 🐧 **Linux** | ARM64 (glibc) | `claude-{version}-linux-arm64` | [见 Linux 离线安装](#linux-离线安装) |
| 🐧 **Linux** | x64 (musl) | `claude-{version}-linux-x64-musl` | [见 Linux 离线安装](#linux-离线安装) |
| 🐧 **Linux** | ARM64 (musl) | `claude-{version}-linux-arm64-musl` | [见 Linux 离线安装](#linux-离线安装) |

> **注意：** musl 构建版本适用于 Alpine Linux 和其他基于 musl 的发行版

> **安装说明：**
> - **Windows**：使用 `install` 命令运行下载的 `.exe` 文件
> - **macOS**：运行前使用 `chmod +x` 授予执行权限
> - **Linux**：请按下方 [Linux 离线安装](#linux-离线安装) 的步骤操作，直接运行 `install` 在离线环境下会失败
> - 将 `{version}` 替换为实际版本号（例如 `1.0.112`）
> - `install` 命令会设置 shell 集成和 `claude` CLI 启动器

### Linux 离线安装

直接运行 `./claude-{version}-linux-x64 install` 需要联网，离线时会失败。正确做法是先把二进制放进版本目录，再用**明确的版本号**激活：

```bash
mkdir -p ~/.local/share/claude/versions
install -m 755 claude-2.1.310-linux-x64 ~/.local/share/claude/versions/2.1.310
~/.local/share/claude/versions/2.1.310 install 2.1.310
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
claude --version                         # 2.1.310 (Claude Code)
```

- 将 `2.1.310` 和 `linux-x64` 替换为实际版本号和平台（`linux-arm64`、`linux-x64-musl`、`linux-arm64-musl`）
- `install` 后面的版本号**必须**和 `versions/` 下的文件名一致
- 如果使用 zsh，把 `~/.bashrc` 换成 `~/.zshrc`

**原因** —— `install` 子命令内部：

- `install` 不带参数时，target 默认为 `latest`，先联网解析出版本号（离线时在这里就失败：`Failed to fetch version from .../latest`）
- 核心函数会检查 `~/.local/share/claude/versions/<版本>` 是否存在：
  - **不存在** → `Downloading native installer version <版本>`，从 downloads.claude.ai 重新下载到 staging 目录，校验后移入版本目录。它**不会**复用正在运行的自身文件
  - **已存在** → 联网拉 manifest 复验这份文件；如果网络不可达、**而且**用户明确指定了版本号，就走 `offline, activating as requested` 分支，直接激活
- 激活：创建 `~/.local/bin/claude` → `versions/<版本>` 软链，并写入 `installMethod: native`

> **排障：** 下载前会先对目标路径加锁，所以离线失败时会在 `versions/` 下留下一个 **0 字节文件**。可用 `ls -l ~/.local/share/claude/versions/` 检查，删掉 0 字节文件后再按上面的步骤安装。

### 浏览所有版本

访问 **[Releases](../../releases)** 下载特定版本或浏览完整版本历史。

## 🔄 工作原理

本仓库使用两阶段 GitHub Actions 流水线：

### 1. 更新检测（每 6 小时运行一次）

[`check-update.yml`](.github/workflows/check-update.yml) 工作流：
- 解析 [官方 CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) 获取版本号
- 将发现的版本与 `version.json`（本地索引）对比
- 过滤出 >= 1.0.37 的版本（支持的最低版本）
- 每次运行最多批处理 5 个版本以遵守 API 速率限制
- 如果发现新版本，则触发同步工作流

### 2. Release 同步（按需触发）

[`sync-release.yml`](.github/workflows/sync-release.yml) 工作流：
1. 从官方 Google Cloud Storage 存储桶获取 `manifest.json`
2. 并发下载所有平台的二进制文件（7 个并行工作线程）
3. 根据 manifest 中的 SHA256 校验和验证每个下载
4. 创建 GitHub Release，包含更新日志说明和已验证的二进制文件
5. 更新 `version.json` 索引并提交更改

### 数据源

- **官方仓库：** [anthropics/claude-code](https://github.com/anthropics/claude-code)
- **安装脚本：** [claude.ai/install.sh](https://claude.ai/install.sh)（提供 GCS 存储桶 URL）
- **更新日志：** [CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)

## 🛠️ 手动操作

你可以通过 GitHub Actions 手动触发同步：

### 触发更新检查

1. 前往 **[Actions → Check for Updates](../../actions/workflows/check-update.yml)**
2. 点击 **Run workflow** → **Run workflow**

### 同步特定版本

1. 前往 **[Actions → Sync Releases](../../actions/workflows/sync-release.yml)**
2. 点击 **Run workflow**
3. 输入版本的 JSON 数组（例如 `["2.1.0","2.1.1"]`）
4. 点击 **Run workflow**

## 📚 技术细节

<details>
<summary><strong>项目结构</strong></summary>

```
cc-releases/
├── .github/workflows/
│   ├── check-update.yml    # 定时更新检测
│   └── sync-release.yml    # Release 同步
├── scripts/
│   ├── check_update.py     # 更新检测入口点
│   ├── sync_release.py     # 同步入口点
│   └── lib/                # 核心模块
│       ├── config.py       # 常量和配置
│       ├── fetcher.py      # GCS 存储桶和 manifest 获取
│       ├── changelog.py    # CHANGELOG.md 解析
│       ├── downloader.py   # 并发下载和验证
│       ├── version.py      # version.json 管理
│       └── release.py      # GitHub Release 操作
├── version.json            # 已同步版本索引
└── README.md
```

</details>

<details>
<summary><strong>版本索引结构</strong></summary>

`version.json` 跟踪已同步的发布版本：

```json
{
  "synced": ["2.1.0", "1.0.38", "1.0.37"],
  "lastRun": "2026-01-09T10:30:00Z",
  "latestSynced": "2.1.0"
}
```

**字段说明：**
- `synced`：已同步版本数组，按从新到旧排序
- `lastRun`：上次同步的 ISO 8601 UTC 时间戳
- `latestSynced`：最新已同步版本（`synced` 数组的第一个元素）

</details>

<details>
<summary><strong>开发环境配置</strong></summary>

**前置要求：** Python 3.8+，[GitHub CLI](https://cli.github.com/)

```bash
# 安装依赖
pip install -r requirements.txt

# 测试更新检测
python scripts/check_update.py

# 测试同步特定版本
python scripts/sync_release.py '["2.1.0","2.1.1"]'
```

</details>

## ❓ 常见问题

<details>
<summary><strong>为什么没有 1.0.37 之前的版本？</strong></summary>

早期版本在官方 Google Cloud Storage 存储桶中没有 `manifest.json` 文件，无法进行自动完整性验证。

</details>

<details>
<summary><strong>新版本多久同步一次？</strong></summary>

更新检查器每 6 小时运行一次。也可以通过 GitHub Actions 手动触发同步。

</details>

<details>
<summary><strong>这些是官方二进制文件吗？</strong></summary>

是的。所有二进制文件都直接从 Anthropic 的官方 Google Cloud Storage 存储桶下载，并使用官方 manifest 中的 SHA256 校验和进行验证。

</details>

<details>
<summary><strong>可以下载旧版本吗？</strong></summary>

可以。所有 >= 1.0.37 的版本都存档在 [Releases](../../releases) 部分。

</details>

## 🔗 相关链接

- [Claude Code 官方仓库](https://github.com/anthropics/claude-code)
- [Claude Code 文档](https://github.com/anthropics/claude-code#readme)
- [官方更新日志](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
- [问题反馈](https://github.com/anthropics/claude-code/issues)

## 📄 许可证

本仓库采用 [AGPL v3 许可证](LICENSE)。

**注意：** Claude Code 本身采用其自己的许可条款。有关 Claude Code 的许可信息，请参考 [官方仓库](https://github.com/anthropics/claude-code)。

---

<p align="center">
  <sub>由自动化工作流维护 • 非 Anthropic 官方项目</sub>
</p>
