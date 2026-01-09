"""
Configuration constants.
"""

INSTALL_SCRIPT_URL = "https://claude.ai/install.sh"
CHANGELOG_URL = "https://raw.githubusercontent.com/anthropics/claude-code/refs/heads/main/CHANGELOG.md"

MIN_VERSION = "1.0.37"  # Lowest supported version (older versions have no manifest).
MAX_PER_RUN = 5  # Max versions per run (prevents workflow timeouts).

VERSION_FILE = "version.json"

REQUEST_TIMEOUT = 30
DOWNLOAD_TIMEOUT = 300  # Large file download timeout (seconds).

MAX_DOWNLOAD_WORKERS = 7
