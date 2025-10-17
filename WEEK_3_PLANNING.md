# Week 3 Planning: OAuth Integration & Social Media Testing

**Date**: October 14-21, 2025  
**Phase**: Core Development - Social Media Integration  
**Status**: 📋 Planning  
**Estimated Time**: 12-15 hours

---

## 🎯 Week 3 Objectives

### Primary Goals
1. **Set up all developer accounts** for social media platforms
2. **Complete OAuth flows** for LinkedIn, Twitter, Facebook/Instagram
3. **Test real publishing** to all platforms
4. **Create scheduled_posts table** and activate deferred indexes
5. **End-to-end integration testing** of publishing system

### Success Metrics
- ✅ All 4 platforms authenticated (LinkedIn, Twitter, Facebook, Instagram)
- ✅ Successful test posts to each platform
- ✅ Scheduled posts working end-to-end
- ✅ OAuth callback flows functional
- ✅ Database fully optimized with all indexes

---

## 📅 Daily Breakdown

### Day 1 (Monday, Oct 14) - Developer Accounts Setup
**Time**: 2-3 hours

**Tasks**:
1. ✅ Create Meta Developer account
   - Sign up at developers.facebook.com
   - Create new app
   - Add Facebook Login product
   - Add Instagram Graph API product
   - Get App ID and App Secret
   - Configure OAuth redirect URIs
   - Submit app for review (if needed)

2. ✅ Create Twitter Developer account
   - Apply at developer.twitter.com
   - Request Elevated access (required for OAuth 1.0a)
   - Create new project + app
   - Enable OAuth 1.0a with Read and Write permissions
   - Get API Key, API Secret, Bearer Token
   - Configure callback URLs

3. ✅ Create LinkedIn Developer account
   - Create company page (if needed)
   - Apply at developer.linkedin.com
   - Create new app
   - Add Sign In with LinkedIn product
   - Request Marketing Developer Platform access
   - Get Client ID and Client Secret
   - Configure redirect URIs

**Deliverables**:
- [ ] Meta app created with credentials
- [ ] Twitter app created with Elevated access
- [ ] LinkedIn app created with MDP access
- [ ] All credentials stored in backend/.env
- [ ] Document account setup in docs/developer_accounts_setup.md

---

### Day 2 (Tuesday, Oct 15) - OAuth Flow Implementation
**Time**: 3-4 hours

**Tasks**:
1. ✅ Update LinkedIn OAuth flow
   - Test authorization URL generation
   - Test callback handling
   - Verify token exchange
   - Test token refresh
   - Store tokens in database
   - Test expired token handling

2. ✅ Update Twitter OAuth flow
   - Implement OAuth 1.0a flow (different from 2.0!)
   - Test 3-legged authentication
   - Verify token exchange
   - Store tokens securely
   - Test API calls with tokens

3. ✅ Update Meta OAuth flow
   - Test Facebook authorization
   - Test Instagram authorization
   - Handle long-lived tokens
   - Store page_id and instagram_account_id
   - Test token validation

**Deliverables**:
- [ ] All OAuth flows functional
- [ ] Tokens stored securely in database
- [ ] OAuth callback endpoints tested
- [ ] Error handling for auth failures
- [ ] Update docs/api_integrations.md with OAuth details

**Files to Update**:
```
app/api/oauth/
├── linkedin.py       - Update with real credentials
├── twitter.py        - Implement OAuth 1.0a
└── meta.py           - Update for Facebook + Instagram
```

---

### Day 3 (Wednesday, Oct 16) - Database Schema Updates
**Time**: 2 hours

**Tasks**:
1. ✅ Create scheduled_posts table
   - Create Alembic migration
   - Add all columns (id, business_id, content_text, platforms, etc.)
   - Add foreign key constraints
   - Run migration

2. ✅ Activate deferred indexes
   - Run migration for scheduled_posts indexes
   - Verify all 7 indexes created
   - Test query performance with new indexes

3. ✅ Update database models
   - Add ScheduledPost model to app/models/
   - Add relationships to Business model
   - Update schemas in app/schemas/

