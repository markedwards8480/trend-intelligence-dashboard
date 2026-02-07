# Quick Start Guide

## Setup in 3 Steps

### 1. Install Dependencies

```bash
cd /sessions/adoring-trusting-davinci/trend-intelligence-dashboard/frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

Visit `http://localhost:5173` in your browser.

### 3. Explore the App

The app includes realistic mock data on all pages:

- **Dashboard** (`/`): Browse trending fashion items
- **Submit Trend** (`/submit`): Paste a URL to analyze trends
- **Mood Boards** (`/moodboards`): Create style collections
- **Monitoring** (`/monitoring`): Set up trend tracking
- **Analytics** (`/analytics`): View trend insights

## Project Features

### Color Scheme
- Soft Pink (#EC4899) - Primary
- White & Light Gray - Backgrounds
- Dark Gray (#1F2937) - Text & Accents

### Pages Overview

| Page | Purpose | Mock Data |
|------|---------|-----------|
| Dashboard | Browse all trends | 6 trending items |
| Submit Trend | Analyze new URLs | AI analysis results |
| Trend Detail | View trend metrics | Engagement chart |
| Mood Boards | Curate collections | 4 sample boards |
| Monitoring | Track trends | 5 active targets |
| Analytics | View insights | 4+ charts |

### Key Components

- **Layout**: Responsive sidebar + header
- **TrendCard**: Shows trend with score, colors, tags
- **TrendScoreBadge**: Visual trend score (🔥 hot, ⭐ medium, ❄️ cool)

## Development Tips

### Add a New Page

1. Create file in `src/pages/YourPage.tsx`
2. Add route in `src/App.tsx`
3. Add nav link in `src/components/Layout.tsx`

### Add a New API Call

1. Create function in `src/api/yourModule.ts`
2. Create custom hook in `src/hooks/useYourData.ts`
3. Use hook in your page component

### Style Components

- Use Tailwind classes directly
- Custom classes in `src/index.css`
- Extend colors in `tailwind.config.js`

## API Connection (When Ready)

The app expects a backend at `http://localhost:8000/api`. When you have a backend:

1. Update `VITE_API_BASE_URL` in `.env` if needed
2. Remove mock data fallbacks from hooks
3. Test each endpoint

Example API usage:

```typescript
import { getDailyTrends } from '@/api/trends'

const trends = await getDailyTrends({
  category: 'Dresses',
  sort_by: 'score'
})
```

## Build for Production

```bash
npm run build
npm run preview  # Test production build locally
```

Output will be in `dist/` directory.

## Troubleshooting

**Port 5173 in use?**
```bash
npm run dev -- --port 3000
```

**TypeScript errors?**
```bash
# Check types
npx tsc --noEmit
```

**Tailwind not working?**
- Ensure classes match `tailwind.config.js`
- Check `src/index.css` has @tailwind directives

## File Structure Quick Reference

```
src/
  api/          → Backend communication
  components/   → Reusable UI parts
  pages/        → Full page views
  hooks/        → State & data logic
  types/        → TypeScript definitions
  App.tsx       → Routes & main layout
  index.css     → Global styles
```

## Next Steps

1. ✅ Install dependencies: `npm install`
2. ✅ Start dev server: `npm run dev`
3. ✅ Explore pages
4. ⏳ Connect to backend API
5. ⏳ Deploy to production

Enjoy building! 🚀
