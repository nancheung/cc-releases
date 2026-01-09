# Release 1.0.53

- Updated @-mention file truncation from 100 lines to 2000 lines
- Add helper script settings for AWS token refresh: awsAuthRefresh (for foreground operations like aws sso login) and awsCredentialExport (for background operation with STS-like response).