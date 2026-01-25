# Security Policy

## Supported Versions

This repository contains operational templates, scripts, and automation tooling
for internal use. Security updates are applied to the main branch.

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this repository, please report it
responsibly.

### How to Report

1. **Do NOT** open a public GitHub issue for security vulnerabilities.
2. Contact the repository administrators directly via the organization's
   internal communication channels.
3. If you must use email, reach out to the repository owner listed in the
   organization profile.

### What to Include

- Description of the vulnerability
- Steps to reproduce (if applicable)
- Potential impact assessment
- Any suggested remediation

### Response Timeline

- **Acknowledgment**: Within 48 hours of report receipt
- **Initial Assessment**: Within 7 days
- **Resolution Target**: Depends on severity
  - Critical: 24-72 hours
  - High: 7 days
  - Medium: 30 days
  - Low: Next planned release

## Security Best Practices

### Repository Hygiene

This repository follows these security practices:

1. **No credentials in code**: API keys, tokens, and passwords must never be
   committed. Use environment variables or a secrets manager.

2. **No personal data**: Do not store PII (names, emails, addresses) in the
   repository or tracker.

3. **Dependency management**: Python dependencies are pinned and validated
   against known vulnerabilities.

4. **Input validation**: Scripts validate input data before processing.

### For Contributors

When contributing to this repository:

- Do not hardcode secrets or credentials
- Do not commit sensitive configuration files
- Review dependencies before adding them
- Follow the principle of least privilege for any automation

### For Operators

When deploying or running scripts:

- Use environment variables for sensitive configuration
- Enable MFA on all connected accounts
- Review automation permissions regularly
- Keep local copies secured

## Scope

This security policy covers:

- All code in this repository
- Scripts and automation tooling
- Documentation containing operational procedures
- Any deployed instances of Forge or other public-facing components

## Out of Scope

The following are outside the scope of this security policy:

- Third-party services referenced in documentation (ElevenLabs, Runway, etc.)
- External platforms (TikTok, YouTube, Instagram, Facebook)
- Personal devices used to access this repository
