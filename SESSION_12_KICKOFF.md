# 🚀 SESSION 12 KICKOFF: Image Upload & AI Image Generation

**Date**: October 13, 2025  
**Estimated Duration**: 3-4 hours  
**Priority**: **HIGH** (Required for Instagram)

---

## 🎯 SESSION OBJECTIVES

### Primary Goals
1. ✅ Enable image upload to cloud storage (S3 or Cloudinary)
2. ✅ Implement AI image generation (DALL-E or Stable Diffusion)
3. ✅ Create image library/management system
4. ✅ Integrate images into publish modal
5. ✅ Auto-validate Instagram posts have images

### Why This Session is Critical
**Instagram Requirement**: Instagram posts REQUIRE images. Currently, we only support external URLs, which creates friction for users. This session removes that barrier and enables:
- Direct image upload from user's device
- AI-generated images from text prompts
- Image library for reuse across posts
- Seamless Instagram publishing

---

## 📋 CURRENT STATE

### What We Have
- ✅ Meta (Facebook/Instagram) integration complete
- ✅ Instagram publishing endpoint (`POST /api/v1/publishing/instagram`)
- ✅ Instagram validation (checks for image_url)
- ✅ Warning in UI: "Instagram requires an image"

### Current Limitation
```tsx
// Current Instagram publishing
{
  "business_id": 1,
  "content_text": "Check this out!",
  "content_images": ["https://external-url.com/image.jpg"]  // ❌ User must provide URL
}
```

**Problems**:
- Users must upload to external service first
- No way to generate images with AI
- No image history/library
- Extra steps before posting

### What We're Building
```tsx
// After Session 12
{
  "business_id": 1,
  "content_text": "Check this out!",
  "content_images": [
    "https://our-bucket.s3.amazonaws.com/images/uuid.jpg"  // ✅ Our storage
  ]
}

// OR generate with AI
{
  "prompt": "A modern office with plants and natural light",
  "style": "professional",
  → Returns: "https://our-bucket.s3.amazonaws.com/ai-images/uuid.jpg"
}
```

---

## 🏗️ ARCHITECTURE OVERVIEW

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ ImageUploader│  │ AIImageGen   │  │ ImageLibrary    │   │
│  │ Component    │  │ Component    │  │ Component       │   │
│  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘   │
│         │                  │                    │            │
│         └──────────────────┴────────────────────┘            │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   API Gateway   │
                    └────────┬────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                        BACKEND                               │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Image API Endpoints                     │   │
│  │  POST /api/v1/images/upload                         │   │
│  │  POST /api/v1/images/generate                       │   │
│  │  GET  /api/v1/images/list                           │   │
│  │  DELETE /api/v1/images/{id}                         │   │
│  └────────┬───────────────────────────────┬─────────────┘   │
│           │                               │                 │
│  ┌────────▼──────────┐         ┌─────────▼──────────────┐   │
│  │ ImageStorage      │         │ AIImageGeneration      │   │
│  │ Service           │         │ Service                │   │
│  │ - S3 upload       │         │ - DALL-E API           │   │
│  │ - Cloudinary alt  │         │ - Stable Diffusion     │   │
│  │ - URL generation  │         │ - Prompt optimization  │   │
│  └────────┬──────────┘         └─────────┬──────────────┘   │
│           │                               │                 │
│           └───────────────┬───────────────┘                 │
│                           │                                 │
│                  ┌────────▼────────┐                        │
│                  │  Image Model    │                        │
│                  │  (Database)     │                        │
│                  └─────────────────┘                        │
└──────────────────────────────────────────────────────────────┘
                           │
                ┌──────────▼──────────┐
                │   Cloud Storage     │
                │  - AWS S3           │
                │  - OR Cloudinary    │
                └─────────────────────┘
