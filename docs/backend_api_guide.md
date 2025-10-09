# Backend API Integration Guide

## 🚀 Quick Start

### 1. Start Backend Services

```bash
# From project root
docker-compose up -d

# Check services are running
docker-compose ps
```

### 2. Initialize Database

```bash
chmod +x scripts/init_db.sh
./scripts/init_db.sh
```

This will:
- Create the PostgreSQL database
- Install Python dependencies
- Generate Alembic migrations
- Create all tables (users, businesses, etc.)

### 3. Access API Documentation

Visit: http://localhost:8000/docs

You'll see:
- Interactive Swagger UI
- All available endpoints
- Request/response schemas
- Try-it-out functionality

---

## 📋 Available API Endpoints

### Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <clerk_jwt_token>
```

### Users

**POST /api/v1/users/**
- Create a new user (called after Clerk signup)
- Body: `{"clerk_id": "user_xxx", "email": "user@example.com"}`

**GET /api/v1/users/me**
- Get current authenticated user's profile
- Requires: Bearer token

**GET /api/v1/users/{user_id}**
- Get user by ID
- Requires: Bearer token (own profile only)

### Businesses

**POST /api/v1/businesses/**
- Create a business (from onboarding)
- Body: `{"name": "...", "description": "...", "target_audience": "...", "marketing_goals": "..."}`
- Requires: Bearer token

**GET /api/v1/businesses/**
- Get all businesses for current user
- Requires: Bearer token

**GET /api/v1/businesses/{business_id}**
- Get specific business
- Requires: Bearer token

**PUT /api/v1/businesses/{business_id}**
- Update business details
- Requires: Bearer token

**DELETE /api/v1/businesses/{business_id}**
- Delete a business
- Requires: Bearer token

---

## 🔐 Frontend Integration

### 1. Get Clerk JWT Token

In your Next.js components:

```tsx
import { useAuth } from '@clerk/nextjs';

export default function YourComponent() {
  const { getToken } = useAuth();
  
  const callAPI = async () => {
    const token = await getToken();
    
    const response = await fetch('http://localhost:8000/api/v1/businesses', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return response.json();
  };
}
```

### 2. Create API Client (Recommended)

Create `frontend/lib/api.ts`:

```typescript
import { auth } from '@clerk/nextjs';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function apiClient(endpoint: string, options: RequestInit = {}) {
  const { getToken } = auth();
  const token = await getToken();
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  
  return response.json();
}

export const api = {
  // Users
  getCurrentUser: () => apiClient('/api/v1/users/me'),
  
  // Businesses
  createBusiness: (data: BusinessCreate) => 
    apiClient('/api/v1/businesses/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  getBusinesses: () => apiClient('/api/v1/businesses/'),
  
  getBusiness: (id: number) => apiClient(`/api/v1/businesses/${id}`),
  
  updateBusiness: (id: number, data: BusinessUpdate) =>
    apiClient(`/api/v1/businesses/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
};
```

### 3. Update Onboarding to Save Data

In `frontend/app/onboarding/page.tsx`:

```typescript
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';

const handleComplete = async () => {
  try {
    await api.createBusiness({
      name: formData.businessName,
      description: formData.businessDescription,
      target_audience: formData.targetAudience,
      marketing_goals: formData.goals,
    });
    
    router.push('/dashboard');
  } catch (error) {
    console.error('Failed to save business:', error);
    // Show error toast
  }
};
```

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    clerk_id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    first_name VARCHAR,
    last_name VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Businesses Table
```sql
CREATE TABLE businesses (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR REFERENCES users(clerk_id),
    name VARCHAR NOT NULL,
    description TEXT,
    target_audience TEXT,
    marketing_goals TEXT,
    industry VARCHAR,
    company_size VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Future Tables
- strategies
- content
- social_accounts
- analytics
- subscriptions

---

## 🧪 Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Create business (with token)
curl -X POST http://localhost:8000/api/v1/businesses/ \
  -H "Authorization: Bearer YOUR_CLERK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Business",
    "description": "We do amazing things",
    "target_audience": "Small business owners",
    "marketing_goals": "Increase brand awareness"
  }'

# Get businesses
curl http://localhost:8000/api/v1/businesses/ \
  -H "Authorization: Bearer YOUR_CLERK_TOKEN"
```

### Using Swagger UI

1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter: `Bearer YOUR_CLERK_TOKEN`
4. Try out endpoints with the UI

---

## ⚠️ Important Notes

1. **JWT Verification**: Currently using basic JWT decode without signature verification. Need to implement proper JWKS verification with Clerk's public keys.

2. **CORS**: Already configured in FastAPI to allow frontend requests from http://localhost:3000

3. **Environment Variables**: Add to `backend/.env`:
   ```
   DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_growth_manager
   CLERK_SECRET_KEY=your_clerk_secret_key
   ```

4. **Error Handling**: All endpoints return proper HTTP status codes:
   - 200: Success
   - 201: Created
   - 400: Bad Request
   - 401: Unauthorized
   - 403: Forbidden
   - 404: Not Found
   - 500: Server Error

---

## 🔄 Next Steps

1. ✅ Create Clerk account and get keys
2. ✅ Test authentication flow in frontend
3. ⏳ Initialize database with migrations
4. ⏳ Create API client in frontend
5. ⏳ Update onboarding to call backend
6. ⏳ Build AI strategy generation endpoint

---

**Generated**: October 9, 2025
**Updated**: Session 4
