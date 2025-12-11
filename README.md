# Learning Platform Desktop

A comprehensive Electron desktop application for intelligent learning through adaptive spaced repetition and AI-powered content ingestion.

## Features

### 🎯 Core Functionality
- **Smart Content Ingestion**: Import from PDFs, websites, videos, and documents with AI-powered processing
- **Interactive Learning**: Flashcards, quizzes, and mind maps for engaging learning experiences  
- **Adaptive Learning**: Personalized spaced repetition algorithm for optimal retention
- **Local AI Processing**: Run language models locally for privacy and offline capability

### 📊 Dashboard & Analytics
- Progress visualization: Cards reviewed today, streak, XP
- Charts: Retention rate, daily review count (last 30 days)
- Upcoming: Due cards count, leech warnings
- Quick actions: Start session, Ingest content, View statistics

### 📚 Content Management
- **Deck Organization**: Create, rename, delete, and manage card decks
- **Content Types**: Support for flashcards, quizzes, and mind maps
- **Import Methods**: File upload, URL paste, video link processing
- **Real-time Progress**: Live progress tracking during content ingestion

### 🎮 Review Interface
- **Interactive Cards**: Front with back reveal (click/keyboard)
- **Grading System**: 4-button grading with keyboard shortcuts (1-4)
- **Session Timer**: Track elapsed time and average card time
- **Progress Tracking**: X/Y cards done with visual progress
- **Streak Management**: Current learning streak tracking

### ⚙️ Settings & Customization
- **Hardware Tier Selection**: Auto-detect or manual override for performance
- **LLM Provider Choice**: Local vs Cloud API options
- **Theme Support**: Light/dark mode with system preference detection
- **Review Preferences**: Session duration and card order customization
- **Data Management**: Export/import functionality for backups

### 🔐 Accessibility & UX
- **WCAG 2.1 AA Compliance**: 4.5:1 contrast ratios, keyboard navigation
- **Keyboard Shortcuts**: Full keyboard navigation support
- **Screen Reader Support**: Proper ARIA labels and announcements
- **Responsive Design**: Optimized for desktop with mobile viewport preparation
- **Micro Animations**: 150ms hover states, 300ms transitions, 500ms emphasis

## Technology Stack

- **Frontend**: React 18, TypeScript-ready
- **Desktop**: Electron 28
- **Styling**: Tailwind CSS with custom design system
- **Animation**: Framer Motion
- **Charts**: Recharts for data visualization
- **State Management**: Zustand with persistence
- **Icons**: Lucide React
- **Build Tool**: Vite for the renderer process
- **Package Manager**: npm

## Project Structure

```
src/
├── main/                 # Electron main process
│   ├── main.js          # Main application entry
│   └── preload.js       # Context isolation bridge
├── renderer/            # React renderer process
│   ├── src/
│   │   ├── components/  # React components
│   │   │   ├── layout/  # Layout components
│   │   │   ├── pages/   # Page components
│   │   │   └── ui/      # Reusable UI components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── store/       # Zustand state management
│   │   ├── styles/      # Global styles and CSS
│   │   └── utils/       # Utility functions
│   ├── public/          # Static assets
│   └── dist/            # Built renderer files
└── shared/              # Shared between main and renderer
```

## Development

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd learning-platform-desktop
```

2. Install dependencies:
```bash
npm install
```

3. Install renderer dependencies:
```bash
cd src/renderer
npm install
cd ../..
```

### Development Scripts

```bash
# Start development mode (both Electron and React)
npm run dev

# Start only Electron in development
npm run electron:dev

# Start only React development server
npm run react:dev

# Build for production
npm run build

# Build only the renderer
npm run react:build

# Run Electron in production mode
npm run electron:start
```

### Development Workflow

The application uses a dual-process architecture:

1. **Main Process** (`src/main/`): Handles OS integration, file system, native menus
2. **Renderer Process** (`src/renderer/`): React UI with hot reload via Vite

In development:
- Main process reloads with nodemon
- Renderer process hot reloads with Vite
- IPC communication via preload script for security

## Building & Distribution

### Build Commands

```bash
# Build both renderer and Electron app
npm run build

# Platform-specific builds
npm run build:win    # Windows
npm run build:mac    # macOS  
npm run build:linux  # Linux
```

### Code Signing

For production distribution, configure code signing in `electron-builder`:

```json
{
  "build": {
    "mac": {
      "identity": "Developer ID Application: Your Name"
    },
    "win": {
      "certificateFile": "path/to/certificate.p12"
    }
  }
}
```

## Configuration

### Environment Variables

Create `.env` files for configuration:

```env
# Main process environment
NODE_ENV=development

# Renderer process environment  
VITE_API_URL=http://localhost:3000
VITE_DEBUG=true
```

### App Settings

The application persists user settings locally using `electron-store`:

- Theme preferences (light/dark/auto)
- Hardware tier selection
- LLM provider choice
- Review session preferences
- User statistics and progress

## Keyboard Shortcuts

### Navigation
- `Ctrl+1-6`: Navigate to main sections
- `Ctrl+,`: Open settings
- `F1`: Show keyboard shortcuts
- `Esc`: Close modal or cancel action

### Review Session
- `Space`: Show/hide card answer
- `1-4`: Grade card (1=Again, 2=Hard, 3=Good, 4=Easy)
- `Enter`: Submit quiz answer
- `Ctrl+P`: Pause/resume session
- `Ctrl+E`: End session

### General
- `Ctrl+S`: Save current work
- `Ctrl+N`: New deck
- `Ctrl+O`: Import content
- `Ctrl+T`: Toggle theme
- `Ctrl+/`: Focus search

## Accessibility

The application follows WCAG 2.1 AA guidelines:

- **Color Contrast**: Minimum 4.5:1 ratio for text
- **Keyboard Navigation**: Full app functionality via keyboard
- **Screen Reader Support**: ARIA labels and live regions
- **Focus Management**: Visible focus indicators
- **Reduced Motion**: Respects `prefers-reduced-motion`

## Performance

### Optimization Features
- Hardware tier auto-detection for optimal performance
- Lazy loading for large content collections
- Efficient state management with Zustand
- Virtual scrolling for large lists
- Optimized bundle splitting

### Memory Management
- Automatic cleanup of expired cards
- Efficient chart rendering with Recharts
- Context isolation in Electron for security
- Local data persistence with compression

## Security

### Electron Security Features
- Context isolation enabled
- Node integration disabled in renderer
- Preload script for secure IPC
- Content Security Policy headers
- Safe file handling and validation

### Data Privacy
- Local-first approach with optional cloud sync
- End-to-end encryption ready
- User data stays on device by default
- Transparent privacy controls

## Contributing

### Development Guidelines

1. **Code Style**: Follow existing patterns and use ESLint/Prettier
2. **Component Structure**: Use functional components with hooks
3. **State Management**: Use Zustand for global state, React state for local
4. **Styling**: Use Tailwind CSS classes, avoid inline styles
5. **Accessibility**: Include proper ARIA labels and keyboard support

### Commit Convention

Follow conventional commits:
- `feat:` New features
- `fix:` Bug fixes  
- `docs:` Documentation updates
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Testing updates

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and feedback:
- Email: support@learningplatform.dev
- GitHub Issues: Report bugs and feature requests
- Documentation: User guide and tutorials available in-app

---

**Made with ❤️ for learners everywhere**
