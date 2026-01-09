# Release 2.0.62

- Added "(Recommended)" indicator for multiple-choice questions, with the recommended option moved to the top of the list
- Added `attribution` setting to customize commit and PR bylines (deprecates `includeCoAuthoredBy`)
- Fixed duplicate slash commands appearing when ~/.claude is symlinked to a project directory
- Fixed slash command selection not working when multiple commands share the same name
- Fixed an issue where skill files inside symlinked skill directories could become circular symlinks
- Fixed running versions getting removed because lock file incorrectly going stale
- Fixed IDE diff tab not closing when rejecting file changes