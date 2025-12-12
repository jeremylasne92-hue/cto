# Cognisphere Desktop - Review UI Dashboard

A comprehensive Electron React application for studying and monitoring progress with interactive dashboards, card review sessions, quizzes, and mind maps.

## Features

### 📊 Dashboard
- **Statistics Display**: Cards due today, current streak, retention percentage, total study time
- **Interactive Charts**: 
  - Retention rate trends (7-day line chart)
  - Deck distribution (pie chart)
  - Progress tracking with visual indicators
- **Daily Progress**: Visual progress bars for cards reviewed and time spent
- **Quick Actions**: Deck creation, import, and reporting

### 🃏 Review Workspace
- **Card Presentation**: Clean front/back display with readable typography
- **FSRS Grading System**: 
  - Again/Hard/Good/Easy buttons with color coding
  - Keyboard shortcuts (1-4 keys)
  - Space/Enter to reveal answers
- **Timer Integration**: Response time tracking and session duration
- **Progress Tracking**: Visual progress through study queue
- **Offline Support**: Graceful degradation when backend is unavailable
- **Session Management**: Automatic session start/end with statistics

### 🧠 Quiz Viewer
- **Interactive Quizzes**: Multiple choice questions with instant feedback
- **Difficulty Indicators**: Easy/Medium/Hard badges and filtering
- **Results Analysis**: Detailed scoring with explanations
- **Progress Tracking**: Question-by-question progress indication
- **Retake Functionality**: Easy quiz restart and improvement tracking

### 🗺️ Mind Map Viewer
- **Visual Knowledge Representation**: Node-based mind map visualization
- **Interactive Nodes**: Click to expand/collapse children
- **Node Editing**: Double-click to edit node content
- **Zoom Controls**: Pan and zoom for large mind maps
- **Export Functionality**: JSON export for backup and sharing
- **Connection Visualization**: SVG-based lines showing node relationships

### 🎨 Design System
- **Chakra UI Integration**: Accessible, responsive component library
- **Dark Mode Support**: System-aware theme switching
- **Desktop-Optimized Layout**: Responsive design for Electron window
- **Professional Typography**: Inter font family for optimal readability
- **Consistent Color Scheme**: Brand colors with accessibility compliance

## Technology Stack

- **Frontend**: React 18 + TypeScript + Vite
- **UI Framework**: Chakra UI with custom theming
- **State Management**: Zustand with persistence
- **Charts**: Recharts for data visualization
- **Routing**: React Router v6
- **Desktop**: Electron 28
- **Testing**: Vitest + React Testing Library + jsdom
- **Development**: TypeScript strict mode, ESLint

## Architecture

### Client-Side State Management
```typescript
// Zustand store structure
interface AppState {
  // UI State
  darkMode: boolean;
  currentView: 'dashboard' | 'review' | 'quiz' | 'mindmap';
  isOnline: boolean;
  
  // Study Data
  stats: StudyStats | null;
  cards: Card[];
  decks: Deck[];
  studyQueue: Card[];
  
  // Session Management
  currentSession: StudySession | null;
  sessionStartTime: Date | null;
}
```

### API Service Layer
- Mock API service for development
- Fallback mechanisms for offline mode
- Electron API integration for native features
- HTTP client with timeout and error handling

### Component Architecture
- **Layout**: Responsive sidebar navigation with mobile drawer
- **Dashboard**: Grid-based stats display with chart integration
- **ReviewWorkspace**: Card presentation with keyboard shortcuts
- **QuizViewer**: Tabbed interface with results analysis
- **MindMapViewer**: Canvas-based visualization with interaction

## Development Setup

### Prerequisites
- Node.js 18+
- npm or pnpm

### Installation
```bash
# Install dependencies
npm install

# Setup development environment
npm run setup:backend

# Start development servers
npm run dev
```

This starts:
- React development server (port 3000)
- Electron desktop shell
- Mock backend API

### Available Scripts
```bash
# Development
npm run dev                 # Start all services
npm run dev:frontend       # Start React dev server
npm run dev:electron       # Start Electron shell
npm run dev:backend        # Start backend service

# Building
npm run build              # Build all workspaces
npm run build:desktop      # Build Electron app
npm run build:frontend     # Build React app
npm run build:backend      # Build backend

# Testing
npm run test               # Run component tests
npm run test:coverage      # Run tests with coverage
npm run lint               # Lint code
```

## Usage Guide

### Starting a Review Session
1. **Dashboard**: Review today's progress and click "Start Review Session"
2. **Navigation**: Use sidebar to directly access Review workspace
3. **Card Review**: 
   - Press Space or click "Show Answer"
   - Rate your recall with keyboard (1-Again, 2-Hard, 3-Good, 4-Easy)
   - View progress in real-time

### Taking Quizzes
1. Navigate to Quiz tab
2. Select quiz from available options
3. Answer questions sequentially
4. Review detailed results with explanations

### Exploring Mind Maps
1. Select mind map from sidebar
2. Click nodes to expand/collapse branches
3. Use zoom controls for detailed exploration
4. Edit node content by clicking edit icons
5. Export for backup or sharing

### Customization
- **Dark Mode**: Toggle in header or sidebar
- **Deck Selection**: Choose specific decks for focused study
- **Study Goals**: Configure daily targets in dashboard
- **Keyboard Shortcuts**: Customizable in settings (future feature)

## File Structure

```
apps/
├── desktop-shell/          # Electron main process
│   ├── src/
│   │   ├── main.ts        # Main Electron process
│   │   └── preload.ts     # Secure IPC bridge
│   └── package.json
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Main application pages
│   │   ├── store/         # Zustand state management
│   │   ├── services/      # API and external services
│   │   ├── types/         # TypeScript type definitions
│   │   ├── hooks/         # Custom React hooks
│   │   ├── tests/         # Component and integration tests
│   │   ├── App.tsx        # Main application component
│   │   ├── main.tsx       # React entry point
│   │   ├── theme.ts       # Chakra UI theme configuration
│   │   └── index.css      # Global styles
│   └── package.json
services/
└── backend/               # FastAPI backend (future)
```

## Key Features Implementation

### FSRS Algorithm Integration
- Response time tracking for spaced repetition optimization
- Grade-based card scheduling (Again/Hard/Good/Easy)
- Interval calculation for optimal review timing
- Ease factor adjustment based on performance

### Real-time Updates
- Live progress tracking during review sessions
- Automatic session statistics calculation
- Offline mode with local data persistence
- Optimistic UI updates with error handling

### Responsive Design
- Mobile-first approach with progressive enhancement
- Adaptive layouts for different screen sizes
- Touch-friendly interface for tablet usage
- Desktop-optimized keyboard shortcuts

### Performance Optimization
- Lazy loading for chart components
- Virtual scrolling for large card queues
- Memoized components to prevent unnecessary re-renders
- Efficient state updates with Zustand

## Future Enhancements

### Planned Features
- **Deck Synchronization**: Cloud backup and sync across devices
- **Advanced Analytics**: Detailed learning analytics and insights
- **Custom Study Modes**: Interval training, timed challenges
- **Collaborative Features**: Shared decks and study groups
- **AI-Powered Suggestions**: Intelligent card generation and review scheduling

### Technical Improvements
- **Service Worker**: Offline-first functionality
- **WebRTC**: Real-time collaboration features
- **WebGL**: Enhanced 3D visualizations for mind maps
- **Machine Learning**: Predictive analytics for study optimization

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow TypeScript strict mode conventions
- Maintain test coverage above 80%
- Use Chakra UI components for consistency
- Implement proper error boundaries
- Document complex algorithms and business logic
