# Development Workflow - SRS Mobile

This document outlines the development workflow for the SRS Mobile Companion App.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Daily Workflow](#daily-workflow)
3. [Feature Development](#feature-development)
4. [Bug Fixes](#bug-fixes)
5. [Release Process](#release-process)
6. [Hotfix Process](#hotfix-process)

## Development Setup

### Initial Setup

```bash
# Clone repository
git clone https://github.com/yourusername/srs-companion.git
cd srs-companion

# Install dependencies
npm run setup

# Start development
cd mobile
npm start
```

### iOS Setup

```bash
# Install CocoaPods dependencies
cd ios
pod install
cd ..

# Run on simulator
npm run ios

# Run on device
npm run ios -- --device
```

### Android Setup

```bash
# Start emulator (or connect device)
emulator -avd Pixel_4_API_30

# Run on emulator/device
npm run android
```

## Daily Workflow

### Starting Work

1. **Pull latest changes**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create/switch to feature branch**
   ```bash
   git checkout -b feature/your-feature
   ```

3. **Start development server**
   ```bash
   cd mobile
   npm start
   ```

4. **Run app**
   ```bash
   # In another terminal
   npm run ios    # or npm run android
   ```

### During Development

1. **Make changes** in your editor
2. **Test changes** in simulator/device
3. **Run tests** frequently
   ```bash
   npm test
   ```

4. **Check types**
   ```bash
   npm run typecheck
   ```

5. **Lint code**
   ```bash
   npm run lint
   ```

### Ending Work

1. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: your descriptive message"
   ```

2. **Push to remote**
   ```bash
   git push origin feature/your-feature
   ```

3. **Create PR** if feature is complete

## Feature Development

### 1. Planning Phase

- Review feature requirements
- Design UI mockups
- Plan data structures
- Identify affected components
- Estimate complexity

### 2. Implementation Phase

#### Create Feature Branch

```bash
git checkout main
git pull origin main
git checkout -b feature/feature-name
```

#### Write Tests First (TDD)

```typescript
// src/__tests__/newFeature.test.ts
describe('New Feature', () => {
  it('should do something', () => {
    // Test code
  });
});
```

#### Implement Feature

1. **Create types** in `src/types/`
2. **Implement logic** in `src/utils/` or `src/services/`
3. **Update store** in `src/store/`
4. **Create/update components** in `src/components/`
5. **Create/update screens** in `src/screens/`
6. **Add navigation** if needed

#### Test Implementation

```bash
# Run tests
npm test

# Run specific test
npm test -- newFeature.test.ts

# Run with coverage
npm test -- --coverage
```

#### Manual Testing

- Test on iOS simulator
- Test on Android emulator
- Test on real devices
- Test in light mode
- Test in dark mode
- Test offline mode
- Test accessibility

### 3. Review Phase

#### Self Review

- [ ] Code follows style guide
- [ ] All tests pass
- [ ] No TypeScript errors
- [ ] No linting errors
- [ ] Documentation updated
- [ ] Comments added where needed
- [ ] Performance is acceptable
- [ ] Accessibility is maintained

#### Create Pull Request

```bash
git push origin feature/feature-name
```

Then create PR on GitHub with:
- Clear description
- Screenshots/videos
- Testing notes
- Related issues

### 4. Merge Phase

- Address review comments
- Rebase if needed
- Squash commits if requested
- Wait for approval
- Merge to main

## Bug Fixes

### 1. Investigation

- Reproduce the bug
- Identify root cause
- Check for related issues
- Determine severity

### 2. Fix Implementation

```bash
# Create fix branch
git checkout main
git pull origin main
git checkout -b fix/bug-description

# Write test that fails
# Implement fix
# Verify test passes
# Test manually

# Commit and push
git add .
git commit -m "fix: description of fix"
git push origin fix/bug-description
```

### 3. Verification

- Original issue is fixed
- No new issues introduced
- All tests pass
- Manual testing completed

## Release Process

### 1. Preparation

```bash
# Create release branch
git checkout main
git pull origin main
git checkout -b release/v1.1.0

# Update version
cd mobile
npm version 1.1.0

# Update CHANGELOG.md
# Update version in app.json
# Update version in Info.plist (iOS)
# Update versionCode/versionName (Android)
```

### 2. Testing

- Full regression testing
- Test on all supported devices
- Test upgrade from previous version
- Verify all new features
- Check for performance issues

### 3. Build

#### iOS

```bash
# Open Xcode
cd ios
open SRSMobile.xcworkspace

# In Xcode:
# 1. Select Generic iOS Device
# 2. Product > Archive
# 3. Distribute App
# 4. App Store Connect
# 5. Upload
```

#### Android

```bash
cd android
./gradlew bundleRelease

# APK location:
# android/app/build/outputs/bundle/release/app-release.aab
```

### 4. Deployment

#### iOS (TestFlight)

1. Upload to App Store Connect
2. Add build to TestFlight
3. Submit for review
4. Distribute to testers

#### Android (Internal Testing)

1. Upload to Play Console
2. Create release in Internal Testing
3. Add release notes
4. Rollout to testers

### 5. Release

#### iOS

1. Submit for App Store review
2. Set release date
3. Monitor review status
4. Release to production

#### Android

1. Promote to Production
2. Set rollout percentage
3. Monitor crash reports
4. Gradually increase rollout

### 6. Post-Release

- Monitor crash reports
- Track user feedback
- Monitor performance metrics
- Prepare hotfix if needed
- Update documentation
- Announce release

## Hotfix Process

### When to Hotfix

- Critical bugs in production
- Security vulnerabilities
- Data loss issues
- App crashes
- Payment issues

### Hotfix Steps

```bash
# Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# Implement minimal fix
# Add test for bug
# Verify fix works

# Update version (patch)
cd mobile
npm version patch  # e.g., 1.0.0 -> 1.0.1

# Commit and push
git add .
git commit -m "fix: critical bug description"
git push origin hotfix/critical-bug

# Create PR to main
# Get expedited review
# Merge to main

# Build and deploy immediately
# Monitor closely
```

### Hotfix Build

```bash
# iOS
cd ios
# Build in Xcode with expedited review request

# Android
cd android
./gradlew bundleRelease
# Upload to Play Console with priority flag
```

## Development Tips

### Performance Profiling

```bash
# React DevTools
npm install -g react-devtools
react-devtools

# Flipper (debugging)
# Download from https://fbflipper.com/
```

### Debugging

```typescript
// Add breakpoints in VS Code
// Use React Native Debugger
// Check Metro bundler logs
// View device logs:

// iOS
xcrun simctl spawn booted log stream

// Android
adb logcat *:S ReactNative:V ReactNativeJS:V
```

### Common Issues

#### Metro Bundler Issues
```bash
# Clear cache
npm start -- --reset-cache
```

#### iOS Build Issues
```bash
# Clean build
cd ios
pod deintegrate
pod install
```

#### Android Build Issues
```bash
# Clean build
cd android
./gradlew clean
```

## Code Review Checklist

### For Authors

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code is self-explanatory
- [ ] No console.logs
- [ ] No commented code
- [ ] Follows style guide
- [ ] Handles errors
- [ ] Optimized for performance

### For Reviewers

- [ ] Code is understandable
- [ ] Logic is correct
- [ ] Tests are adequate
- [ ] No security issues
- [ ] Performance is acceptable
- [ ] Accessibility maintained
- [ ] Documentation sufficient

## Resources

- [React Native Documentation](https://reactnative.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Testing Library](https://testing-library.com/react-native)
- [React Navigation](https://reactnavigation.org/)
- [Zustand Documentation](https://github.com/pmndrs/zustand)

## Support

For workflow questions:
- Check this document
- Ask team members
- Create discussion on GitHub
- Update this doc with learnings
