# Publishing Components Integration Example

## Overview
This guide shows how to integrate the new publishing components into your content pages.

## Components Created

### 1. PublishNowButton
**Location**: `components/publishing/PublishNowButton.tsx`

**Usage**:
```tsx
import PublishNowButton from '@/components/publishing/PublishNowButton';

<PublishNowButton
  content="Your post content here"
  platforms={['linkedin', 'twitter']}
  businessId={businessId}
  platformParams={{
    facebook: { page_id: "123456" },
    instagram: { instagram_account_id: "789012" }
  }}
  onSuccess={(results) => {
    console.log('Published successfully:', results);
  }}
  onError={(error) => {
    console.error('Publishing failed:', error);
  }}
  variant="primary"  // 'primary' | 'secondary' | 'outline'
  size="md"          // 'sm' | 'md' | 'lg'
/>
```

### 2. SchedulePostModal
**Location**: `components/publishing/SchedulePostModal.tsx`

**Usage**:
```tsx
import { useState } from 'react';
import SchedulePostModal from '@/components/publishing/SchedulePostModal';

const [scheduleModalOpen, setScheduleModalOpen] = useState(false);

<button onClick={() => setScheduleModalOpen(true)}>
  Schedule Post
</button>

<SchedulePostModal
  isOpen={scheduleModalOpen}
  onClose={() => setScheduleModalOpen(false)}
  content="Your post content here"
  platforms={['linkedin']}
  businessId={businessId}
  platformParams={{}}
  onScheduled={(scheduledPostId) => {
    console.log('Post scheduled:', scheduledPostId);
    setScheduleModalOpen(false);
  }}
  onError={(error) => {
    console.error('Scheduling failed:', error);
  }}
/>
```

### 3. ScheduledPostsCalendar (Page)
**Location**: `app/dashboard/scheduled/page.tsx`

This is a full page component that displays:
- Calendar view of scheduled posts
- List view with detailed information
- Cancel scheduled posts functionality

**Navigation**:
Add to your dashboard navigation:
```tsx
<Link href="/dashboard/scheduled">
  <Calendar className="w-5 h-5" />
  Scheduled Posts
</Link>
```

## Integration Example

### Content Generation Page

```tsx
'use client';

import { useState } from 'react';
import PublishNowButton from '@/components/publishing/PublishNowButton';
import SchedulePostModal from '@/components/publishing/SchedulePostModal';

export default function ContentPage() {
  const [generatedContent, setGeneratedContent] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['linkedin']);
  const [businessId, setBusinessId] = useState<number>(1);
  const [scheduleModalOpen, setScheduleModalOpen] = useState(false);

  return (
    <div>
      {/* Content Display */}
      <div className="mb-4">
        <textarea
          value={generatedContent}
          onChange={(e) => setGeneratedContent(e.target.value)}
          className="w-full p-4 border rounded-lg"
          rows={8}
          placeholder="Your content here..."
        />
      </div>

      {/* Platform Selection */}
      <div className="mb-4">
        <label className="block mb-2">Select Platforms:</label>
        <div className="flex gap-2">
          {['linkedin', 'twitter', 'facebook', 'instagram'].map((platform) => (
            <label key={platform} className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={selectedPlatforms.includes(platform)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setSelectedPlatforms([...selectedPlatforms, platform]);
                  } else {
                    setSelectedPlatforms(selectedPlatforms.filter(p => p !== platform));
                  }
                }}
              />
              {platform}
            </label>
          ))}
        </div>
      </div>

      {/* Publishing Actions */}
      <div className="flex gap-3">
        {/* Publish Now */}
        <PublishNowButton
          content={generatedContent}
          platforms={selectedPlatforms as any}
          businessId={businessId}
          onSuccess={(results) => {
            console.log('Published:', results);
            alert(`Published to ${results.length} platforms!`);
          }}
          onError={(error) => {
            console.error('Error:', error);
          }}
        />

        {/* Schedule Post */}
        <button
          onClick={() => setScheduleModalOpen(true)}
          className="px-6 py-2 bg-white border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50"
        >
          Schedule for Later
        </button>
      </div>

      {/* Schedule Modal */}
      <SchedulePostModal
        isOpen={scheduleModalOpen}
        onClose={() => setScheduleModalOpen(false)}
        content={generatedContent}
        platforms={selectedPlatforms as any}
        businessId={businessId}
        onScheduled={(id) => {
          alert(`Post scheduled! ID: ${id}`);
          setScheduleModalOpen(false);
        }}
      />
    </div>
  );
}
```

