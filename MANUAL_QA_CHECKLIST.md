# Cognisphere Desktop - Manual QA Checklist

Use this checklist to manually verify that all features of the Review UI Dashboard work correctly in the Electron application.

## 🚀 Application Launch

- [ ] **Application Starts Successfully**
  - [ ] Electron window opens without errors
  - [ ] React application loads properly
  - [ ] No console errors in Developer Tools
  - [ ] Application window is resizable

- [ ] **Dark Mode Toggle**
  - [ ] Dark mode toggle button visible in header and sidebar
  - [ ] Clicking toggle switches between light and dark themes
  - [ ] Theme preference persists across application restart
  - [ ] All components properly styled in both themes

## 📊 Dashboard Testing

- [ ] **Dashboard Page Loads**
  - [ ] Dashboard displays at application startup
  - [ ] All statistics cards show data (even if mock data)
  - [ ] Progress bars animate correctly
  - [ ] Charts render without errors

- [ ] **Statistics Display**
  - [ ] "Cards Due Today" shows a number
  - [ ] "Current Streak" displays days count
  - [ ] "Retention Rate" shows percentage with trend
  - [ ] "Total Study Time" displays in hours/minutes

- [ ] **Interactive Charts**
  - [ ] Retention rate line chart displays 7-day data
  - [ ] Pie chart shows deck distribution with colors
  - [ ] Hovering over chart elements shows tooltips
  - [ ] Charts are responsive to window resizing

- [ ] **Progress Tracking**
  - [ ] "Today's Progress" section shows progress bars
  - [ ] Cards reviewed vs total shows percentage
  - [ ] Time spent progress bar updates correctly
  - [ ] "Start Review Session" button is visible and enabled

- [ ] **Quick Actions**
  - [ ] "Create New Deck" button is clickable
  - [ ] "Import Cards" button functions
  - [ ] "View Reports" button works
  - [ ] All buttons have appropriate hover states

## 🃏 Review Workspace Testing

- [ ] **Navigation to Review**
  - [ ] "Review" tab in sidebar is clickable
  - [ ] Dashboard "Start Review Session" button navigates correctly
  - [ ] Review workspace loads with card display

- [ ] **Card Presentation**
  - [ ] Front side of card displays readable text
  - [ ] Card is properly sized and centered
  - [ ] "Show Answer" button is prominent and clickable
  - [ ] Keyboard shortcut (Space/Enter) shows answer

- [ ] **Answer Display**
  - [ ] Back side reveals correct answer
  - [ ] Answer is clearly formatted and readable
  - [ ] Four grading buttons appear: Again, Hard, Good, Easy
  - [ ] Buttons are color-coded appropriately

- [ ] **FSRS Grading System**
  - [ ] Clicking "Again" (red) processes response
  - [ ] Clicking "Hard" (orange) processes response
  - [ ] Clicking "Good" (green) processes response
  - [ ] Clicking "Easy" (blue) processes response
  - [ ] Toast notifications appear after each rating

- [ ] **Keyboard Shortcuts**
  - [ ] Key "1" triggers "Again" rating
  - [ ] Key "2" triggers "Hard" rating
  - [ ] Key "3" triggers "Good" rating
  - [ ] Key "4" triggers "Easy" rating
  - [ ] Space/Enter shows answer when hidden

- [ ] **Timer Functionality**
  - [ ] Response timer starts when card loads
  - [ ] Timer displays in MM:SS format
  - [ ] Timer resets for each new card
  - [ ] Timer continues through answer display

- [ ] **Progress Tracking**
  - [ ] Progress bar updates as cards are reviewed
  - [ ] "Card X of Y" counter displays correctly
  - [ ] "Cards remaining" counter updates accurately
  - [ ] Session completion message appears when queue empty

- [ ] **Session Management**
  - [ ] Session starts automatically when entering review
  - [ ] Session statistics are calculated correctly
  - [ ] Session completion toast appears when done
  - [ ] Session data persists appropriately

