# Implementation Details - SRS Mobile Companion App

## Overview

This document provides detailed information about the implementation of the SRS Mobile Companion App (Phase 1 Sprint 4 - MVP, Review-Only).

## Architecture

### Technology Stack

- **React Native 0.73.2**: Cross-platform mobile framework
- **TypeScript 5.3.3**: Type-safe development
- **Zustand 4.4.7**: Lightweight state management
- **SQLite**: Local offline storage
- **React Navigation 6.x**: Navigation framework
- **Axios**: HTTP client for API calls

### Design Patterns

1. **Service Layer Pattern**: Separated concerns for database, API, sync, and notifications
2. **State Management**: Centralized Zustand store with actions
3. **Repository Pattern**: Database service acts as data repository
4. **Observer Pattern**: Sync service uses listeners for status updates

## Core Components

### 1. State Management (`src/store/index.ts`)

Zustand store managing:
- Decks and cards data
- User statistics
- Sync status
- Settings
- Current review session

Key actions:
- `initializeApp()`: Initialize database and load data
- `startReviewSession()`: Begin a review session
- `gradeCard()`: Grade a card and update SRS state
- `syncData()`: Sync with backend server

### 2. Database Service (`src/services/database.ts`)

SQLite database with tables:
- `decks`: Deck information
- `cards`: Card data with SRS state
- `reviews`: Review history (with sync flag)
- `concepts`: Knowledge graph concepts
- `user_stats`: User progress and statistics

Key features:
- Promise-based API
- Transaction support
- Indexed queries for performance
- Sync tracking (synced flag)

### 3. SRS Algorithm (`src/utils/srs.ts`)

Implementation of SM-2 algorithm:
- Grade 1-2: Failed recall, reset to 1 day
- Grade 3: Good recall, standard interval
- Grade 4: Easy recall, increased interval

Factors:
- `easeFactor`: Difficulty adjustment (default 2.5)
- `interval`: Days until next review
- `repetitions`: Successful review count
- `lapses`: Failed review count

### 4. Sync Service (`src/services/sync.ts`)

Bidirectional sync mechanism:
1. Push local reviews to server
2. Pull decks from server
3. Pull due cards from server
4. Pull concepts from server
5. Pull user stats from server

Conflict resolution: Last Write Wins (LWW)

### 5. Notification Service (`src/services/notifications.ts`)

Local notifications only (no push):
- Daily reminders at configured time
- Due card notifications
- Permission handling
- Channel configuration (Android)

## Screen Components

### 1. Today's Reviews Screen

Features:
- Card display with front/back
- Swipe gestures for grading:
  - Left: Again (Grade 1)
  - Right: Easy (Grade 4)
  - Up: Good (Grade 3)
  - Down: Hard (Grade 2)
- Button-based grading alternative
- Session counter and timer
- Streak display
- Session summary on completion

Performance optimizations:
- Animated.Value for smooth gestures
- useCallback for handler memoization
- Efficient re-renders

### 2. Decks Screen

Features:
- List of all decks
- Progress circles showing due/total
- Stats: total cards, reviewed today
- Progress bars
- Tap to start session

### 3. Stats Screen

Features:
- Overview cards: streak, level, retention
- XP progress bar
- Line chart (last 30 days)
- Streak freeze counter
- All-time statistics

Charts powered by `react-native-chart-kit`

### 4. Graph Screen

Features:
- SVG-based knowledge graph
- Color-coded nodes by mastery:
  - Green (>80%): Mastered
  - Yellow (50-80%): Learning
  - Orange (20-50%): Struggling
  - Gray (<20%): New
- Tap concept for details
- Related concepts navigation
- Edge rendering between related concepts

### 5. Settings Screen

Features:
- Account information
- Manual sync button
- Sync status display
- Notification toggle and time picker
- Dark mode toggle
- App version and about info

## Data Flow

### Review Flow

1. User opens app
2. App loads due cards from SQLite
3. User reviews card
4. App calculates new SRS state
5. App updates card in SQLite
6. App saves review to SQLite (synced=0)
7. Next sync: reviews pushed to server

### Sync Flow

1. User triggers sync (manual or automatic)
2. Check internet connection
3. Push unsynced reviews
4. Pull latest data from server
5. Update SQLite with server data
6. Mark synced reviews (synced=1)
7. Notify UI of completion

## Performance Optimizations

### Database
- Indexes on frequently queried columns
- Batch operations where possible
- Prepared statements
- Connection pooling

### UI
- React.memo for expensive components
- useCallback/useMemo for expensive computations
- FlatList for large lists
- Animated API for 60fps animations
- Debounced sync triggers

### Storage
- Efficient SQLite schema
- Only cache necessary data
- Periodic cleanup of old data
- Compressed images

## Offline Support

### Strategy
1. All essential data cached in SQLite
2. App fully functional offline
3. Reviews queued for sync
4. Graceful degradation when offline
5. Clear offline indicators

### Sync Queue
- Reviews stored with synced=0 flag
- Automatic retry on connection restore
- Manual sync button always available
- Conflict resolution: server wins

## Security

### Data Protection
- SQLite database encryption (production)
- Secure token storage
- HTTPS for all API calls
- No sensitive data in logs

### Authentication
- JWT token-based auth
- Token refresh mechanism
- Secure storage using platform APIs
- Automatic logout on token expiry

## Testing Strategy

### Unit Tests
- SRS algorithm calculations
- Database operations
- Sync logic
- Utility functions

### Integration Tests
- Store actions
- API service calls
- Database migrations
- Sync workflows

### E2E Tests (Future)
- User flows
- Review sessions
- Sync operations
- Offline scenarios

## Accessibility

### Features
- VoiceOver/TalkBack labels
- Semantic HTML/native elements
- High contrast support
- Dynamic text sizing
- Focus management
- Keyboard navigation

### WCAG 2.1 AA Compliance
- Color contrast ratios
- Touch target sizes (44x44pt)
- Alternative text
- Readable fonts
- Clear error messages

## Platform-Specific Considerations

### iOS
- Safe area handling
- Dynamic type support
- Haptic feedback
- Dark mode system integration
- App lifecycle handling

### Android
- Material Design guidelines
- Back button handling
- Notification channels
- Permission requests
- App lifecycle handling

## Future Enhancements

### Planned Features
1. Biometric authentication
2. Card creation (remove review-only restriction)
3. Audio/image attachments
4. Advanced statistics
5. Social features (sharing, leaderboards)
6. Spaced repetition presets
7. Custom card types
8. Deck sharing
9. Export/import functionality
10. Widget support

### Technical Debt
- Add comprehensive tests
- Implement proper error boundaries
- Add performance monitoring
- Implement analytics
- Add crash reporting
- Optimize bundle size
- Implement code splitting

## Deployment

### iOS
1. Configure signing in Xcode
2. Archive for distribution
3. Upload to App Store Connect
4. Submit for review
5. Release to users

### Android
1. Generate signed APK/AAB
2. Upload to Play Console
3. Configure listing
4. Submit for review
5. Release to production

## Monitoring

### Metrics to Track
- App launch time
- Review completion time
- Sync success rate
- Crash rate
- User retention (J7, J30)
- Active users
- Review accuracy
- Offline usage percentage

## Support

### Documentation
- User guide
- FAQ
- Troubleshooting guide
- API documentation
- Architecture diagrams

### Feedback Channels
- In-app feedback
- Email support
- GitHub issues
- User surveys

## Conclusion

This implementation provides a solid foundation for the SRS Mobile Companion App MVP. It focuses on the core review functionality while maintaining high performance, offline capability, and excellent user experience. The architecture is designed to scale as new features are added in future sprints.
