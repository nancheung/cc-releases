# Release 1.0.84

- Fix tool_use/tool_result id mismatch error when network is unstable
- Fix Claude sometimes ignoring real-time steering when wrapping up a task
- @-mention: Add ~/.claude/\* files to suggestions for easier agent, output style, and slash command editing
- Use built-in ripgrep by default; to opt out of this behavior, set USE_BUILTIN_RIPGREP=0