## 🧠 Quiz Viewer Testing

- [ ] **Quiz Navigation**
  - [ ] "Quiz" tab in sidebar is accessible
  - [ ] Quiz viewer loads with quiz selection
  - [ ] Available quizzes display as tabs

- [ ] **Quiz Selection**
  - [ ] Multiple quizzes can be created/available
  - [ ] Quiz tab switching works smoothly
  - [ ] Quiz metadata displays (question count, difficulty)

- [ ] **Question Presentation**
  - [ ] Question text is clear and readable
  - [ ] Multiple choice options display properly
  - [ ] Difficulty badges are visible and colored
  - [ ] Progress indicator shows current question

- [ ] **Answer Interaction**
  - [ ] Radio buttons select answers correctly
  - [ ] "Next Question" advances properly
  - [ ] "Previous Question" goes back correctly
  - [ ] Answer validation prevents incomplete submission

- [ ] **Quiz Submission**
  - [ ] "Submit Quiz" button enables when all answered
  - [ ] Results page displays score correctly
  - [ ] Individual question review shows correct/incorrect
  - [ ] Correct answers display with explanations

- [ ] **Results Analysis**
  - [ ] Final score percentage calculates correctly
  - [ ] Each question shows user answer vs correct answer
  - [ ] Color coding indicates correct (green) vs incorrect (red)
  - [ ] "Retake Quiz" button resets for retry

## 🗺️ Mind Map Viewer Testing

- [ ] **Mind Map Navigation**
  - [ ] "Mind Maps" tab loads properly
  - [ ] Available mind maps list in sidebar
  - [ ] Mind map selection changes display

- [ ] **Mind Map Visualization**
  - [ ] Nodes display as colored boxes with text
  - [ ] Connections between nodes show as lines
  - [ ] Root node is prominently displayed
  - [ ] Node positioning is logical and readable

- [ ] **Node Interaction**
  - [ ] Clicking nodes expands/collapses children
  - [ ] Expanded nodes show all connected children
  - [ ] Collapsed nodes hide child connections
  - [ ] Node selection highlights the node

- [ ] **Node Editing**
  - [ ] Edit button (pencil icon) is visible on nodes
  - [ ] Clicking edit allows content modification
  - [ ] Save/Cancel functionality works correctly
  - [ ] Changes persist and display immediately

- [ ] **Zoom Controls**
  - [ ] Zoom in button increases scale
  - [ ] Zoom out button decreases scale
  - [ ] Reset zoom returns to 100%
  - [ ] Scale indicator updates correctly
  - [ ] Zoom limits prevent extreme scaling

- [ ] **Node Details**
  - [ ] Selected node shows details panel
  - [ ] Node content displays in details
  - [ ] Children count and expanded state shown
  - [ ] Details panel updates with node selection

- [ ] **Export Functionality**
  - [ ] Export button triggers download
  - [ ] JSON file downloads with mind map data
  - [ ] Export includes all node information
  - [ ] File name follows convention

## 🔧 Technical Testing

- [ ] **Offline Mode**
  - [ ] Disconnect network and verify "Offline Mode" badge
  - [ ] All functionality works with local data
  - [ ] Reconnect network and verify "Online" status
  - [ ] Data synchronization occurs properly

- [ ] **Error Handling**
  - [ ] Network errors show appropriate messages
  - [ ] Missing data handled gracefully
  - [ ] Invalid responses don't crash application
  - [ ] User-friendly error messages display

- [ ] **Performance**
  - [ ] Application starts within 3 seconds
  - [ ] Page transitions are smooth (< 200ms)
  - [ ] Large datasets don't cause lag
  - [ ] Memory usage remains stable during use

- [ ] **Responsive Design**
  - [ ] Window resizing maintains layout integrity
  - [ ] Sidebar collapses on smaller windows
  - [ ] Mobile drawer works on narrow screens
  - [ ] Charts adapt to available space

