# Environment Variables Setup

## Required Clerk Variables

To set up authentication, you need to create a Clerk account and get your API keys:

1. Go to https://clerk.com and create an account
2. Create a new application
3. Go to "API Keys" in the Clerk dashboard
4. Copy the following keys:

```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
CLERK_SECRET_KEY=sk_test_xxxxx
```

## Steps to Get Clerk Keys

1. Visit https://dashboard.clerk.com
2. Click "Create Application"
3. Name your application: "AI Growth Manager"
4. Select authentication methods:
   - ✅ Email
   - ✅ Google
   - ✅ LinkedIn (optional for now)
5. After creation, go to "API Keys" tab
6. Copy the Publishable Key (starts with pk_test_)
7. Copy the Secret Key (starts with sk_test_)
8. Create a `.env.local` file in the frontend directory
9. Paste the keys into `.env.local`

## Testing Authentication

Once you've added the keys to `.env.local`:

```bash
cd frontend
npm run dev
```

Visit http://localhost:3000 and:
- Click "Get Started" or "Sign Up"
- Create a test account
- Verify you're redirected to /onboarding
- Complete onboarding
- Verify you're redirected to /dashboard
- Test sign out and sign in again

## Next Steps After Auth Works

1. Set up backend API authentication (verify Clerk JWT tokens)
2. Create database schema for users and businesses
3. Implement business onboarding flow (save to database)
4. Build AI strategy generation feature
