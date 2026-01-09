# Release 2.0.55

- Fixed proxy DNS resolution being forced on by default. Now opt-in via `CLAUDE_CODE_PROXY_RESOLVES_HOSTS=true` environment variable
- Fixed keyboard navigation becoming unresponsive when holding down arrow keys in memory location selector
- Improved AskUserQuestion tool to auto-submit single-select questions on the last question, eliminating the extra review screen for simple question flows
- Improved fuzzy matching for `@` file suggestions with faster, more accurate results