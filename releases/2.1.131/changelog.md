# Release 2.1.131

- Fixed VS Code extension failing to activate on Windows due to a hardcoded build path in the bundled SDK (`createRequire` polyfill bug)
- Fixed Mantle endpoint authentication failing with missing `x-api-key` header