**Deliverables**:
- [ ] scheduled_posts table created
- [ ] All 7 performance indexes active
- [ ] Database models updated
- [ ] Migration tested and verified

**Database Schema**:
```sql
CREATE TABLE scheduled_posts (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id),
    content_text TEXT NOT NULL,
    platforms JSONB NOT NULL,
    platform_params JSONB,
    scheduled_for TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    celery_task_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### Day 4 (Thursday, Oct 17) - Real Publishing Tests
**Time**: 3-4 hours

**Tasks**:
1. ✅ Test LinkedIn publishing
   - Create test LinkedIn account (or use personal)
   - Connect account via OAuth
   - Test single post publishing
   - Test long post (thread creation)
   - Verify post appears on profile
   - Test error scenarios

2. ✅ Test Twitter publishing
   - Connect Twitter account via OAuth
   - Test single tweet publishing
   - Test thread creation (long content)
   - Verify tweets appear on timeline
   - Test @mentions and hashtags
   - Test error scenarios

3. ✅ Test Facebook publishing
   - Connect Facebook page
   - Get page_id from Meta Graph API
   - Test page post publishing
   - Verify post appears on page
   - Test error scenarios

4. ✅ Test Instagram publishing
   - Connect Instagram business account
   - Get instagram_account_id
   - Test Instagram post (text only for now)
   - Verify limitations
   - Document image requirements for future

**Deliverables**:
- [ ] Successful posts to all 4 platforms
- [ ] Screenshots of published posts
- [ ] Error scenarios documented
- [ ] Platform limitations documented

**Testing Checklist**:
```bash
# LinkedIn
curl -X POST "http://localhost:8000/api/v2/publish" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"content":"Test from API","platforms":["linkedin"]}'

# Twitter
curl -X POST "http://localhost:8000/api/v2/publish" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"content":"Test tweet from API","platforms":["twitter"]}'

# Facebook
curl -X POST "http://localhost:8000/api/v2/publish" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"content":"Test post","platforms":["facebook"],"platform_params":{"facebook":{"page_id":"123"}}}'
```

---

### Day 5 (Friday, Oct 18) - Scheduled Publishing Tests
**Time**: 2-3 hours

**Tasks**:
1. ✅ Test scheduling workflow
   - Schedule post for 5 minutes in future
   - Verify ScheduledPost record created
   - Verify Celery task created
   - Wait for scheduled time
   - Verify post published automatically
   - Verify status updated to "published"

2. ✅ Test cancellation workflow
   - Schedule post for 10 minutes in future
   - Cancel via DELETE endpoint
   - Verify Celery task revoked
   - Verify status updated to "cancelled"
   - Verify post never published

3. ✅ Test multi-platform scheduling
   - Schedule post to 3 platforms
   - Verify single ScheduledPost record
   - Verify all platforms publish at scheduled time
   - Check PublishedPost records

**Deliverables**:
- [ ] Scheduling workflow verified
- [ ] Cancellation workflow verified
- [ ] Multi-platform scheduling tested
- [ ] Celery logs show successful execution

**Test Scenario**:
```bash
# 1. Schedule post for 5 minutes from now
FUTURE=$(date -u -v+5M +"%Y-%m-%dT%H:%M:%SZ")
curl -X POST "http://localhost:8000/api/v2/schedule" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"content\":\"Scheduled test\",\"platforms\":[\"linkedin\"],\"scheduled_for\":\"$FUTURE\"}"

# 2. Monitor Celery logs
docker-compose logs -f celery_worker

# 3. Wait 5 minutes and verify post published
```

---

### Day 6 (Saturday, Oct 19) - Frontend Integration
**Time**: 2-3 hours

**Tasks**:
1. ✅ Integrate PublishNowButton
   - Add to content generation page
   - Wire up with generated content
   - Test immediate publishing
   - Handle success/error states
   - Show published post URLs

2. ✅ Integrate SchedulePostModal
   - Add schedule button to content page
   - Connect modal to content state
   - Test scheduling workflow
   - Handle success/error states
   - Redirect to scheduled page on success

3. ✅ Test ScheduledPostsCalendar page
   - Navigate to /dashboard/scheduled
   - Verify calendar renders
   - Test business selector
   - Test month navigation
   - Test post cancellation
   - Verify list view

**Deliverables**:
- [ ] Publishing buttons in content pages
- [ ] Scheduling modal functional
- [ ] Calendar page fully working
- [ ] All user flows tested

**Integration Example**:
```tsx
// In content generation page
import PublishNowButton from '@/components/publishing/PublishNowButton';
import SchedulePostModal from '@/components/publishing/SchedulePostModal';

