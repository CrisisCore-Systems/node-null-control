# Security Policy

## Supported Versions

Operational templates, scripts, and automation tooling for internal use.
Security updates go to the main branch.

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

## Reporting a Vulnerability

Report security issues responsibly.

### How to Report

1. **Don't** open a public GitHub issue.
2. Contact the repo admins via internal channels.
3. If you must use email, reach out to the owner listed in the org profile.

### What to Include

- Description
- Repro steps (if applicable)
- Potential impact
- Suggested fix

### Response Timeline

- **Acknowledgment**: 48 hours
- **Initial Assessment**: 7 days
- **Resolution**:
  - Critical: 24-72 hours
  - High: 7 days
  - Medium: 30 days
  - Low: Next release

## Security Practices

### Repo Hygiene

1. **No credentials in code**: Use env vars or a secrets manager.
2. **No personal data**: No PII in the repo or tracker.
3. **Dependency management**: Python deps pinned and checked for vulns.
4. **Input validation**: Scripts validate input before processing.

### For Contributors

- Don't hardcode secrets
- Don't commit sensitive config
- Review dependencies before adding
- Least privilege for automation

### For Operators

- Use env vars for sensitive config
- MFA on all connected accounts
- Review automation permissions regularly
- Keep local copies secured

## Scope

Covers:
- All code in this repository
- Scripts and automation
- Operational docs
- Deployed Forge instances

## Out of Scope

- Third-party services (ElevenLabs, Runway, etc.)
- External platforms (TikTok, YouTube, Instagram, Facebook)
- Personal devices
