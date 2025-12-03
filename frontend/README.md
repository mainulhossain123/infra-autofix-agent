# Auto-Remediation Dashboard - Frontend

Modern React dashboard for the Auto-Remediation Platform.

## 🚀 Quick Start

### Development Mode

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Access at http://localhost:3000
```

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## 📦 Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **Recharts** - Charts and data visualization
- **Lucide React** - Icon library
- **date-fns** - Date formatting utilities

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── Layout.jsx
│   │   ├── Navbar.jsx
│   │   └── Sidebar.jsx
│   ├── pages/           # Page components
│   │   ├── Dashboard.jsx
│   │   ├── IncidentsPage.jsx
│   │   ├── RemediationPage.jsx
│   │   ├── ManualControlPage.jsx
│   │   └── ConfigPage.jsx
│   ├── services/        # API services
│   │   └── api.js
│   ├── utils/          # Utility functions
│   │   └── formatters.js
│   ├── App.jsx         # Main app component
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles
├── public/             # Static assets
├── index.html          # HTML template
├── vite.config.js      # Vite configuration
├── tailwind.config.js  # Tailwind configuration
└── package.json        # Dependencies
```

## 🎨 Features

### Dashboard
- Real-time health monitoring
- System metrics (CPU, Memory, Errors)
- Interactive charts
- Auto-refresh every 5 seconds

### Incidents
- Incident list with filtering
- Status badges (Active/Resolved)
- Severity indicators
- Pagination support
- Detailed incident view

### Remediation History
- Action history table
- Success/failure indicators
- Execution time tracking
- Filter by action type

### Manual Control
- Trigger remediation actions
- Restart containers
- Start replica containers
- Confirmation dialogs
- Real-time feedback

### Configuration
- Update thresholds
- Circuit breaker settings
- Form validation
- Save confirmation

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```bash
VITE_API_URL=http://localhost:5000
```

### API Proxy

The Vite dev server proxies API requests to the backend:

```javascript
// vite.config.js
proxy: {
  '/api': {
    target: 'http://app:5000',
    changeOrigin: true,
  }
}
```

## 🎨 Styling

### Tailwind CSS

Custom color palette defined in `tailwind.config.js`:

- **Primary** - Blue shades for main actions
- **Success** - Green for successful operations
- **Warning** - Yellow for warnings
- **Danger** - Red for errors and critical items

### Custom Classes

Utility classes defined in `index.css`:

- `.card` - Card container
- `.btn` - Button base
- `.btn-primary`, `.btn-success`, etc. - Button variants
- `.badge` - Status badge
- `.input` - Form input
- `.table` - Table styles

## 📱 Responsive Design

- Mobile-first approach
- Responsive navigation
- Collapsible sidebar
- Touch-friendly controls

## 🔗 API Integration

All API calls are centralized in `src/services/api.js`:

```javascript
import { getHealth, getIncidents, triggerManualRemediation } from './services/api';

// Example usage
const health = await getHealth();
const incidents = await getIncidents({ status: 'ACTIVE' });
await triggerManualRemediation({ action: 'restart_container', target: 'ar_app' });
```

## 🧪 Development

### Hot Module Replacement

Vite provides instant HMR for fast development:

```bash
npm run dev
```

### Linting

```bash
npm run lint
```

## 📦 Building for Production

```bash
# Build optimized production bundle
npm run build

# Output: dist/
```

The build is optimized with:
- Code splitting
- Tree shaking
- Minification
- Asset optimization

## 🐳 Docker Integration

The frontend will be containerized with Docker:

```dockerfile
# Development
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
```

## 🚀 Deployment

The dashboard connects to the backend API endpoints:

- **Health**: `GET /health`
- **Metrics**: `GET /api/metrics`
- **Incidents**: `GET /api/incidents`
- **Remediation**: `GET /api/remediation/history`
- **Config**: `GET /api/config`

Make sure the backend is running on port 5000.

## 📄 License

Part of the Auto-Remediation Platform project.