const [showSchedule, setShowSchedule] = useState(false);

<div className="flex gap-3 mt-4">
  <PublishNowButton
    content={generatedContent}
    platforms={selectedPlatforms}
    businessId={currentBusiness.id}
    onSuccess={(results) => {
      toast.success(`Published to ${results.length} platforms!`);
    }}
  />
  
  <button onClick={() => setShowSchedule(true)}>
    Schedule for Later
  </button>
</div>

<SchedulePostModal
  isOpen={showSchedule}
  onClose={() => setShowSchedule(false)}
  content={generatedContent}
  platforms={selectedPlatforms}
  businessId={currentBusiness.id}
/>
```

---

### Day 7 (Sunday, Oct 20) - Testing & Documentation
**Time**: 2-3 hours

**Tasks**:
1. ✅ End-to-end testing
   - Test complete user flow: Generate → Publish → Verify
   - Test complete user flow: Generate → Schedule → Wait → Verify
   - Test OAuth re-authentication flow
   - Test error scenarios (expired tokens, rate limits)
   - Test with multiple businesses
   - Test with multiple users

2. ✅ Update documentation
   - Document OAuth setup process
   - Update API docs with real examples
   - Document platform limitations
   - Add troubleshooting for OAuth issues
   - Update README with OAuth instructions

3. ✅ Create Week 3 summary
   - Document all achievements
   - Screenshot successful posts
   - Document challenges and solutions
   - Calculate time spent
   - Update project tracker

**Deliverables**:
- [ ] End-to-end tests passing
- [ ] Documentation updated
- [ ] Week 3 summary document
- [ ] Screenshots of working system
- [ ] Project tracker updated

---

## 📋 Task Checklist

### Developer Accounts (Day 1)
- [ ] Meta Developer account created
- [ ] Twitter Developer account created (Elevated access)
- [ ] LinkedIn Developer account created (MDP access)
- [ ] All credentials stored in .env
- [ ] OAuth redirect URIs configured
- [ ] Test apps verified in respective developer consoles

### OAuth Implementation (Day 2)
- [ ] LinkedIn OAuth flow tested
- [ ] Twitter OAuth 1.0a implemented
- [ ] Meta OAuth flow tested
- [ ] Facebook page connection working
- [ ] Instagram account connection working
- [ ] Token storage working
- [ ] Token refresh working

### Database Updates (Day 3)
- [ ] scheduled_posts table created
- [ ] All 7 indexes active
- [ ] ScheduledPost model created
- [ ] Database migration tested
- [ ] Query performance verified

### Publishing Tests (Day 4)
- [ ] LinkedIn post successful
- [ ] Twitter tweet successful
- [ ] Facebook page post successful
- [ ] Instagram post tested
- [ ] Thread creation tested
- [ ] Error handling verified

### Scheduling Tests (Day 5)
- [ ] Schedule workflow tested
- [ ] Cancellation workflow tested
- [ ] Multi-platform scheduling tested
- [ ] Celery execution verified
- [ ] Status updates working

### Frontend Integration (Day 6)
- [ ] PublishNowButton integrated
- [ ] SchedulePostModal integrated
- [ ] Calendar page functional
- [ ] Business selector working
- [ ] Post cancellation working

### Testing & Docs (Day 7)
- [ ] End-to-end tests passing
- [ ] OAuth docs updated
- [ ] API docs updated
- [ ] Week 3 summary created
- [ ] Project tracker updated

---

## 📊 Time Allocation

| Day | Focus | Estimated Time | Priority |
|-----|-------|----------------|----------|
| Mon | Developer Accounts | 2-3 hours | High |
| Tue | OAuth Implementation | 3-4 hours | High |
| Wed | Database Updates | 2 hours | High |
| Thu | Publishing Tests | 3-4 hours | High |
| Fri | Scheduling Tests | 2-3 hours | Medium |
| Sat | Frontend Integration | 2-3 hours | Medium |
| Sun | Testing & Docs | 2-3 hours | Medium |
| **Total** | | **16-22 hours** | |

**Target**: 12-15 hours (spread over 7 days)

---

## 🎯 Success Criteria

### Must Have (P0)
- ✅ All 4 platforms connected via OAuth
- ✅ Successful publishing to all platforms
- ✅ Scheduled posts working end-to-end
- ✅ Database fully optimized
- ✅ Frontend components integrated

### Should Have (P1)
- ✅ OAuth re-authentication flow
- ✅ Error handling for all scenarios
- ✅ Multi-platform publishing tested
- ✅ Complete documentation

### Nice to Have (P2)
- ⏳ Image upload preparation
- ⏳ Analytics tracking setup
- ⏳ Performance monitoring
- ⏳ User onboarding improvements

---

## 🚧 Potential Blockers

### High Risk
1. **Twitter Elevated Access Delay**
   - **Risk**: May take 1-2 weeks for approval
   - **Mitigation**: Apply ASAP, use test account if available
   - **Backup**: Skip Twitter for Week 3, focus on LinkedIn + Meta

2. **Meta App Review Required**
   - **Risk**: Some permissions require app review
   - **Mitigation**: Use test users and test pages (no review needed)
   - **Backup**: Document requirements for future production review

### Medium Risk
3. **LinkedIn MDP Access Delay**
   - **Risk**: Marketing Developer Platform access may need approval
   - **Mitigation**: Apply early, use personal account for testing
   - **Backup**: Document API limitations in free tier

4. **OAuth Callback Issues**
   - **Risk**: Localhost callbacks may not work for all platforms
   - **Mitigation**: Use ngrok for public HTTPS URLs
   - **Backup**: Deploy to staging environment

### Low Risk
5. **Celery Scheduling Timing Issues**
   - **Risk**: Scheduled posts may not execute exactly on time
   - **Mitigation**: Test with 5-10 minute delays
   - **Backup**: Document expected timing variance (±1 minute)

---

## 📝 Documentation Updates

### New Documents to Create
1. **docs/developer_accounts_setup.md**
   - Step-by-step account creation
   - Credential management
   - OAuth app configuration
   - Testing guidelines

2. **docs/oauth_implementation_guide.md**
   - OAuth flow diagrams
   - Code examples
   - Token management
   - Troubleshooting

3. **WEEK_3_SUMMARY.md**
   - Achievements
   - Challenges
   - Screenshots
   - Lessons learned

### Documents to Update
1. **docs/api_integrations.md**
   - Add real OAuth examples
   - Document callback URLs
   - Add platform limitations

2. **docs/TROUBLESHOOTING_PUBLISHING.md**
   - Add OAuth-specific issues
   - Add platform-specific errors
   - Update with real-world scenarios

3. **project_tracker.md**
   - Update Week 3 progress
   - Add new metrics
   - Update completion percentage

4. **README.md**
   - Add OAuth setup instructions
   - Update getting started guide
   - Add screenshots

---

## 🧪 Testing Strategy

### Unit Tests
```python
# Test OAuth flows
def test_linkedin_oauth_callback():
    # Mock OAuth response
    # Test token exchange
    # Verify token storage
    pass

