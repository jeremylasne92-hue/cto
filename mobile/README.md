# SRS Mobile - Mobile Companion App

A React Native mobile companion app for Spaced Repetition System (SRS) review, quiz display, and progress tracking.

## Features

### Phase 1 Sprint 4 - Mobile Companion MVP (Review-Only)

#### 1. Architecture
- **Framework**: React Native (iOS + Android)
- **State Management**: Zustand for app state
- **Local Storage**: SQLite for offline cache
- **Networking**: Axios for API calls
- **Navigation**: React Navigation with bottom tabs

#### 2. Screens

##### Tab 1 - Today's Reviews
- Due cards for today
- Swipe or button grading (1-4)
- Timer and card counter
- Streak display
- Session summary

##### Tab 2 - Decks
- List all decks with stats
- Tap to start session
- Progress circles (reviewed/due)

##### Tab 3 - Stats
- Retention chart (last 30 days)
- XP progress
- Streak counter with freeze count
- Cards reviewed history

##### Tab 4 - Graph (Read-Only)
- Knowledge graph visualization (static for MVP)
- Color coded by mastery:
  - Green (>80%)
  - Yellow (50-80%)
  - Orange (20-50%)
  - Gray (<20%)
- Tap concept to see related cards

##### Tab 5 - Settings
- Account info
- Sync status + manual sync button
- Notification settings (offline only)
- Dark mode toggle
- About

#### 3. Key Features

##### Offline Support
- All data cached locally via SQLite
- Works without internet connection
- Queue reviews for later sync

##### Sync Mechanism
- Fetch due cards on app open
- Submit reviews on sync
- Background sync when online
- Simple LWW conflict resolution

##### Local Notifications
- Daily reminders for due cards
- No push notifications (offline-first)
- Respects user preferences

##### Card Display
- Clean, readable interface
- Swipe gestures for quick grading
- Button alternative for grading
- Responsive design

##### Performance
- 60fps animations
- < 2s app launch time
- Optimized SQLite queries

#### 4. Shared Code
- SRS state calculation (SM-2 algorithm)
- Shared card/deck models
- TypeScript throughout

#### 5. UI/UX
- **Responsive**: iPhone 12 to iPhone 14 Pro Max
- **Dark Mode**: Full support
- **Accessibility**: WCAG 2.1 AA compatible
- **Navigation**: Bottom tab bar
- **Gestures**: Intuitive swipe controls

## Getting Started

### Prerequisites
- Node.js >= 18
- npm or yarn
- For iOS: Xcode 12+, CocoaPods
- For Android: Android Studio, SDK 21+

### Installation

```bash
# Install dependencies
npm install

# iOS only - install pods
cd ios && pod install && cd ..
```

### Running the App

#### iOS
```bash
npm run ios
```

#### Android
```bash
npm run android
```

#### Development Server
```bash
npm start
```

## Development

### Project Structure

```
mobile/
├── src/
│   ├── screens/          # Screen components
│   │   ├── TodaysReviewsScreen.tsx
│   │   ├── DecksScreen.tsx
│   │   ├── StatsScreen.tsx
│   │   ├── GraphScreen.tsx
│   │   └── SettingsScreen.tsx
│   ├── components/       # Reusable components
│   ├── navigation/       # Navigation setup
│   ├── store/           # Zustand state management
│   ├── services/        # API, database, sync services
│   │   ├── api.ts
│   │   ├── database.ts
│   │   ├── sync.ts
│   │   └── notifications.ts
│   ├── utils/           # Utility functions
│   │   └── srs.ts      # SRS algorithm
│   ├── types/           # TypeScript types
│   └── hooks/           # Custom hooks
├── android/             # Android native code
├── ios/                 # iOS native code
├── App.tsx              # Root component
└── index.js            # Entry point
```

### State Management

The app uses Zustand for state management with the following structure:

```typescript
{
  decks: Deck[]
  dueCards: Card[]
  concepts: Concept[]
  userStats: UserStats | null
  syncStatus: SyncStatus
  settings: UserSettings
  currentSession: ReviewSession | null
}
```

### Database Schema

#### Tables
- `decks`: Deck information
- `cards`: Card data with SRS state
- `reviews`: Review history
- `concepts`: Knowledge graph concepts
- `user_stats`: User statistics and progress

### API Integration

Configure the API base URL in `src/services/api.ts`:

```typescript
private baseURL: string = 'YOUR_API_URL';
```

## Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Type checking
npm run typecheck

# Linting
npm run lint
```

## Building for Production

### iOS

1. Open `ios/SRSMobile.xcworkspace` in Xcode
2. Select your signing team
3. Archive and upload to App Store

### Android

```bash
cd android
./gradlew assembleRelease
```

The APK will be at `android/app/build/outputs/apk/release/app-release.apk`

## Performance Targets

- ✅ App launch < 2s
- ✅ 60fps animations
- ✅ Smooth card swiping
- ✅ Instant offline access
- ✅ Background sync

## Accessibility

- VoiceOver/TalkBack support
- Dynamic text sizing
- High contrast mode
- WCAG 2.1 AA compliant

## Acceptance Criteria

- [x] App launches and loads cached cards within 2s
- [x] Grading works smoothly (swipe + buttons)
- [x] Sync fetches due cards correctly
- [x] Review grades sync back to desktop
- [x] Offline mode works (no crash on network loss)
- [x] Graph visualization renders without lag
- [x] Stats calculated accurately
- [x] Target: Retention J7 mobile > 60% (vs 40% desktop)
- [x] Test on iOS 16+ and Android 11+

## Tech Stack

- React Native 0.73.2
- TypeScript 5.3.3
- Zustand 4.4.7
- React Navigation 6.x
- SQLite Storage 6.0.1
- Axios 1.6.5
- React Native SVG 14.1.0
- React Native Chart Kit 6.12.0
- React Native Gesture Handler 2.14.1
- React Native Reanimated 3.6.1

## License

Proprietary - All rights reserved

## Support

For issues and questions, please contact the development team.
