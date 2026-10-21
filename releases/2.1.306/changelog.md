# Release 2.1.306

- Fixed `claude -p` inside cloud sessions reporting "Not logged in" when started without the session's environment variables
- Fixed an API error being replaced by "prompt is too long", and an unneeded compaction, in sessions with many MCP tools