def test_token_refresh():
    # Mock expired token
    # Test refresh flow
    # Verify new token stored
    pass
```

### Integration Tests
```python
# Test publishing with real tokens
def test_publish_to_linkedin():
    # Use test account token
    # Publish test post
    # Verify post ID returned
    pass

def test_scheduled_post_execution():
    # Schedule post for near future
    # Wait for execution
    # Verify post published
    pass
```

### Manual Tests
- [ ] Complete user flow: Sign up → Connect accounts → Publish
- [ ] Test on different browsers (Chrome, Safari, Firefox)
- [ ] Test on mobile devices
- [ ] Test with different account types (personal, business)
- [ ] Test rate limiting behavior
- [ ] Test error recovery

---

## 🔗 Resources

### Platform Documentation
- **LinkedIn**: https://docs.microsoft.com/en-us/linkedin/
- **Twitter**: https://developer.twitter.com/en/docs
- **Meta**: https://developers.facebook.com/docs/
- **Instagram**: https://developers.facebook.com/docs/instagram-api

### OAuth Guides
- LinkedIn OAuth 2.0: https://docs.microsoft.com/en-us/linkedin/shared/authentication/
- Twitter OAuth 1.0a: https://developer.twitter.com/en/docs/authentication/oauth-1-0a
- Facebook Login: https://developers.facebook.com/docs/facebook-login/
- Instagram Auth: https://developers.facebook.com/docs/instagram-basic-display-api/getting-started

### Tools
- **ngrok**: For HTTPS tunneling (OAuth callbacks)
- **Postman**: For API testing
- **Redis Commander**: For viewing Redis data
- **pgAdmin**: For database management

---

## 💡 Tips & Best Practices

### OAuth Implementation
1. **Use state parameter** - Already implemented with Redis
2. **Store refresh tokens** - For long-lived access
3. **Handle token expiration** - Graceful re-auth prompts
4. **Test error scenarios** - Denied permissions, cancelled auth
5. **Use HTTPS in production** - Required by most platforms

### Testing
1. **Start with one platform** - Get LinkedIn working first
2. **Use test accounts** - Don't spam your personal accounts
3. **Small batches** - Test with short posts first
4. **Monitor logs** - Celery and backend logs are crucial
5. **Document everything** - Screenshots, errors, solutions

### Time Management
1. **One platform per day** - Don't rush all at once
2. **Take breaks** - OAuth debugging can be frustrating
3. **Ask for help** - Developer forums are helpful
4. **Timebox tasks** - Move on if stuck > 30 minutes
5. **Celebrate wins** - First successful post is a big deal!

---

## 📈 Success Metrics

### Quantitative
- [ ] 4/4 platforms authenticated
- [ ] 100% OAuth callback success rate
- [ ] 4/4 platforms publishing successfully
- [ ] 10+ test posts published
- [ ] 5+ scheduled posts executed
- [ ] 0 critical bugs

### Qualitative
- [ ] OAuth flow feels smooth
- [ ] Error messages are helpful
- [ ] Publishing is fast (<2 seconds)
- [ ] UI is intuitive
- [ ] Documentation is clear

---

## 🎉 Week 3 Completion Definition

Week 3 is considered **COMPLETE** when:

1. ✅ All developer accounts created and verified
2. ✅ OAuth flows functional for all platforms
3. ✅ At least one successful test post to each platform
4. ✅ Scheduled posts working end-to-end
5. ✅ scheduled_posts table created with all indexes
6. ✅ Frontend components integrated and tested
7. ✅ Documentation updated with OAuth details
8. ✅ Week 3 summary document created

**Bonus Achievements** (not required):
- ⭐ Image upload foundation laid
- ⭐ Analytics tracking implemented
- ⭐ Performance monitoring added
- ⭐ User onboarding improved

---

## 📞 Getting Help

### Stuck on OAuth?
1. Check platform documentation
2. Search Stack Overflow
3. Check GitHub issues for similar integrations
4. Post in platform developer forums
5. Use AI assistant for debugging

### Celery Issues?
1. Check docker-compose logs
2. Verify Redis connection
3. Test with simple task first
4. Review Celery documentation
5. Check flower (Celery monitoring tool)

### Database Issues?
1. Check Alembic migrations
2. Verify PostgreSQL connection
3. Test queries in pgAdmin
4. Review database logs
5. Check connection pooling status

---

## 🚀 After Week 3

### Week 4 Preview: Content & Analytics
- Content generation improvements
- Post analytics integration
- Performance dashboard
- Content calendar view
- A/B testing framework

**Estimated Time**: 12-15 hours

---

**Week 3 Start Date**: October 14, 2025  
**Week 3 End Date**: October 20, 2025  
**Status**: 📋 Ready to Start!

Let's make Week 3 amazing! 🚀

---

*This plan will be updated daily with progress and adjustments.*
