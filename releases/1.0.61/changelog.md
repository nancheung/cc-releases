# Release 1.0.61

- Transcript mode (Ctrl+R): Changed Esc to exit transcript mode rather than interrupt
- Settings: Added `--settings` flag to load settings from a JSON file
- Settings: Fixed resolution of settings files paths that are symlinks
- OTEL: Fixed reporting of wrong organization after authentication changes
- Slash commands: Fixed permissions checking for allowed-tools with Bash
- IDE: Added support for pasting images in VSCode MacOS using ⌘+V
- IDE: Added `CLAUDE_CODE_AUTO_CONNECT_IDE=false` for disabling IDE auto-connection
- Added `CLAUDE_CODE_SHELL_PREFIX` for wrapping Claude and user-provided shell commands run by Claude Code