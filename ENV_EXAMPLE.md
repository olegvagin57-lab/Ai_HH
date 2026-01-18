# Environment Variables Example

Copy these variables to your `.env` file (in project root) and fill in your actual values.
**NEVER commit `.env` file to version control!**

```env
# Environment
ENVIRONMENT=development
DEBUG=true

# MongoDB Configuration
# For local development: mongodb://localhost:27017
# For production with auth: mongodb://username:password@host:27017/database?authSource=admin
# For MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=hh_analyzer

# Redis Configuration
# For local development: redis://localhost:6379
# For production with auth: redis://:password@host:6379
# For Redis Cloud: rediss://:password@host:port
REDIS_URL=redis://localhost:6379

# HeadHunter API (OAuth)
HH_CLIENT_ID=your-hh-client-id
HH_CLIENT_SECRET=your-hh-client-secret
HH_REDIRECT_URI=http://localhost:3000/auth/callback

# Cloudflare Worker (Gemini API proxy)
CLOUDFLARE_WORKER_URL=https://proud-water-5293.olegvagin1311.workers.dev
GEMINI_API_KEY=

# Security - CRITICAL: Generate a strong secret key for production!
# Use: python -c "import secrets; print(secrets.token_urlsafe(32))"
# Minimum 32 characters required
SECRET_KEY=your-secret-key-here-change-in-production-min-32-chars-required
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
# For development: http://localhost:3000
# For production: https://yourdomain.com,https://www.yourdomain.com
CORS_ORIGINS=http://localhost:3000

# AI Settings
MAX_RESUMES_FOR_DEEP_ANALYSIS=50
MAX_RESUMES_FROM_SEARCH=200

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Logging
LOG_FORMAT=json
LOG_LEVEL=INFO
LOG_FILE=
```

## Generating SECRET_KEY

For production, generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Or using OpenSSL:
```bash
openssl rand -base64 32
```
