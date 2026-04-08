# Release 2.1.96

- Fixed Bedrock requests failing with `403 "Authorization header is missing"` when using `AWS_BEARER_TOKEN_BEDROCK` or `CLAUDE_CODE_SKIP_BEDROCK_AUTH` (regression in 2.1.94)