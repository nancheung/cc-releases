# Release 2.1.294

- Fixed `prompt` and `agent` hooks written as instructions (such as "Block commands that...") allowing what they should block
- Improved how `prompt` hooks on Stop and SubagentStop written as instructions (such as "Carry on if the build is broken") are judged, so Claude is less likely to stop early