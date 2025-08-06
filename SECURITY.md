# Security Policy

## Supported Versions

We actively support the following versions of equalearn.ai.:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in equalearn.ai., please follow these steps:

### 1. **DO NOT** create a public GitHub issue

Security vulnerabilities should be reported privately to protect our users.

### 2. Email Security Report

Send an email to: [security@equalearn.ai](mailto:security@equalearn.ai)

Please include the following information:

- **Description**: A clear description of the vulnerability
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Impact**: Potential impact of the vulnerability
- **Suggested Fix**: If you have a suggested fix (optional)
- **Affected Version**: Which version(s) are affected
- **Environment**: Operating system, Python version, etc.

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Resolution**: As soon as possible, typically within 30 days

### 4. Disclosure Policy

- We will acknowledge receipt of your report within 48 hours
- We will provide regular updates on the progress
- Once the issue is resolved, we will:
  - Credit you in the security advisory (if you wish)
  - Publish a security advisory on GitHub
  - Release a patched version

## Security Best Practices

### For Users

1. **Keep Updated**: Always use the latest version of equalearn.ai.
2. **Local Deployment**: Run the application locally for maximum security
3. **Model Security**: Only use trusted AI models from official sources
4. **File Uploads**: Be cautious with file uploads, especially from untrusted sources
5. **Network Security**: Use HTTPS in production environments

### For Developers

1. **Dependency Updates**: Regularly update dependencies
2. **Input Validation**: Always validate and sanitize user inputs
3. **File Handling**: Implement proper file type and size validation
4. **Error Handling**: Avoid exposing sensitive information in error messages
5. **Access Control**: Implement proper access controls if deploying publicly

## Security Features

### Current Security Measures

- **Local Processing**: All AI processing happens locally, no data sent to external servers
- **File Validation**: Strict file type and size validation
- **Input Sanitization**: User inputs are sanitized before processing
- **Error Handling**: Secure error handling that doesn't expose sensitive information
- **No Data Collection**: The application doesn't collect or store user data

### Planned Security Enhancements

- [ ] Rate limiting for API endpoints
- [ ] Enhanced file validation
- [ ] Security headers implementation
- [ ] Automated security scanning
- [ ] Security audit tools integration

## Responsible Disclosure

We believe in responsible disclosure. If you find a vulnerability:

1. **Report Privately**: Don't disclose publicly until we've had time to fix it
2. **Give Us Time**: Allow us reasonable time to investigate and fix the issue
3. **Work Together**: We're happy to work with security researchers
4. **Credit**: We'll credit you in our security advisories

## Security Contacts

- **Security Email**: [security@equalearn.ai](mailto:security@equalearn.ai)
- **PGP Key**: Available upon request
- **GitHub Security**: Use GitHub's security advisory feature

Thank you for helping keep equalearn.ai. secure! 🔒 