## API Endpoints Used

### 1. Publish Now
```
POST /api/v2/publish
```

**Request**:
```json
{
  "content": "Post content",
  "platforms": ["linkedin", "twitter"],
  "platform_params": {
    "facebook": { "page_id": "123" }
  }
}
```

**Response**:
```json
{
  "success": true,
  "results": [
    {
      "platform": "linkedin",
      "success": true,
      "post_id": "urn:li:share:123",
      "url": "https://linkedin.com/..."
    }
  ],
  "published_post_ids": [1, 2]
}
```

### 2. Schedule Post
```
POST /api/v2/schedule
```

**Request**:
```json
{
  "content": "Post content",
  "platforms": ["linkedin"],
  "scheduled_for": "2024-01-20T10:00:00Z",
  "platform_params": {}
}
```

**Response**:
```json
{
  "success": true,
  "scheduled_post_id": 123,
  "celery_task_id": "abc-123-def",
  "scheduled_for": "2024-01-20T10:00:00Z"
}
```

### 3. List Scheduled Posts
```
GET /api/v2/scheduled?business_id=1
```

**Response**:
```json
{
  "scheduled_posts": [
    {
      "id": 123,
      "content_text": "Post content",
      "platforms": ["linkedin"],
      "scheduled_for": "2024-01-20T10:00:00Z",
      "status": "pending",
      "celery_task_id": "abc-123"
    }
  ]
}
```

### 4. Cancel Scheduled Post
```
DELETE /api/v2/schedule/{post_id}
```

**Response**:
```json
{
  "success": true,
  "message": "Scheduled post cancelled successfully"
}
```

## Features

### PublishNowButton
- ✅ Immediate publishing to multiple platforms
- ✅ Loading and success states
- ✅ Error handling with user feedback
- ✅ Automatic opening of published posts in new tabs
- ✅ Customizable variants and sizes

### SchedulePostModal
- ✅ Date and time picker for future scheduling
- ✅ Validation (must be future date/time)
- ✅ Platform badges showing where content will be published
- ✅ Content preview
- ✅ Success/error feedback
- ✅ Auto-close on success

### ScheduledPostsCalendar
- ✅ Calendar view with monthly navigation
- ✅ List view with detailed information
- ✅ Cancel scheduled posts functionality
- ✅ Status badges (pending, queued, published)
- ✅ Platform-specific icons and colors
- ✅ Business selector for multi-business accounts

## Styling
All components use Tailwind CSS and match the existing design system:
- **Primary Color**: Blue (#2563EB)
- **Success Color**: Green (#059669)
- **Error Color**: Red (#DC2626)
- **Icons**: Lucide React

## Next Steps

1. **Add to Navigation**:
   ```tsx
   // In dashboard layout
   <Link href="/dashboard/scheduled">Scheduled Posts</Link>
   ```

2. **Update Content Page**:
   - Import PublishNowButton and SchedulePostModal
   - Add buttons next to generated content
   - Wire up with existing state

3. **Add to Strategy Page**:
   - Enable scheduling generated content
   - Show scheduled posts in strategy timeline

4. **Testing**:
   - Test publishing to all platforms
   - Test scheduling with different dates/times
   - Test cancelling scheduled posts
   - Test with multiple businesses

## Error Handling

All components include comprehensive error handling:
- Authentication errors
- Network errors
- Validation errors
- Rate limit errors (429)
- Server errors (500)

Errors are displayed inline and can also trigger callbacks for custom handling.

## Accessibility

- Keyboard navigation supported
- ARIA labels on interactive elements
- Focus management in modals
- Screen reader friendly

## Performance

- Optimistic UI updates
- Automatic retry on transient failures (backend)
- Efficient re-rendering with React hooks
- Minimal API calls with proper caching
