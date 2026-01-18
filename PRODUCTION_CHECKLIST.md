# Production Deployment Checklist

Use this checklist before deploying to production to ensure everything is properly configured.

## Security

- [ ] All secrets moved to environment variables (no hardcoded secrets)
- [ ] `SECRET_KEY` generated and is at least 32 characters
- [ ] `SECRET_KEY` is different from development/staging
- [ ] MongoDB authentication enabled (if applicable)
- [ ] Redis password set (if applicable)
- [ ] CORS origins configured for production domain only
- [ ] `DEBUG=false` in production environment
- [ ] `ENVIRONMENT=production` set
- [ ] SSL/TLS certificates obtained and configured
- [ ] Firewall configured (only necessary ports open)
- [ ] `.env` file is in `.gitignore` and not committed

## Infrastructure

- [ ] Server has sufficient resources (CPU, RAM, disk)
- [ ] Docker and Docker Compose installed
- [ ] Domain name DNS configured correctly
- [ ] SSL certificates valid and auto-renewal configured
- [ ] MongoDB connection string tested
- [ ] Redis connection string tested
- [ ] Network configuration correct
- [ ] Health checks passing

## Database

- [ ] MongoDB backup strategy configured
- [ ] Backup scripts tested
- [ ] Backup retention policy set (30 days recommended)
- [ ] Database migrations system ready
- [ ] Initial database schema created
- [ ] Database indexes created
- [ ] Database authentication configured (if applicable)

## Application Configuration

- [ ] All environment variables set in `.env` file
- [ ] `docker-compose.prod.yml` configured correctly
- [ ] Nginx configuration updated with correct domain
- [ ] CORS origins set correctly
- [ ] Rate limiting configured appropriately
- [ ] Log level set to INFO or WARNING (not DEBUG)
- [ ] Log rotation configured

## Monitoring and Logging

- [ ] Prometheus configured (optional but recommended)
- [ ] Grafana dashboards set up (optional)
- [ ] Alertmanager configured with notification channels
- [ ] Centralized logging configured (Loki/ELK)
- [ ] Health check endpoints tested
- [ ] Metrics endpoint accessible
- [ ] Log aggregation working

## CI/CD

- [ ] GitHub Actions secrets configured
- [ ] Docker Hub credentials set
- [ ] SSH keys for deployment server configured
- [ ] CD pipeline tested on staging
- [ ] Smoke tests passing
- [ ] Rollback procedure documented and tested

## Testing

- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Staging environment tested
- [ ] Smoke tests created and passing
- [ ] Load testing performed (if applicable)
- [ ] Security audit completed

## Documentation

- [ ] `DEPLOYMENT.md` reviewed
- [ ] `PRODUCTION_CHECKLIST.md` completed
- [ ] Runbook created for common operations
- [ ] Incident response plan documented
- [ ] Contact information for support team available

## Pre-Deployment

- [ ] Code reviewed and approved
- [ ] All dependencies updated and secure
- [ ] Database migrations tested
- [ ] Backup of current production (if updating)
- [ ] Deployment window scheduled
- [ ] Team notified of deployment

## Deployment Steps

- [ ] Server access verified
- [ ] Repository cloned/updated
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Services started successfully
- [ ] Database migrations applied
- [ ] Health checks passing
- [ ] Smoke tests passing
- [ ] Monitoring dashboards showing data

## Post-Deployment

- [ ] Admin user created
- [ ] Application accessible via domain
- [ ] HTTPS working correctly
- [ ] API endpoints responding
- [ ] Frontend loading correctly
- [ ] All features tested manually
- [ ] Performance metrics acceptable
- [ ] Error logs reviewed (no critical errors)
- [ ] Team notified of successful deployment

## Rollback Plan

- [ ] Previous version tagged
- [ ] Rollback procedure documented
- [ ] Rollback tested in staging
- [ ] Database backup available
- [ ] Team knows how to execute rollback

## Ongoing Maintenance

- [ ] Backup verification scheduled (weekly)
- [ ] SSL certificate renewal automated
- [ ] Dependency updates scheduled (monthly)
- [ ] Security patches applied promptly
- [ ] Log rotation working
- [ ] Monitoring alerts configured
- [ ] Performance reviews scheduled

## Sign-Off

- [ ] Technical lead approval: _________________ Date: _______
- [ ] Security review: _________________ Date: _______
- [ ] Operations approval: _________________ Date: _______

## Notes

Add any additional notes or concerns here:

_____________________________________________________________
_____________________________________________________________
_____________________________________________________________

## Quick Reference

### Health Check URLs
- General: `https://yourdomain.com/api/v1/health`
- Readiness: `https://yourdomain.com/api/v1/health/ready`
- Liveness: `https://yourdomain.com/api/v1/health/live`
- Detailed: `https://yourdomain.com/api/v1/health/detailed`

### Useful Commands

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python scripts/run_migrations.py

# Create backup
./scripts/backup_mongodb.sh

# Run smoke tests
./scripts/smoke_tests.sh https://yourdomain.com
```
