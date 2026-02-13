# Release 2.1.41

- Fixed AWS auth refresh hanging indefinitely by adding a 3-minute timeout
- Added `claude auth login`, `claude auth status`, and `claude auth logout` CLI subcommands
- Added Windows ARM64 (win32-arm64) native binary support
- Improved `/rename` to auto-generate session name from conversation context when called without arguments
- Improved narrow terminal layout for prompt footer
- Fixed file resolution failing for @-mentions with anchor fragments (e.g., `@README.md#installation`)
- Fixed FileReadTool blocking the process on FIFOs, `/dev/stdin`, and large files
- Fixed background task notifications not being delivered in streaming Agent SDK mode
- Fixed cursor jumping to end on each keystroke in classifier rule input
- Fixed markdown link display text being dropped for raw URL
- Fixed auto-compact failure error notifications being shown to users
- Fixed permission wait time being included in subagent elapsed time display
- Fixed proactive ticks firing while in plan mode
- Fixed clear stale permission rules when settings change on disk
- Fixed hook blocking errors showing stderr content in UI