```

---

## 🗄️ DATABASE SCHEMA

### New Table: `images`

```sql
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    business_id INTEGER NOT NULL REFERENCES businesses(id),
    
    -- Image metadata
    filename VARCHAR NOT NULL,
    original_filename VARCHAR,
    file_size INTEGER,  -- bytes
    mime_type VARCHAR,  -- image/jpeg, image/png, etc.
    width INTEGER,
    height INTEGER,
    
    -- Storage
    storage_provider VARCHAR NOT NULL,  -- 's3', 'cloudinary'
    storage_url TEXT NOT NULL,  -- Full URL to image
    storage_key TEXT,  -- S3 key or Cloudinary public_id
    
    -- AI Generation (if applicable)
    is_ai_generated BOOLEAN DEFAULT FALSE,
    ai_prompt TEXT,  -- Original prompt if AI-generated
    ai_model VARCHAR,  -- 'dall-e-3', 'stable-diffusion', etc.
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 0,  -- How many posts used this image
    last_used_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_business_images (business_id),
    INDEX idx_created_at (created_at DESC)
);
```

### Sample Record

```json
{
  "id": 1,
  "business_id": 1,
  "filename": "sunset-beach-20251013.jpg",
  "original_filename": "IMG_1234.jpg",
  "file_size": 2457600,
  "mime_type": "image/jpeg",
  "width": 1920,
  "height": 1080,
  "storage_provider": "s3",
  "storage_url": "https://aigrowth-images.s3.amazonaws.com/1/sunset-beach-20251013.jpg",
  "storage_key": "1/sunset-beach-20251013.jpg",
  "is_ai_generated": false,
  "ai_prompt": null,
  "ai_model": null,
  "usage_count": 3,
  "last_used_at": "2025-10-13T14:30:00Z",
  "created_at": "2025-10-13T10:00:00Z"
}
```

---

## 📤 IMAGE UPLOAD FLOW

### Option 1: AWS S3 (Recommended for Production)

**Pros**:
- Industry standard
- Unlimited storage
- $0.023/GB/month
- Fast CDN via CloudFront
- Fine-grained permissions

**Setup Required**:
```bash
# Environment variables
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=aigrowth-images
AWS_S3_REGION=us-east-1
```

**Upload Flow**:
```python
# 1. Receive file from frontend
file = await request.file()

# 2. Validate (size, type)
if file.size > 10_000_000:  # 10MB limit
    raise HTTPException(400, "File too large")

# 3. Generate unique filename
filename = f"{business_id}/{uuid.uuid4()}-{file.filename}"

# 4. Upload to S3
s3_client.upload_fileobj(
    file.file,
    bucket='aigrowth-images',
    key=filename,
    ExtraArgs={'ContentType': file.content_type}
)

# 5. Generate public URL
url = f"https://{bucket}.s3.amazonaws.com/{filename}"

# 6. Save to database
image = Image(
    business_id=business_id,
    filename=filename,
    storage_url=url,
    storage_provider='s3'
)
```

### Option 2: Cloudinary (Alternative)

**Pros**:
- Built-in image transformations
- Auto-optimization
- Free tier: 25GB storage
- Easier setup

**Setup Required**:
```bash
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

**Upload Flow**:
```python
import cloudinary
import cloudinary.uploader

result = cloudinary.uploader.upload(
    file.file,
    folder=f"business_{business_id}",
    resource_type="image"
)

url = result['secure_url']
public_id = result['public_id']
```

### Decision: Start with S3
- More industry standard
- Better for production scale
- Lower long-term costs
- Cloudinary can be added later as alternative

---

## 🤖 AI IMAGE GENERATION

### Option 1: OpenAI DALL-E 3 (Recommended)

**Pros**:
- Best quality
- 1024x1024, 1024x1792, 1792x1024 sizes
- Natural language prompts
- HD quality option

**Cons**:
- $0.040 per image (standard)
- $0.080 per image (HD)

**API Usage**:
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

response = await client.images.generate(
    model="dall-e-3",
    prompt="A professional office with modern furniture and plants",
    size="1024x1024",
    quality="standard",  # or "hd"
    n=1
)

