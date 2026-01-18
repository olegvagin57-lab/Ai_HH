# Production Deployment Guide

This guide provides step-by-step instructions for deploying HH Resume Analyzer to production.

## Prerequisites

- Server with Docker and Docker Compose installed
- Domain name configured with DNS pointing to your server
- SSH access to the server
- Basic knowledge of Linux server administration

## Pre-Deployment Checklist

Before deploying, ensure you have completed all items in [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md).

## Server Setup

### 1. Initial Server Configuration

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone Repository

```bash
cd /opt
sudo git clone <your-repo-url> hh-analyzer
cd hh-analyzer
sudo chown -R $USER:$USER .
```

### 3. Configure Environment Variables

```bash
# Copy environment template
cp ENV_EXAMPLE.md .env

# Edit .env file with your production values
nano .env
```

**Critical variables to set:**

- `SECRET_KEY`: Generate a strong secret key (32+ characters)
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

- `MONGODB_URL`: Production MongoDB connection string
- `REDIS_URL`: Production Redis connection string
- `CORS_ORIGINS`: Your production domain(s)
- `ENVIRONMENT=production`
- `DEBUG=false`

### 4. Set Up SSL Certificates

#### Option A: Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to project
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/chain.pem nginx/ssl/

# Set permissions
sudo chown $USER:$USER nginx/ssl/*.pem
chmod 600 nginx/ssl/privkey.pem
chmod 644 nginx/ssl/*.pem
```

#### Option B: Using Script

```bash
chmod +x scripts/setup-ssl.sh
./scripts/setup-ssl.sh yourdomain.com admin@yourdomain.com
```

### 5. Update Nginx Configuration

Edit `nginx/nginx.prod.conf` and replace `yourdomain.com` with your actual domain:

```nginx
server_name yourdomain.com www.yourdomain.com;
```

### 6. Configure MongoDB Authentication (Recommended)

```bash
# Start MongoDB container
docker-compose -f docker-compose.prod.yml up -d mongodb

# Create admin user
docker-compose -f docker-compose.prod.yml exec mongodb mongosh admin --eval "
db.createUser({
  user: 'admin',
  pwd: 'your-secure-password',
  roles: [{ role: 'root', db: 'admin' }]
})
"

# Update MONGODB_URL in .env
# mongodb://admin:your-secure-password@mongodb:27017/hh_analyzer?authSource=admin
```

### 7. Set Up Database Backups

```bash
# Make backup script executable
chmod +x scripts/backup_mongodb.sh

# Test backup
./scripts/backup_mongodb.sh

# Schedule automatic backups (daily at 2 AM)
chmod +x scripts/schedule_backup.sh
./scripts/schedule_backup.sh "0 2 * * *"
```

## Deployment

### 1. Build and Start Services

```bash
# Pull latest images (if using Docker Hub)
docker-compose -f docker-compose.prod.yml pull

# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 2. Run Database Migrations

```bash
docker-compose -f docker-compose.prod.yml exec backend python scripts/run_migrations.py
```

### 3. Verify Deployment

```bash
# Run smoke tests
chmod +x scripts/smoke_tests.sh
./scripts/smoke_tests.sh https://yourdomain.com

# Check health endpoints
curl https://yourdomain.com/api/v1/health
curl https://yourdomain.com/api/v1/health/ready
curl https://yourdomain.com/api/v1/health/live
```

### 4. Set Up Monitoring (Optional)

```bash
# Start monitoring stack
docker-compose -f docker-compose.prod.yml -f monitoring/docker-compose.monitoring.yml up -d

# Access Grafana
# http://yourdomain.com:3001 (configure reverse proxy for production)
# Default credentials: admin/admin (change on first login)
```

### 5. Set Up Logging (Optional)

```bash
# Start logging stack
docker-compose -f docker-compose.prod.yml -f monitoring/docker-compose.logging.yml up -d
```

## Post-Deployment

### 1. Create Admin User

```bash
docker-compose -f docker-compose.prod.yml exec backend python -c "
from app.application.services.auth_service import AuthService
import asyncio

async def create_admin():
    auth_service = AuthService()
    user = await auth_service.register_user(
        email='admin@yourdomain.com',
        username='admin',
        password='SecurePassword123!',
        role_names=['admin']
    )
    print(f'Admin user created: {user.email}')

asyncio.run(create_admin())
"
```

### 2. Configure Firewall

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS
sudo ufw enable
```

### 3. Set Up Automatic Certificate Renewal

```bash
# Add cron job for certificate renewal
sudo crontab -e

# Add this line (runs daily at 3 AM)
0 3 * * * certbot renew --quiet --deploy-hook "docker-compose -f /opt/hh-analyzer/docker-compose.prod.yml restart nginx"
```

## Updating Deployment

### Manual Update

```bash
cd /opt/hh-analyzer

# Pull latest code
git pull

# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python scripts/run_migrations.py

# Restart services
docker-compose -f docker-compose.prod.yml up -d --no-deps --build backend celery celery-beat
docker-compose -f docker-compose.prod.yml restart nginx

# Verify
./scripts/smoke_tests.sh https://yourdomain.com
```

### Automated Update (via CI/CD)

The GitHub Actions workflow (`.github/workflows/cd.yml`) will automatically deploy when you push to `main` branch.

Ensure you have configured the following secrets in GitHub:
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `PRODUCTION_HOST`
- `PRODUCTION_USER`
- `PRODUCTION_SSH_KEY`

## Troubleshooting

### Check Service Status

```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs celery
```

### Check Health Endpoints

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/health/detailed
```

### Restart Services

```bash
docker-compose -f docker-compose.prod.yml restart
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Database Backup and Restore

```bash
# Backup
./scripts/backup_mongodb.sh

# Restore
./scripts/restore_mongodb.sh backups/mongodb_backup_*.tar.gz
```

## Rollback

If deployment fails:

```bash
# Stop current deployment
docker-compose -f docker-compose.prod.yml down

# Use previous image version
docker-compose -f docker-compose.prod.yml pull hh-analyzer-backend:previous-tag
docker-compose -f docker-compose.prod.yml up -d
```

## Security Considerations

1. **Never commit `.env` file** - It contains sensitive information
2. **Use strong passwords** - For MongoDB, Redis, and admin users
3. **Enable firewall** - Only allow necessary ports
4. **Keep dependencies updated** - Regularly update Docker images
5. **Monitor logs** - Check for suspicious activity
6. **Regular backups** - Ensure backups are working
7. **SSL certificates** - Keep them renewed automatically

## Performance Tuning

### MongoDB

- Adjust `wiredTigerCacheSizeGB` based on available memory
- Enable replication for high availability
- Use MongoDB Atlas for managed service

### Redis

- Configure `maxmemory` and `maxmemory-policy`
- Use Redis persistence (AOF or RDB)
- Consider Redis Cloud for managed service

### Application

- Adjust worker count in `backend/Dockerfile` CMD
- Scale Celery workers based on load
- Use load balancer for multiple backend instances

## Support

For issues or questions:
1. Check logs: `docker-compose -f docker-compose.prod.yml logs`
2. Review health endpoints: `/api/v1/health/detailed`
3. Check monitoring dashboards (if configured)
4. Review GitHub Issues
