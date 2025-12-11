# Contributing to SRS Mobile Companion App

Thank you for your interest in contributing to the SRS Mobile Companion App! This guide will help you get started.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Commit Messages](#commit-messages)
7. [Pull Request Process](#pull-request-process)
8. [Issue Reporting](#issue-reporting)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect differing viewpoints and experiences
- Accept responsibility for mistakes
- Prioritize the community's best interests

## Getting Started

### Prerequisites

- Node.js >= 18
- npm or yarn
- Git
- For iOS: Xcode 12+, CocoaPods
- For Android: Android Studio, SDK 21+

### Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/srs-companion.git
   cd srs-companion
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/original/srs-companion.git
   ```

4. Install dependencies:
   ```bash
   npm run setup
   ```

5. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `test/` - Test improvements
- `chore/` - Maintenance tasks

Example: `feature/add-audio-support`

### Making Changes

1. Keep changes focused and atomic
2. Write tests for new features
3. Update documentation as needed
4. Ensure all tests pass
5. Follow coding standards

### Running the App

```bash
# iOS
npm run mobile:ios

# Android
npm run mobile:android
```

### Running Tests

```bash
# All tests
npm run mobile:test

# Watch mode
cd mobile && npm test -- --watch

# Coverage
cd mobile && npm test -- --coverage
```

### Type Checking

```bash
npm run mobile:typecheck
```

### Linting

```bash
npm run mobile:lint

# Auto-fix
cd mobile && npm run lint -- --fix
```

## Coding Standards

### TypeScript

- Use TypeScript for all new code
- Enable strict mode
- Define interfaces for all data structures
- Avoid `any` type unless absolutely necessary
- Use descriptive variable and function names

### React Native

- Use functional components with hooks
- Avoid inline functions in render
- Use `useCallback` and `useMemo` appropriately
- Keep components small and focused
- Extract reusable logic into custom hooks

### Styling

- Use StyleSheet.create for styles
- Follow platform-specific design guidelines
- Support both light and dark modes
- Ensure touch targets are at least 44x44pt
- Use consistent spacing (8pt grid system)

### File Organization

```
src/
├── screens/       # Screen components
├── components/    # Reusable components
├── services/      # Business logic
├── store/         # State management
├── utils/         # Utility functions
├── types/         # TypeScript types
└── hooks/         # Custom hooks
```

### Naming Conventions

- Components: PascalCase (`TodaysReviewsScreen.tsx`)
- Functions: camelCase (`calculateNextReview`)
- Constants: UPPER_SNAKE_CASE (`MAX_RETRY_ATTEMPTS`)
- Interfaces: PascalCase with 'I' prefix optional (`Card` or `ICard`)
- Files: Match primary export name

### Code Style

- Use Prettier for formatting (config in `.prettierrc.js`)
- Use ESLint for linting (config in `.eslintrc.js`)
- Maximum line length: 100 characters
- Use 2 spaces for indentation
- Use single quotes for strings
- Add trailing commas in objects and arrays

## Testing Guidelines

### Unit Tests

- Test pure functions and utilities
- Test business logic thoroughly
- Mock external dependencies
- Aim for >80% code coverage

### Integration Tests

- Test component interactions
- Test state management
- Test API service calls
- Test database operations

### Test Structure

```typescript
describe('Feature Name', () => {
  describe('specific functionality', () => {
    it('should do something specific', () => {
      // Arrange
      const input = setupTestData();
      
      // Act
      const result = functionUnderTest(input);
      
      // Assert
      expect(result).toBe(expectedValue);
    });
  });
});
```

### What to Test

- ✅ Business logic (SRS algorithm)
- ✅ Data transformations
- ✅ API interactions
- ✅ Database operations
- ✅ State management
- ❌ Third-party libraries
- ❌ React Native built-ins

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

### Examples

```
feat(reviews): add swipe gestures for card grading

Implement left/right swipe for Again/Easy grades
Implement up/down swipe for Good/Hard grades
Add haptic feedback on swipe

Closes #123
```

```
fix(sync): prevent duplicate reviews on sync failure

Add transaction rollback on sync error
Mark reviews as synced only after server confirmation

Fixes #456
```

## Pull Request Process

### Before Submitting

1. ✅ All tests pass
2. ✅ Code is formatted (Prettier)
3. ✅ No linting errors
4. ✅ TypeScript compiles
5. ✅ Documentation updated
6. ✅ Commits follow convention
7. ✅ Branch is up to date with main

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] Tested on iOS
- [ ] Tested on Android

## Screenshots (if applicable)
[Add screenshots]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added and passing

## Related Issues
Closes #123
```

### Review Process

1. Automated checks must pass
2. At least one approval required
3. Address all review comments
4. Resolve merge conflicts
5. Squash commits if needed
6. Maintainer will merge

## Issue Reporting

### Bug Reports

Include:
- Clear, descriptive title
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots/videos
- Device and OS version
- App version
- Error logs

### Feature Requests

Include:
- Clear, descriptive title
- Problem to solve
- Proposed solution
- Alternative solutions considered
- Additional context

### Issue Template

```markdown
**Describe the bug/feature**
Clear description

**Steps to Reproduce** (for bugs)
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior** (for bugs)
What actually happens

**Screenshots**
If applicable

**Environment**
- Device: [e.g. iPhone 14 Pro]
- OS: [e.g. iOS 16.4]
- App Version: [e.g. 1.0.0]

**Additional Context**
Any other information
```

## Communication

- GitHub Issues: Bug reports and feature requests
- Pull Requests: Code review discussions
- Email: Team communication
- Slack: Quick questions (if applicable)

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project README

## Questions?

If you have questions:
1. Check existing documentation
2. Search closed issues
3. Open a new discussion
4. Contact maintainers

Thank you for contributing! 🎉
