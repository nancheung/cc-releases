# Release 2.0.34

- VSCode Extension: Added setting to configure the initial permission mode for new conversations
- Improved file path suggestion performance with native Rust-based fuzzy finder
- Fixed infinite token refresh loop that caused MCP servers with OAuth (e.g., Slack) to hang during connection
- Fixed memory crash when reading or writing large files (especially base64-encoded images)