image_url = response.data[0].url  # Temporary URL
# Download and save to S3
```

### Option 2: Stable Diffusion (Alternative)

**Pros**:
- Much cheaper (~$0.002 per image)
- More control over style
- Can self-host

**Cons**:
- More complex setup
- Requires prompt engineering
- Quality varies

**API Options**:
- Stability AI API
- Replicate API
- Self-hosted (requires GPU)

### Decision: Start with DALL-E 3
- Better quality out of box
- Simpler integration
- More reliable results
- Cost acceptable for MVP (~$4 for 100 images)

---

## 🔌 API ENDPOINTS

### 1. **POST `/api/v1/images/upload`**
Upload image from user's device

**Request** (multipart/form-data):
```http
POST /api/v1/images/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

business_id: 1
file: <binary>
```

**Response**:
```json
{
  "success": true,
  "image": {
    "id": 1,
    "filename": "1/uuid-photo.jpg",
    "storage_url": "https://bucket.s3.amazonaws.com/1/uuid-photo.jpg",
    "file_size": 2457600,
    "mime_type": "image/jpeg",
    "width": 1920,
    "height": 1080,
    "created_at": "2025-10-13T10:00:00Z"
  }
}
```

**Validation**:
- Max file size: 10MB
- Allowed types: JPEG, PNG, GIF, WebP
- Image dimensions: min 400x400, max 4096x4096

### 2. **POST `/api/v1/images/generate`**
Generate image with AI from text prompt

**Request**:
```json
{
  "business_id": 1,
  "prompt": "A modern office with plants and natural light, professional photography",
  "size": "1024x1024",
  "quality": "standard",
  "style": "professional"  // optional preset
}
```

**Response**:
```json
{
  "success": true,
  "image": {
    "id": 2,
    "filename": "1/ai-uuid.jpg",
    "storage_url": "https://bucket.s3.amazonaws.com/1/ai-uuid.jpg",
    "is_ai_generated": true,
    "ai_prompt": "A modern office with plants...",
    "ai_model": "dall-e-3",
    "width": 1024,
    "height": 1024,
    "created_at": "2025-10-13T10:05:00Z"
  }
}
```

**Prompt Enhancement**:
```python
def enhance_prompt(prompt: str, style: str = None) -> str:
    """Add style-specific enhancements to user prompt"""
    
    style_templates = {
        "professional": "{prompt}, professional photography, high quality, well-lit",
        "creative": "{prompt}, artistic, creative composition, vibrant colors",
        "minimalist": "{prompt}, minimalist design, clean, simple, modern",
        "vintage": "{prompt}, vintage style, retro aesthetic, film grain"
    }
    
    if style and style in style_templates:
        return style_templates[style].format(prompt=prompt)
    
    return prompt
