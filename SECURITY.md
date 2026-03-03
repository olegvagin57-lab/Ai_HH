# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it by emailing the project maintainer or creating a private security advisory on GitHub.

**Please do not report security vulnerabilities through public GitHub issues.**

### What to include in your report:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response time:

- Initial response: within 48 hours
- Status update: within 7 days
- Fix timeline: depends on severity

## Security Best Practices

### For Production Deployment:

1. **Environment Variables**
   - Never commit .env files to version control
   - Generate strong SECRET_KEY (min 32 characters): python -c "import secrets; print(secrets.token_urlsafe(32))"
   - Use unique credentials for each environment

2. **Secrets**
   - Never commit `.env` files or tokens/keys to the repository
   - Rotate secrets regularly (especially `SECRET_KEY`)

3. **Database**
   - Use strong MongoDB passwords
   - Enable authentication
   - Restrict network access

4. **CORS**
   - Configure CORS_ORIGINS to only allow your domain
   - Never use * in production

5. **HTTPS**
   - Always use HTTPS in production
   - Set up SSL/TLS certificates

6. **Dependencies**
   - Regularly update dependencies
   - Run 
pm audit and pip-audit
   - Monitor security advisories

## Known Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Rate limiting
- Input validation with Pydantic
- Role-based access control (RBAC)
- CORS protection
- Security headers middleware

