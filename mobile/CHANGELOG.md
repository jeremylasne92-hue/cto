# Changelog

All notable changes to the SRS Mobile Companion App will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added - Phase 1 Sprint 4 MVP (Review-Only)

#### Core Features
- Review system with swipe and button-based grading
- Offline-first architecture with SQLite storage
- Bidirectional sync with backend server
- Today's Reviews screen with card display
- Decks screen with progress tracking
- Stats screen with retention charts
- Knowledge graph visualization
- Settings screen with sync and preferences

#### Architecture
- React Native 0.73.2 framework
- TypeScript 5.3.3 for type safety
- Zustand state management
- SQLite for local storage
- React Navigation with bottom tabs
- Axios for API communication

#### SRS Algorithm
- SM-2 algorithm implementation
- 4-grade system (Again, Hard, Good, Easy)
- Automatic interval calculation
- Ease factor adjustment
- Lapse tracking

#### Sync System
- Push local reviews to server
- Pull decks, cards, concepts, and stats
- Unsynced review queue
- Manual sync button
- Sync status indicators
- Last Write Wins conflict resolution

#### Offline Support
- Full app functionality offline
- Local SQLite database
- Review queue for pending syncs
- Graceful offline handling
- Connection status detection

#### UI/UX
- Dark mode support
- Swipe gestures for card grading
- Smooth 60fps animations
- Progress indicators
- Session summaries
- Streak displays
- XP and leveling system

#### Notifications
- Local daily reminders
- Due card notifications
- Configurable notification time
- Permission handling

#### Accessibility
- VoiceOver/TalkBack support
- Dynamic text sizing
- High contrast mode
- WCAG 2.1 AA compliance
- Touch target optimization

#### Performance
- App launch < 2s
- 60fps animations
- Efficient SQLite queries
- Optimized re-renders
- Gesture handler optimization

#### Platform Support
- iOS 13.4+
- Android API 21+ (Android 5.0)
- iPhone 12 to iPhone 14 Pro Max tested
- Various Android devices tested

#### Testing
- Jest test framework setup
- React Native Testing Library
- SRS algorithm unit tests
- Mock API responses
- Type checking with TypeScript

#### Documentation
- README with quick start guide
- Implementation documentation
- API documentation
- Code comments
- TypeScript types

### Developer Experience
- ESLint configuration
- Prettier code formatting
- TypeScript strict mode
- Git hooks ready
- Hot reload support
- Debug menu access

## [Unreleased]

### Planned Features
- [ ] Biometric authentication
- [ ] Card creation (remove review-only restriction)
- [ ] Audio/image attachments
- [ ] Advanced statistics
- [ ] Social features
- [ ] Custom SRS presets
- [ ] Deck sharing
- [ ] Export/import functionality
- [ ] Widget support
- [ ] Apple Watch companion
- [ ] Wear OS support

### Technical Improvements
- [ ] Comprehensive test coverage
- [ ] Performance monitoring
- [ ] Analytics integration
- [ ] Crash reporting
- [ ] A/B testing framework
- [ ] Code splitting
- [ ] Bundle size optimization
- [ ] Background sync improvements

---

## Version History

### [1.0.0] - 2024-01-15
Initial MVP release with review-only functionality.

---

## Notes

- This changelog follows semantic versioning
- Each version includes the release date
- Features are categorized by type
- Breaking changes are clearly marked
- Migration guides provided when needed

## How to Update

### For Users
1. Open App Store (iOS) or Play Store (Android)
2. Navigate to SRS Mobile
3. Tap "Update"
4. Review changelog in store listing

### For Developers
1. Pull latest changes from repository
2. Run `npm install` to update dependencies
3. Review CHANGELOG.md for breaking changes
4. Update local configuration if needed
5. Run tests: `npm test`
6. Build and deploy following deployment guide

## Support

For issues with specific versions:
- Check known issues in GitHub
- Contact support with version number
- Include device and OS information