## ⌨️ Keyboard Navigation

- [ ] **Global Shortcuts**
  - [ ] Tab navigation works through all interactive elements
  - [ ] Enter activates focused buttons
  - [ ] Escape closes modals/dropdowns
  - [ ] Arrow keys navigate within components

- [ ] **Review Workspace Shortcuts**
  - [ ] Space shows answer (when hidden)
  - [ ] 1-4 keys trigger rating buttons
  - [ ] Arrow keys navigate between cards (if implemented)
  - [ ] ESC cancels current operation (if applicable)

## 📱 Electron-Specific Testing

- [ ] **Window Management**
  - [ ] Window can be resized in all directions
  - [ ] Minimize/maximize/restore work correctly
  - [ ] Window remembers size/position between sessions
  - [ ] Close button terminates application properly

- [ ] **Menu System**
  - [ ] Application menu appears (File, View)
  - [ ] Menu items function appropriately
  - [ ] Keyboard shortcuts work in menus
  - [ ] Dark mode toggle in menu (if implemented)

- [ ] **IPC Communication**
  - [ ] Frontend can communicate with main process
  - [ ] FSRS responses are properly submitted
  - [ ] File operations work (save dialog, if implemented)
  - [ ] Version information displays correctly

## 🔍 Data Integrity

- [ ] **State Persistence**
  - [ ] Theme preference saves between sessions
  - [ ] Study progress persists appropriately
  - [ ] Quiz results are maintained
  - [ ] User settings remain consistent

- [ ] **Data Synchronization**
  - [ ] Local state updates reflect immediately
  - [ ] Backend communication updates UI
  - [ ] Optimistic updates work correctly
  - [ ] Error states don't corrupt data

## 🎨 Visual Quality

- [ ] **Design Consistency**
  - [ ] All buttons follow same styling pattern
  - [ ] Color scheme is consistent throughout
  - [ ] Typography is readable and uniform
  - [ ] Icons align properly with text

- [ ] **Accessibility**
  - [ ] High contrast ratios in both themes
  - [ ] Focus indicators visible on all interactive elements
  - [ ] Screen reader compatible (basic testing)
  - [ ] Keyboard navigation works completely

- [ ] **Animation Quality**
  - [ ] Smooth transitions between states
  - [ ] Progress bars animate appropriately
  - [ ] Loading spinners function correctly
  - [ ] Hover states provide clear feedback

## 📋 End-to-End Testing

- [ ] **Complete Study Session**
  1. Open application and verify dashboard loads
  2. Check today's progress and start review session
  3. Review at least 3 cards with different ratings
  4. Verify progress updates and session statistics
  5. Complete session and return to dashboard
  6. Confirm dashboard stats reflect session results

- [ ] **Multi-Feature Workflow**
  1. Start on dashboard and review progress
  2. Take a quiz and complete it successfully
  3. Explore a mind map and interact with nodes
  4. Switch back to dashboard and verify all data updated
  5. Toggle dark mode and ensure all views adapt
  6. Close application and restart to verify persistence

## 🚨 Known Issues & Limitations

- [ ] Backend API is currently mocked for development
- [ ] Real FSRS algorithm integration pending backend
- [ ] Some mind map editing features may be basic
- [ ] Export functionality limited to JSON format
- [ ] Performance with very large datasets untested

## 📝 Test Results Recording

For each test item, mark:
- ✅ **PASS**: Feature works as expected
- ❌ **FAIL**: Feature doesn't work or has issues
- ⚠️ **PARTIAL**: Feature works with limitations
- ⏭️ **SKIP**: Test not applicable or couldn't be completed

### Critical Issues Found:
[List any critical bugs or issues that prevent normal operation]

### Enhancement Suggestions:
[List any suggestions for improving user experience or functionality]

### Overall Assessment:
[Provide overall quality assessment and readiness for production use]