```

### 3. **GET `/api/v1/images/list`**
List all images for a business

**Query Parameters**:
- `business_id` (required)
- `page` (default: 1)
- `limit` (default: 20, max: 100)
- `sort` (default: created_at desc)
- `filter` (optional: ai_generated, uploaded)

**Response**:
```json
{
  "images": [
    {
      "id": 2,
      "filename": "ai-sunset.jpg",
      "storage_url": "https://...",
      "is_ai_generated": true,
      "usage_count": 1,
      "created_at": "2025-10-13T10:05:00Z"
    },
    {
      "id": 1,
      "filename": "photo.jpg",
      "storage_url": "https://...",
      "is_ai_generated": false,
      "usage_count": 3,
      "created_at": "2025-10-13T10:00:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "pages": 1
}
```

### 4. **DELETE `/api/v1/images/{id}`**
Delete an image

**Response**:
```json
{
  "success": true,
  "message": "Image deleted successfully"
}
```

**Actions**:
1. Delete from S3/Cloudinary
2. Delete database record
3. Check if used in published posts (warn user?)

### 5. **GET `/api/v1/images/{id}`**
Get image details

**Response**:
```json
{
  "id": 1,
  "filename": "photo.jpg",
  "storage_url": "https://...",
  "file_size": 2457600,
  "mime_type": "image/jpeg",
  "width": 1920,
  "height": 1080,
  "usage_count": 3,
  "last_used_at": "2025-10-13T14:30:00Z",
  "created_at": "2025-10-13T10:00:00Z"
}
```

---

## 🎨 FRONTEND COMPONENTS

### 1. **ImageUploader Component**

**Location**: `frontend/app/dashboard/images/components/ImageUploader.tsx`

**Features**:
- Drag & drop zone
- File picker button
- Image preview before upload
- Progress bar during upload
- Validation (size, type)
- Success/error states

**UI Design**:
```tsx
<div className="border-2 border-dashed border-gray-300 rounded-lg p-8">
  {/* Drag & Drop Zone */}
  <div className="text-center">
    <Upload className="mx-auto h-12 w-12 text-gray-400" />
    <p className="mt-2 text-sm text-gray-600">
      Drag and drop your image here, or click to browse
    </p>
    <p className="mt-1 text-xs text-gray-500">
      PNG, JPG, GIF up to 10MB
    </p>
  </div>
  
  {/* Preview */}
  {preview && (
    <div className="mt-4">
      <img src={preview} className="max-h-48 mx-auto rounded" />
      <button onClick={handleUpload}>Upload</button>
    </div>
  )}
  
  {/* Progress */}
  {uploading && (
    <div className="mt-4">
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div className="bg-blue-600 h-2 rounded-full" style={{width: `${progress}%`}} />
      </div>
    </div>
  )}
</div>
```

### 2. **AIImageGenerator Component**

**Location**: `frontend/app/dashboard/images/components/AIImageGenerator.tsx`

**Features**:
- Text prompt input
- Style selector (professional, creative, minimalist, vintage)
- Size selector (1024x1024, 1024x1792, 1792x1024)
- Quality toggle (standard/HD)
- Generate button
- Loading state (15-30 sec generation time)
- Preview generated image

**UI Design**:
```tsx
<div className="space-y-4">
  {/* Prompt Input */}
  <div>
    <label>Describe your image</label>
    <textarea 
      placeholder="A modern office with plants and natural light..."
      rows={3}
    />
  </div>
  
  {/* Style Presets */}
  <div>
    <label>Style</label>
    <div className="grid grid-cols-4 gap-2">
      {['professional', 'creative', 'minimalist', 'vintage'].map(style => (
        <button 
          key={style}
          className={selected === style ? 'bg-blue-600 text-white' : 'bg-gray-100'}
        >
          {style}
        </button>
      ))}
    </div>
  </div>
  
  {/* Size Selector */}
  <div>
    <label>Size</label>
    <select>
      <option value="1024x1024">Square (1024x1024)</option>
      <option value="1024x1792">Portrait (1024x1792)</option>
      <option value="1792x1024">Landscape (1792x1024)</option>
    </select>
  </div>
  
  {/* Generate Button */}
  <button 
    onClick={handleGenerate}
    disabled={generating}
    className="w-full bg-gradient-to-r from-purple-600 to-pink-600"
  >
    {generating ? (
      <>
        <Loader2 className="animate-spin" />
        Generating... (~20 seconds)
      </>
    ) : (
      <>
        <Sparkles />
        Generate with AI
      </>
    )}
  </button>
  
  {/* Cost Notice */}
  <p className="text-xs text-gray-500">
    💡 Each generation costs ~$0.04 (standard) or $0.08 (HD)
  </p>
</div>
```

### 3. **ImageLibrary Component**

**Location**: `frontend/app/dashboard/images/components/ImageLibrary.tsx`

**Features**:
- Grid view of all images
- Filter (All, Uploaded, AI Generated)
- Sort (Newest, Oldest, Most Used)
- Search by filename
- Image cards with metadata
- Delete button
- Select button (for publish modal)

**UI Design**:
```tsx
<div className="space-y-4">
  {/* Filters & Search */}
  <div className="flex gap-4">
    <input 
      type="text" 
      placeholder="Search images..."
      className="flex-1"
    />
    <select onChange={handleFilter}>
      <option value="all">All Images</option>
      <option value="uploaded">Uploaded</option>
      <option value="ai">AI Generated</option>
    </select>
  </div>
  
  {/* Image Grid */}
  <div className="grid grid-cols-3 gap-4">
    {images.map(image => (
      <div key={image.id} className="border rounded-lg overflow-hidden">
        <img src={image.storage_url} className="w-full h-48 object-cover" />
        <div className="p-3">
          <p className="text-sm font-medium truncate">{image.filename}</p>
          <p className="text-xs text-gray-500">
            {image.is_ai_generated ? '🤖 AI Generated' : '📤 Uploaded'}
          </p>
          <p className="text-xs text-gray-500">
            Used {image.usage_count} times
          </p>
          <div className="mt-2 flex gap-2">
            <button onClick={() => onSelect(image)} className="flex-1 bg-blue-600 text-white">
              Select
            </button>
            <button onClick={() => handleDelete(image.id)} className="text-red-600">
              <Trash2 />
            </button>
          </div>
        </div>
      </div>
    ))}
  </div>
</div>
```

### 4. **Update PublishContentModal**

**Add Image Picker Section**:
```tsx
{/* Image Selection */}
<div>
  <label className="block text-sm font-medium text-gray-700 mb-2">
    Images {selectedPlatform === 'instagram' && (
      <span className="text-red-600">*</span>
    )}
  </label>
  
  <div className="space-y-3">
    {/* Selected Images */}
    {selectedImages.length > 0 && (
      <div className="grid grid-cols-4 gap-2">
        {selectedImages.map(image => (
          <div key={image.id} className="relative">
            <img src={image.storage_url} className="w-full h-24 object-cover rounded" />
            <button 
              onClick={() => removeImage(image.id)}
              className="absolute top-1 right-1 bg-red-600 text-white rounded-full p-1"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    )}
    
    {/* Add Image Buttons */}
    <div className="flex gap-2">
      <button 
        onClick={() => setShowImageLibrary(true)}
        className="flex-1 border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-blue-600"
      >
        <ImageIcon className="mx-auto h-6 w-6 text-gray-400" />
        <span className="block mt-2 text-sm text-gray-600">Choose from Library</span>
      </button>
      
      <button 
        onClick={() => setShowUploader(true)}
        className="flex-1 border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-blue-600"
      >
        <Upload className="mx-auto h-6 w-6 text-gray-400" />
        <span className="block mt-2 text-sm text-gray-600">Upload New</span>
      </button>
      
      <button 
        onClick={() => setShowAIGenerator(true)}
        className="flex-1 border-2 border-dashed border-purple-300 rounded-lg p-4 hover:border-purple-600"
      >
        <Sparkles className="mx-auto h-6 w-6 text-purple-400" />
        <span className="block mt-2 text-sm text-purple-600">Generate with AI</span>
      </button>
    </div>
    
    {/* Instagram Validation */}
    {selectedPlatform === 'instagram' && selectedImages.length === 0 && (
      <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 rounded-md px-3 py-2">
        <AlertCircle className="w-4 h-4" />
        <span>Instagram requires at least one image</span>
      </div>
    )}
  </div>
</div>

{/* Modals */}
{showImageLibrary && (
  <Modal onClose={() => setShowImageLibrary(false)}>
    <ImageLibrary 
      businessId={businessId}
      onSelect={(image) => {
        addImage(image);
        setShowImageLibrary(false);
      }}
    />
  </Modal>
)}
```

---

## 🔧 IMPLEMENTATION PHASES

### Phase 1: Image Storage Service (45 min)

**Tasks**:
1. Create `backend/app/services/image_storage.py`
2. Set up AWS S3 client
3. Implement upload function
4. Implement URL generation
5. Add file validation
6. Add error handling

**Key Functions**:
```python
async def upload_image(
    file: UploadFile,
    business_id: int,
    folder: str = "uploads"
) -> dict:
    """Upload image to S3 and return metadata"""
    
async def delete_image(storage_key: str) -> bool:
    """Delete image from S3"""
    
def generate_signed_url(storage_key: str, expires_in: int = 3600) -> str:
    """Generate temporary signed URL (optional)"""
```

### Phase 2: AI Image Generation Service (30 min)

**Tasks**:
1. Create `backend/app/services/ai_image_gen.py`
2. Set up OpenAI client
3. Implement DALL-E 3 integration
4. Add prompt enhancement
5. Download & save to S3
6. Add error handling

**Key Functions**:
```python
async def generate_image(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "standard",
    style: str = None
) -> dict:
    """Generate image with DALL-E 3"""
    
def enhance_prompt(prompt: str, style: str) -> str:
    """Add style enhancements to prompt"""
```

### Phase 3: Image Model & Database (20 min)

**Tasks**:
1. Create `backend/app/models/image.py`
2. Create database migration
3. Run migration
4. Create Pydantic schemas in `backend/app/schemas/image.py`

### Phase 4: Image API Endpoints (40 min)

**Tasks**:
1. Create `backend/app/api/images.py`
2. Implement 5 endpoints (upload, generate, list, get, delete)
3. Add authentication
4. Add validation
5. Test with curl

### Phase 5: Frontend Components (60 min)

**Tasks**:
1. Create `ImageUploader.tsx` (20 min)
2. Create `AIImageGenerator.tsx` (20 min)
3. Create `ImageLibrary.tsx` (20 min)

### Phase 6: Publish Modal Integration (30 min)

**Tasks**:
1. Add image picker to `PublishContentModal.tsx`
2. Update validation for Instagram
3. Add image preview
4. Update payload to include image URLs

### Phase 7: Testing & Documentation (45 min)

**Tasks**:
1. Test image upload
2. Test AI generation
3. Test Instagram posting with image
4. Create `SESSION_12_COMPLETE.md`
5. Update `ROADMAP.md`

**Total Estimated Time**: ~4 hours

---

## 🧪 TESTING SCENARIOS

### 1. Image Upload
- [ ] Upload JPEG (< 10MB)
- [ ] Upload PNG (< 10MB)
- [ ] Upload GIF (< 10MB)
- [ ] Reject file > 10MB
- [ ] Reject non-image file
- [ ] Handle network error
- [ ] Verify S3 storage
- [ ] Verify database record

### 2. AI Image Generation
- [ ] Generate with simple prompt
- [ ] Generate with style preset
- [ ] Generate 1024x1024 (square)
- [ ] Generate 1024x1792 (portrait)
- [ ] Generate 1792x1024 (landscape)
- [ ] Generate HD quality
- [ ] Handle API error
- [ ] Verify S3 storage
- [ ] Verify database record with AI metadata

### 3. Image Library
- [ ] List all images
- [ ] Filter by uploaded
- [ ] Filter by AI generated
- [ ] Search by filename
- [ ] Sort by newest/oldest/usage
- [ ] Delete image
- [ ] Select image for post

### 4. Instagram Publishing
- [ ] Publish post with uploaded image ✅
- [ ] Publish post with AI image ✅
- [ ] Reject post without image ❌
- [ ] Show validation error
- [ ] Verify image in Instagram post

---

## 💰 COST ANALYSIS

### AWS S3 Storage
- **Storage**: $0.023/GB/month
- **PUT requests**: $0.005 per 1,000 requests
- **GET requests**: $0.0004 per 1,000 requests

**Example Monthly Cost (1000 users)**:
- 10 images/user = 10,000 images
- Avg 1MB/image = 10GB storage
- Storage: $0.23/month
- Uploads: $0.05/month
- Downloads: ~$0.01/month
- **Total: ~$0.30/month** 💚

### DALL-E 3 API
- **Standard quality**: $0.040 per image
- **HD quality**: $0.080 per image

**Example Monthly Cost (1000 users)**:
- 5 AI images/user/month = 5,000 images
- Standard quality: $200/month
- **Can be passed to users or limited** 💡

### Recommendations
1. **Free tier for users**: 3 AI images/month included
2. **Charge for additional**: $0.10 per image (50% markup)
3. **S3 storage**: Free (low cost absorbed)
4. **Alternative**: Use Stable Diffusion (~$0.002/image)

---

## 🔐 SECURITY CONSIDERATIONS

### File Upload Security

**Validation**:
```python
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_image(file: UploadFile) -> bool:
    # Check extension
    ext = file.filename.split('.')[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Invalid file type")
    
    # Check size
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)  # Reset
    if size > MAX_FILE_SIZE:
        raise ValueError("File too large")
    
    # Verify it's actually an image
    try:
        from PIL import Image
        img = Image.open(file.file)
        img.verify()
        file.file.seek(0)  # Reset after verify
    except:
        raise ValueError("Invalid image file")
    
    return True
```

**S3 Permissions**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::aigrowth-images/*"
    }
  ]
}
```

**CORS Configuration**:
```xml
<CORSConfiguration>
  <CORSRule>
    <AllowedOrigin>https://yourdomain.com</AllowedOrigin>
    <AllowedMethod>GET</AllowedMethod>
    <AllowedMethod>PUT</AllowedMethod>
    <AllowedMethod>POST</AllowedMethod>
    <AllowedMethod>DELETE</AllowedMethod>
    <AllowedHeader>*</AllowedHeader>
  </CORSRule>
</CORSConfiguration>
```

### AI Generation Security

**Rate Limiting**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/images/generate")
@limiter.limit("5/minute")  # Max 5 generations per minute
async def generate_image(...):
    ...
```

**Prompt Filtering**:
```python
BLOCKED_WORDS = ['inappropriate', 'violent', 'explicit', ...]

def filter_prompt(prompt: str) -> str:
    """Check for inappropriate content"""
    lower_prompt = prompt.lower()
    for word in BLOCKED_WORDS:
        if word in lower_prompt:
            raise ValueError("Inappropriate prompt detected")
    return prompt
```

---

## 📚 DEPENDENCIES TO INSTALL

### Backend
```bash
# AWS SDK
boto3==1.34.20

# Image processing
Pillow==10.1.0

# OpenAI (for DALL-E)
openai==1.3.7

# Optional: Cloudinary alternative
cloudinary==1.37.0
```

### Frontend
```bash
# Already have most dependencies
# May need:
npm install @uppy/core @uppy/react @uppy/dashboard  # Optional advanced uploader
```

---

## 🎯 SUCCESS CRITERIA

### Backend
- [ ] Image storage service working (S3)
- [ ] AI generation service working (DALL-E 3)
- [ ] 5 API endpoints implemented
- [ ] Database migration applied
- [ ] Image model created
- [ ] All validations working

### Frontend
- [ ] ImageUploader component functional
- [ ] AIImageGenerator component functional
- [ ] ImageLibrary component functional
- [ ] Publish modal integrated
- [ ] Instagram validation working

### Integration
- [ ] Upload → S3 → Database → Library
- [ ] AI Generate → DALL-E → S3 → Database → Library
- [ ] Select from library → Add to post
- [ ] Instagram post with image → Success

---

## 🚀 NEXT SESSION PREVIEW

### Session 13: Automated Scheduled Posting
After completing image support, we'll build:
- Background job scheduler (Celery + Redis)
- Calendar view for scheduling
- Bulk post scheduling
- Timezone support
- Queue management

This will enable users to:
- Schedule posts for optimal times
- Plan content weeks in advance
- Auto-post without manual intervention
- Maintain consistent posting schedule

---

## 📝 NOTES

### Key Decisions
1. **Storage**: AWS S3 (over Cloudinary)
2. **AI Model**: DALL-E 3 (over Stable Diffusion)
3. **Upload Method**: Multipart form data
4. **Image Library**: Full-featured (not just picker)

### Nice-to-Have (Future)
- [ ] Image editing (crop, resize, filters)
- [ ] Bulk upload
- [ ] Image templates
- [ ] Brand kit (logos, colors)
- [ ] Video support
- [ ] GIF support

### Blockers to Watch
- AWS credentials setup
- OpenAI API key
- S3 bucket creation
- CORS configuration

---

## ✅ READY TO START

All planning complete! Ready to implement:

1. ✅ Architecture designed
2. ✅ Database schema planned
3. ✅ API endpoints defined
4. ✅ Components designed
5. ✅ Testing scenarios ready
6. ✅ Security considered
7. ✅ Cost analyzed

**Let's build! 🚀**

---

*Session 12 Kickoff - Image Upload & AI Image Generation*
