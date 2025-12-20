# Quick Start Guide - SRS Mobile

Get up and running with the SRS Mobile Companion App in 5 minutes!

## Prerequisites

Before you begin, ensure you have:

- ✅ Node.js 18+ installed
- ✅ npm or yarn
- ✅ Git
- ✅ For iOS: macOS with Xcode 12+
- ✅ For Android: Android Studio with SDK

## Installation

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/srs-companion.git
cd srs-companion

# Install dependencies
npm run setup
```

This will install all dependencies and iOS pods automatically.

### 2. Start Development Server

```bash
cd mobile
npm start
```

Keep this terminal running!

### 3. Run the App

Open a new terminal:

#### For iOS:
```bash
cd mobile
npm run ios
```

#### For Android:
```bash
# Start emulator first, or connect a device
cd mobile
npm run android
```

## First Run

When you first run the app:

1. **Today's Reviews Tab**: Will show "All Caught Up!" (no cards yet)
2. **Decks Tab**: Will show "No Decks Yet" with sync prompt
3. **Stats Tab**: Will show initial stats (all zeros)
4. **Graph Tab**: Will show "No Concepts Yet"
5. **Settings Tab**: Access to sync and preferences

## Setting Up Backend Connection

1. Open `mobile/src/services/api.ts`
2. Update the base URL:
   ```typescript
   private baseURL: string = 'https://your-api.com/api';
   ```

## First Sync

1. Go to **Settings** tab
2. Tap **Sync Now** button
3. Wait for sync to complete
4. Navigate to other tabs to see your data

## Testing Without Backend

To test without a backend server:

1. Create sample data in the database:
   ```bash
   cd mobile
   npm run seed-db  # (You'll need to create this script)
   ```

Or manually add test cards through the SQLite database.

## Development Commands

| Command | Description |
|---------|-------------|
| `npm start` | Start Metro bundler |
| `npm run ios` | Run on iOS simulator |
| `npm run android` | Run on Android emulator |
| `npm test` | Run tests |
| `npm run lint` | Lint code |
| `npm run typecheck` | Type check |

## Troubleshooting

### iOS Build Fails

```bash
cd mobile/ios
pod deintegrate
pod install
cd ..
npm run ios
```

### Android Build Fails

```bash
cd mobile/android
./gradlew clean
cd ..
npm run android
```

### Metro Bundler Issues

```bash
npm start -- --reset-cache
```

### Can't Connect to Development Server

- Ensure your device/simulator is on the same network
- Check Metro bundler is running
- Try restarting the bundler

## Common Tasks

### Add a New Screen

1. Create screen file in `src/screens/`
2. Add navigation entry in `src/navigation/index.tsx`
3. Update types in `src/types/index.ts`

### Add a New Service

1. Create service file in `src/services/`
2. Export methods
3. Import in store or screens as needed

### Update State

1. Open `src/store/index.ts`
2. Add new state properties
3. Add actions to modify state
4. Use in components with `useAppStore()`

## Project Structure Quick Reference

```
mobile/
├── src/
│   ├── screens/       # UI screens (5 tabs)
│   ├── services/      # Business logic
│   ├── store/         # State management
│   ├── utils/         # Utilities (SRS algorithm)
│   ├── types/         # TypeScript types
│   └── navigation/    # Navigation setup
├── android/           # Android native
├── ios/               # iOS native
└── App.tsx           # Root component
```

## Key Files

- `App.tsx` - App entry point
- `src/store/index.ts` - State management
- `src/services/database.ts` - SQLite operations
- `src/services/sync.ts` - Sync mechanism
- `src/utils/srs.ts` - SRS algorithm

## Next Steps

1. ✅ Review the [README.md](mobile/README.md) for detailed documentation
2. ✅ Check [IMPLEMENTATION.md](mobile/IMPLEMENTATION.md) for architecture
3. ✅ Read [WORKFLOW.md](mobile/WORKFLOW.md) for development workflow
4. ✅ Set up backend API (see [API.md](mobile/API.md))
5. ✅ Configure environment variables
6. ✅ Set up error tracking
7. ✅ Configure analytics
8. ✅ Prepare for deployment

## Getting Help

- 📚 Check documentation in `/mobile/` directory
- 🐛 Report issues on GitHub
- 💬 Ask questions in team chat
- 📧 Contact: support@yourdomain.com

## Useful Resources

- [React Native Docs](https://reactnative.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Zustand Docs](https://github.com/pmndrs/zustand)
- [React Navigation](https://reactnavigation.org/)

---

**You're all set!** Happy coding! 🚀
