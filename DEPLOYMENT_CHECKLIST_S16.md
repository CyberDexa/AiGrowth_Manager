# Session 16 - Production Deployment Checklist

## Pre-Deployment

### Environment Configuration
- [ ] Generate encryption key: `python scripts/generate_encryption_key.py`
- [ ] Add `ENCRYPTION_KEY` to production .env (backup securely!)
- [ ] Set `ENVIRONMENT=production` in .env
- [ ] Update `VERSION` for release tracking (e.g., `0.2.0`)
- [ ] Configure `SENTRY_DSN` for error tracking
- [ ] Set `LOG_LEVEL=INFO` (or `WARNING` for production)
- [ ] Verify all OAuth credentials (LinkedIn, Twitter, Meta)
- [ ] Update OAuth redirect URIs to production URLs

### Security Review
- [ ] Verify token encryption is enabled
- [ ] Test state parameter validation
- [ ] Confirm 10-minute state expiry
- [ ] Check one-time state use enforcement
- [ ] Verify tokens are encrypted in database
- [ ] Test token decryption for refresh/revocation
- [ ] Review Sentry PII settings (`send_default_pii=False`)
- [ ] Confirm HTTPS for all OAuth callbacks

### Code Review
- [ ] All OAuth flows tested (LinkedIn, Twitter, Meta)
- [ ] Token refresh working (Twitter)
- [ ] Token revocation working (all platforms)
- [ ] Sync status endpoints returning correct data
- [ ] Dashboard widget displays real-time status
- [ ] Error handling tested for all failure scenarios
- [ ] Logging outputs structured JSON
- [ ] Sentry captures errors correctly

---

## Deployment Steps

### Backend Deployment

#### 1. Database Migration
```bash
cd backend
alembic upgrade head
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Set Environment Variables
```bash
export ENCRYPTION_KEY="<your-generated-key>"
export SENTRY_DSN="https://your-dsn@sentry.io/project-id"
export ENVIRONMENT="production"
export VERSION="0.2.0"
export LOG_LEVEL="INFO"

# OAuth credentials
export LINKEDIN_CLIENT_ID="..."
export LINKEDIN_CLIENT_SECRET="..."
export LINKEDIN_REDIRECT_URI="https://your-domain.com/api/v1/oauth/linkedin/callback"

export TWITTER_CLIENT_ID="..."
export TWITTER_CLIENT_SECRET="..."
export TWITTER_REDIRECT_URI="https://your-domain.com/api/v1/oauth/twitter/callback"

export META_CLIENT_ID="..."
export META_CLIENT_SECRET="..."
export META_REDIRECT_URI="https://your-domain.com/api/v1/oauth/meta/callback"
```

#### 4. Start Application
```bash
# With Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 5. Verify Backend
```bash
curl https://your-domain.com/health
# Should return: {"status": "healthy", "environment": "production"}

curl https://your-domain.com/api/v1/oauth/platforms
# Should return list of platforms
```

---

### Frontend Deployment

#### 1. Build Production Bundle
```bash
cd frontend
npm run build
```

#### 2. Environment Variables
```bash
export NEXT_PUBLIC_API_URL="https://your-backend-domain.com"
```

#### 3. Start Production Server
```bash
npm run start
```

#### 4. Verify Frontend
Visit: https://your-frontend-domain.com/dashboard/analytics

Check:
- [ ] Dashboard loads without errors
- [ ] Sync status widget displays
- [ ] Auto-refresh works (30s interval)
- [ ] "Sync Now" button functional
- [ ] Platform details expand/collapse

---

## Post-Deployment Verification

### Functional Testing

#### OAuth Flows
- [ ] Test LinkedIn OAuth flow end-to-end
- [ ] Test Twitter OAuth flow with PKCE
- [ ] Test Meta OAuth flow with Page selection
- [ ] Verify tokens are encrypted in database
- [ ] Test token refresh (Twitter)
- [ ] Test token revocation (all platforms)

#### Dashboard Features
- [ ] Sync status displays correctly
- [ ] Platform breakdown shows accurate data
- [ ] Manual sync trigger works
- [ ] Sync history loads
- [ ] Token expiration warnings appear
- [ ] Error states display properly

#### Monitoring
- [ ] Check Sentry for captured events
- [ ] Verify structured logs in log aggregator
- [ ] Confirm request IDs in logs
- [ ] Test breadcrumb trail in Sentry
- [ ] Verify user context attached to errors

---

## Monitoring Setup

### Log Aggregation
- [ ] Configure log shipping (Filebeat, Fluentd, etc.)
- [ ] Set up log aggregation (ELK, Splunk, Datadog)
- [ ] Create dashboards for key metrics
- [ ] Set up alerts for errors
- [ ] Configure retention policies

### Sentry Configuration
- [ ] Verify Sentry project created
- [ ] Set up error alerts (email, Slack)
- [ ] Configure performance thresholds
- [ ] Create custom dashboards
- [ ] Set up release tracking
- [ ] Configure user feedback

### Metrics & Dashboards
- [ ] OAuth success rate
- [ ] Token refresh rate
- [ ] Sync job success rate
- [ ] API response times
- [ ] Error rates by endpoint
- [ ] Database query performance

