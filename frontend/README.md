# Trend Intelligence Dashboard - Frontend

A modern React + Vite + TypeScript + Tailwind CSS frontend application for Mark Edwards Apparel's fashion trend intelligence platform.

## Features

- **Real-time Trend Tracking**: Monitor fashion trends across Instagram, TikTok, SHEIN, Fashion Nova, and more
- **AI-Powered Analysis**: Submit URLs for automatic trend analysis including category, colors, style tags, and engagement metrics
- **Mood Board Curation**: Create and manage thematic collections of trends
- **Monitoring Center**: Set up automated trend tracking with customizable targets
- **Analytics Dashboard**: Visualize trend data with charts and insights
- **Responsive Design**: Fully responsive mobile-first design with modern UI

## Tech Stack

- **React 18**: UI framework
- **Vite 5**: Build tool and dev server
- **TypeScript**: Type-safe development
- **Tailwind CSS 3**: Utility-first styling
- **React Router v6**: Client-side routing
- **Recharts**: Data visualization
- **Axios**: HTTP client
- **Lucide React**: Icon library

## Project Structure

```
frontend/
├── src/
│   ├── api/                 # API client functions
│   │   ├── client.ts       # Axios configuration
│   │   ├── trends.ts       # Trend endpoints
│   │   ├── moodboards.ts   # Mood board endpoints
│   │   ├── monitoring.ts   # Monitoring endpoints
│   │   └── dashboard.ts    # Dashboard endpoints
│   ├── components/          # Reusable components
│   │   ├── Layout.tsx      # Main layout with sidebar
│   │   ├── TrendCard.tsx   # Trend card component
│   │   └── TrendScoreBadge.tsx  # Score visualization
│   ├── hooks/              # Custom React hooks
│   │   ├── useTrends.ts    # Trends data fetching
│   │   └── useDashboard.ts # Dashboard data fetching
│   ├── pages/              # Page components
│   │   ├── Dashboard.tsx        # Main dashboard
│   │   ├── SubmitTrend.tsx     # Trend submission
│   │   ├── TrendDetail.tsx     # Detailed trend view
│   │   ├── MoodBoards.tsx      # Mood board list
│   │   ├── MoodBoardDetail.tsx # Single mood board
│   │   ├── MonitoringCenter.tsx # Monitoring management
│   │   └── Analytics.tsx       # Analytics dashboard
│   ├── types/              # TypeScript interfaces
│   │   └── index.ts        # All type definitions
│   ├── App.tsx            # Main app routing
│   ├── main.tsx           # React entry point
│   └── index.css          # Global styles
├── index.html             # HTML template
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript config
├── tailwind.config.js     # Tailwind configuration
├── postcss.config.js      # PostCSS configuration
└── package.json           # Dependencies

```

## Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn

### Installation

```bash
# Install dependencies
npm install

# or with yarn
yarn install
```

### Development

```bash
# Start dev server (http://localhost:5173)
npm run dev

# or with yarn
yarn dev
```

The development server will proxy API requests to `http://localhost:8000/api`.

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Key Components

### Pages

- **Dashboard**: Overview of all trends with filtering and sorting
- **Submit Trend**: URL submission form with AI analysis results
- **Trend Detail**: Detailed view with engagement metrics and recommendations
- **Mood Boards**: Create and manage thematic collections
- **Monitoring Center**: Set up automated trend tracking
- **Analytics**: Charts and insights on trend data

### Components

- **Layout**: Responsive sidebar navigation and header
- **TrendCard**: Displays trend with image, metadata, and actions
- **TrendScoreBadge**: Visual score indicator with emoji and bar

### Hooks

- **useTrends**: Fetches and caches trend data
- **useDashboard**: Fetches dashboard summary data

## Design System

### Colors

- **Primary**: Pink tones (#F472B6, #EC4899, #DB2777)
- **Accent**: Dark grays (#1F2937, #111827)
- **Semantic**: Green (success), Red (error), Orange (warning)

### Typography

- **Display**: Poppins (headings)
- **Body**: Inter (content)

### Components

- Buttons: Primary, Secondary, Ghost variants
- Cards: Elevation and hover effects
- Badges: Colored variants
- Inputs: Focused states with pink accent

## Mock Data

All pages include realistic mock data so the app displays properly without a backend:

- Dashboard: 6 trending items with mock engagement
- Submit Trend: AI analysis results on successful submission
- Mood Boards: 4 sample collections
- Monitoring Center: 5 tracking targets across platforms
- Analytics: Chart data and metrics

## API Integration

The app is configured to work with a backend API. To connect:

1. Ensure backend is running on `http://localhost:8000`
2. Implement the endpoints defined in `/src/api/`
3. Remove mock data fallbacks when ready

### API Endpoints Expected

```
POST   /api/trends/submit           - Submit new trend
GET    /api/trends/daily            - Get trends
GET    /api/trends/{id}             - Get trend detail
POST   /api/trends/{id}/analyze     - Re-analyze trend
GET    /api/trends/metrics/{id}     - Get engagement metrics

GET    /api/moodboards              - Get all mood boards
GET    /api/moodboards/{id}         - Get mood board
POST   /api/moodboards              - Create mood board
PUT    /api/moodboards/{id}         - Update mood board
DELETE /api/moodboards/{id}         - Delete mood board
POST   /api/moodboards/{id}/items   - Add item
DELETE /api/moodboards/{id}/items/{trendId} - Remove item

GET    /api/monitoring              - Get targets
POST   /api/monitoring              - Create target
PATCH  /api/monitoring/{id}         - Toggle target

GET    /api/dashboard/summary       - Get dashboard data
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance Optimization

- Code splitting with React Router
- Image optimization with lazy loading
- CSS tree-shaking with Tailwind
- Build optimization with Vite

## Responsive Breakpoints

- Mobile: 320px - 640px
- Tablet: 641px - 1024px (md)
- Desktop: 1025px+ (lg)

## Accessibility

- Semantic HTML structure
- ARIA labels where needed
- Keyboard navigation support
- Color contrast compliance

## Future Enhancements

- [ ] User authentication
- [ ] Real-time WebSocket updates
- [ ] Image uploading and cropping
- [ ] Trend sharing and exporting
- [ ] Dark mode toggle
- [ ] Advanced filtering and search
- [ ] Trend predictions
- [ ] Team collaboration features

## License

Proprietary - Mark Edwards Apparel

## Support

For issues or questions, contact the development team.
