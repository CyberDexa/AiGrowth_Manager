# Screenshots Directory

This directory contains screenshots and visual assets for marketing materials, documentation, and the landing page.

## Screenshot Naming Convention

Please save screenshots with descriptive names:

### Feature Screenshots (for Landing Page):
1. `hero-dashboard.png` - Main dashboard overview
2. `feature-ai-strategy.png` - AI Strategy generation interface
3. `feature-content-creation.png` - Content creation with AI
4. `feature-multi-platform.png` - Multi-platform publishing modal
5. `feature-templates.png` - Content templates page
6. `feature-analytics.png` - Analytics dashboard with charts
7. `feature-posting-times.png` - Posting time recommendations
8. `feature-content-library.png` - Content library page
9. `feature-calendar.png` - Visual scheduling calendar
10. `feature-onboarding.png` - Onboarding checklist with confetti

### Additional Marketing Assets:
- `social-connections.png` - OAuth connection flow
- `platform-preview.png` - Platform preview cards
- `mobile-menu.png` - Mobile navigation
- `error-boundary.png` - Error handling UI (optional)
- `loading-states.png` - Skeleton loaders (optional)

## Screenshot Dimensions

For best results:
- **Desktop screenshots:** 1920x1080 or 2560x1440
- **Mobile screenshots:** 375x812 (iPhone) or 360x800 (Android)
- **Feature highlights:** 1200x800 (landscape) or 800x1200 (portrait)

## How to Capture Screenshots

### Using Browser Dev Tools:
1. Open your app in Chrome/Firefox
2. Press F12 to open DevTools
3. Toggle device toolbar (Ctrl+Shift+M / Cmd+Shift+M)
4. Set viewport size
5. Take screenshot:
   - Chrome: Cmd/Ctrl+Shift+P → "Capture screenshot"
   - Firefox: Right-click → "Take a Screenshot"

### Using macOS:
- **Full screen:** Cmd+Shift+3
- **Selected area:** Cmd+Shift+4
- **Window with shadow:** Cmd+Shift+4, then Space, then click window

### Using Windows:
- **Full screen:** PrtScn or Win+PrtScn
- **Selected area:** Win+Shift+S
- **Snipping Tool:** Search for "Snipping Tool" in Start menu

## Post-Processing (Optional)

For professional-looking screenshots:
1. **Add subtle shadows:** Use Figma, Photoshop, or online tools
2. **Remove sensitive data:** Blur out any personal information
3. **Add device frames:** Use https://shots.so or https://mockuphone.com
4. **Optimize file size:** Use https://tinypng.com or ImageOptim
5. **Convert to WebP:** For better web performance

## Usage in Landing Page

Once screenshots are captured, update:
- `frontend/app/page.tsx` - Landing page features section
- `README.md` - Feature documentation
- `PUBLISHING_README.md` - Publishing instructions

## Example Screenshot Workflow

1. Start your app locally (`npm run dev`)
2. Navigate to each feature
3. Capture screenshot at key moment (e.g., after generating strategy)
4. Save with descriptive name
5. Optimize image size
6. Add to this directory
7. Update landing page and README

## Tips for Great Screenshots

✅ **Do:**
- Use real, compelling data (not lorem ipsum)
- Show the feature in action
- Capture the "aha!" moment
- Use consistent browser/device
- Good lighting (for device photos)

❌ **Don't:**
- Include personal/sensitive data
- Use default/empty states
- Capture loading spinners
- Show browser UI unless necessary
- Use low-resolution images

---

*Last Updated: October 20, 2025*