---

## Security Hardening

### Production Security
- [ ] Enable HTTPS for all endpoints
- [ ] Configure CORS for production domains
- [ ] Set up rate limiting (OAuth endpoints)
- [ ] Enable request throttling
- [ ] Configure IP whitelisting (if needed)
- [ ] Set up WAF rules (if applicable)
- [ ] Review and restrict CORS origins

### Secret Management
- [ ] Encryption key backed up securely
- [ ] OAuth secrets in secure vault
- [ ] Database credentials rotated
- [ ] Sentry DSN protected
- [ ] Environment variables secured
- [ ] Access logs enabled

---

## Performance Optimization

### Backend
- [ ] Database indexes created (SocialAccount queries)
- [ ] Connection pooling configured
- [ ] Redis cache for state storage (recommended)
- [ ] API response caching enabled
- [ ] Database query optimization
- [ ] Background job optimization

### Frontend
- [ ] CDN configured for static assets
- [ ] Image optimization enabled
- [ ] Code splitting configured
- [ ] Lazy loading implemented
- [ ] SWR cache tuned
- [ ] Performance monitoring enabled

---

## Rollback Plan

### If Issues Arise

#### Quick Rollback
1. Revert to previous release
2. Restore database snapshot (if needed)
3. Clear encryption key cache
4. Restart services
5. Verify health endpoints

#### Database Rollback
```bash
# Rollback last migration
alembic downgrade -1

# Or specific version
alembic downgrade <revision>
```

#### Emergency Contacts
- DevOps Team: [contact info]
- Security Team: [contact info]
- On-call Engineer: [contact info]

---

## Production Monitoring

### Health Checks
- [ ] `/health` endpoint responding
- [ ] Database connectivity verified
- [ ] OAuth services accessible
- [ ] Sentry SDK initialized
- [ ] Logging configured correctly

### Key Metrics to Watch
- **OAuth Success Rate**: >95%
- **Token Encryption**: 100%
- **State Validation**: 100%
- **API Response Time**: <500ms p95
- **Error Rate**: <1%
- **Sync Job Success**: >98%

### Alert Thresholds
- Error rate >5% - Critical
- Response time >1s p95 - Warning
- OAuth failure rate >10% - Critical
- Database connection errors - Critical
- Encryption failures - Critical

---

## Documentation

### Update Documentation
- [ ] API documentation updated
- [ ] OAuth setup guide current
- [ ] Troubleshooting guide updated
- [ ] Release notes published
- [ ] Change log updated
- [ ] Team notified of new features

---

## Post-Deployment Tasks

### Week 1
- [ ] Monitor error rates daily
- [ ] Review Sentry issues
- [ ] Check log aggregation
- [ ] Verify OAuth metrics
- [ ] User feedback collection
- [ ] Performance baseline established

### Week 2
- [ ] Analyze usage patterns
- [ ] Optimize slow queries
- [ ] Review security logs
- [ ] Update monitoring dashboards
- [ ] Plan optimizations

### Ongoing
- [ ] Weekly error review
- [ ] Monthly security audit
- [ ] Quarterly token rotation
- [ ] Regular backup verification
- [ ] Performance optimization
- [ ] Feature usage analysis

---

## Success Criteria

### Must Have (Go/No-Go)
- ✅ OAuth flows work for all 3 platforms
- ✅ Tokens encrypted at rest
- ✅ State validation prevents CSRF
- ✅ Sentry captures errors
- ✅ Structured logs available
- ✅ Dashboard displays sync status
- ✅ No critical security issues

### Should Have
- ✅ Response times <500ms p95
- ✅ Error rate <1%
- ✅ 99% uptime SLA met
- ✅ All monitoring configured
- ✅ Documentation complete

### Nice to Have
- 🔄 Redis state storage (Session 17)
- 🔄 Rate limiting (Session 17)
- 🔄 Multi-account support
- 🔄 Advanced analytics
- 🔄 Webhook support

---

## Stakeholder Sign-Off

### Required Approvals
- [ ] Engineering Lead: _________________ Date: _______
- [ ] Security Team: ___________________ Date: _______
- [ ] Product Manager: _________________ Date: _______
- [ ] DevOps Lead: ____________________ Date: _______

---

## Rollout Plan

### Phase 1: Canary (5%)
- [ ] Deploy to 5% of users
- [ ] Monitor for 24 hours
- [ ] Review metrics
- [ ] Check error rates
- [ ] Collect feedback

### Phase 2: Beta (25%)
- [ ] Deploy to 25% of users
- [ ] Monitor for 48 hours
- [ ] Review performance
- [ ] Verify stability

### Phase 3: Full Rollout (100%)
- [ ] Deploy to all users
- [ ] Monitor closely
- [ ] Announce new features
- [ ] Update documentation
- [ ] Celebrate! 🎉

---

**Deployment Checklist v1.0**  
**Last Updated**: Session 16  
**Status**: Ready for Production ✅

---

## Notes
_Use this space for deployment-specific notes, issues encountered, or special configurations:_

```

```
