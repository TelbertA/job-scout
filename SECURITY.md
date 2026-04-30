# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Job Scout, please report it responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, email: telbertanthony@gmail.com

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes

You will receive a response within 72 hours. If the vulnerability is confirmed, a fix will be prioritized and you will be credited in the release notes.

---

## Security Design

Job Scout is built with Zero Trust Architecture principles:

- **No stored AWS credentials** — GitHub Actions authenticates via OIDC federation
- **Secrets in SSM Parameter Store** — KMS-encrypted SecureString, never in code or environment variables
- **Least-privilege IAM** — every policy scoped to specific resource ARNs
- **Encrypted at rest** — DynamoDB SSE, S3 SSE-S3, ECR AES256
- **Encrypted in transit** — S3 bucket policy denies all non-HTTPS requests
- **Continuous scanning** — six CI security gates on every PR, ECR scan-on-push

---

## Supported Versions

| Version | Supported |
|---|---|
| Latest (main) | Yes |
