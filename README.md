# SRS Mobile Companion App

Mobile companion application for Spaced Repetition System (SRS) review, quiz display, and progress tracking.

## Project Overview

This repository contains a React Native mobile application designed to complement a desktop SRS application. The mobile app focuses on review-only functionality, allowing users to review their flashcards on the go with full offline support.

## Features

- **Review System**: Swipe-based and button-based card grading
- **Offline First**: Full functionality without internet connection
- **Smart Sync**: Bidirectional sync with desktop application
- **Progress Tracking**: Comprehensive statistics and retention charts
- **Knowledge Graph**: Visual representation of concept relationships
- **Dark Mode**: Full dark mode support
- **Notifications**: Local notifications for due cards
- **Cross-Platform**: iOS and Android support

## Quick Start

```bash
# Navigate to mobile directory
cd mobile

# Install dependencies
npm install

# iOS - Install pods
cd ios && pod install && cd ..

# Run on iOS
npm run ios

# Run on Android
npm run android
```

## Documentation

- [Mobile App README](mobile/README.md) - Detailed setup and usage
- [Implementation Guide](mobile/IMPLEMENTATION.md) - Technical architecture and design decisions

## Technology Stack

- React Native 0.73.2
- TypeScript 5.3.3
- Zustand (State Management)
- SQLite (Local Storage)
- React Navigation
- Axios

## Project Structure

```
.
├── mobile/                 # React Native mobile app
│   ├── src/
│   │   ├── screens/       # Screen components
│   │   ├── components/    # Reusable components
│   │   ├── services/      # Business logic services
│   │   ├── store/         # State management
│   │   ├── utils/         # Utility functions
│   │   └── types/         # TypeScript types
│   ├── android/           # Android native code
│   ├── ios/               # iOS native code
│   └── README.md
└── README.md              # This file
```

## Development Workflow

1. **Feature Development**: Work in feature branches
2. **Testing**: Run tests before committing
3. **Code Review**: Submit PRs for review
4. **Integration**: Merge to main after approval
5. **Release**: Tag releases for deployment

## Acceptance Criteria (MVP)

- ✅ App launches within 2 seconds
- ✅ Smooth card review experience (60fps)
- ✅ Offline mode fully functional
- ✅ Sync mechanism works reliably
- ✅ Knowledge graph renders without lag
- ✅ Accurate statistics tracking
- ✅ iOS 16+ and Android 11+ compatibility

## Performance Targets

- App Launch: < 2s
- Frame Rate: 60fps
- Sync Time: < 5s for 100 cards
- Database Queries: < 100ms
- UI Interactions: < 16ms response

## License

Proprietary - All rights reserved

## Contributing

Please read the development guidelines before contributing to this project.

## Support

For issues and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Phase 1 Sprint 4** - Mobile Companion MVP (Review-Only)
