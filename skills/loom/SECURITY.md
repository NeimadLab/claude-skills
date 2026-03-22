# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Loom, please report it responsibly.

**Do NOT open a public issue.**

Email: security@neimadlab.com (or use GitHub's private vulnerability reporting)

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide a timeline for resolution.

## Scope

Security is especially critical for Loom because it mediates between AI models and local/remote filesystems. The following areas are highest priority:

- **Gateway authentication and authorization bypass**
- **Policy engine circumvention**
- **Secret exposure through MCP tool surface**
- **Arbitrary command execution without approval**
- **Session hijacking or token leakage**
- **Event log tampering**

## Supported Versions

| Version | Supported |
|---------|:---------:|
| 0.x.y   | ✅ Current development |
| < 0.1   | ❌ Pre-release |
