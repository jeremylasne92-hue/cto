import React, { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import useStore from './store/useStore'

// Layout components
import MainLayout from './components/layout/MainLayout'

// Page components
import Dashboard from './components/pages/Dashboard'
import Decks from './components/pages/Decks'
import Ingestion from './components/pages/Ingestion'
import Review from './components/pages/Review'
import Settings from './components/pages/Settings'
import About from './components/pages/About'

// UI components
import NotificationToast from './components/ui/NotificationToast'
import KeyboardShortcutsModal from './components/ui/KeyboardShortcutsModal'

function App() {
  const { theme, setTheme, addNotification, removeNotification, notifications } = useStore()

  useEffect(() => {
    // Initialize theme from system preference if not set
    if (!localStorage.getItem('learning-platform-store')) {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      setTheme(prefersDark ? 'dark' : 'light')
    }

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = (e) => {
      if (useStore.getState().theme === 'auto') {
        setTheme(e.matches ? 'dark' : 'light')
      }
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [setTheme])

  useEffect(() => {
    // Listen for menu events from main process
    const handleMenuEvent = (event, data) => {
      switch (data) {
        case 'menu-new-deck':
          // Handle new deck creation
          addNotification({
            type: 'info',
            title: 'Create New Deck',
            message: 'Opening new deck dialog...'
          })
          break
        case 'menu-import-file':
          addNotification({
            type: 'info',
            title: 'Import Content',
            message: 'Opening file import dialog...'
          })
          break
        case 'menu-about':
          addNotification({
            type: 'info',
            title: 'About Learning Platform',
            message: 'Version 1.0.0 - Desktop Edition'
          })
          break
        case 'menu-shortcuts':
          // Show keyboard shortcuts modal
          document.getElementById('shortcuts-modal')?.classList.remove('hidden')
          break
        default:
          break
      }
    }

    // Setup IPC listener if electronAPI is available
    if (window.electronAPI?.onMenuEvent) {
      window.electronAPI.onMenuEvent(handleMenuEvent)
    }

    return () => {
      if (window.electronAPI?.removeAllListeners) {
        window.electronAPI.removeAllListeners('menu-event')
      }
    }
  }, [addNotification])

  return (
    <div className={`app ${theme === 'dark' ? 'dark' : 'light'}`}>
      {/* Skip link for accessibility */}
      <a 
        href="#main-content" 
        className="skip-link"
        tabIndex={1}
      >
        Skip to main content
      </a>

      {/* Main application layout */}
      <MainLayout>
        <AnimatePresence mode="wait">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route 
              path="/dashboard" 
              element={
                <motion.div
                  key="dashboard"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Dashboard />
                </motion.div>
              } 
            />
            <Route 
              path="/decks" 
              element={
                <motion.div
                  key="decks"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Decks />
                </motion.div>
              } 
            />
            <Route 
              path="/ingestion" 
              element={
                <motion.div
                  key="ingestion"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Ingestion />
                </motion.div>
              } 
            />
            <Route 
              path="/review" 
              element={
                <motion.div
                  key="review"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Review />
                </motion.div>
              } 
            />
            <Route 
              path="/settings" 
              element={
                <motion.div
                  key="settings"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Settings />
                </motion.div>
              } 
            />
            <Route 
              path="/about" 
              element={
                <motion.div
                  key="about"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <About />
                </motion.div>
              } 
            />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </AnimatePresence>
      </MainLayout>

      {/* UI Overlays */}
      <AnimatePresence>
        {notifications.map(notification => (
          <NotificationToast
            key={notification.id}
            notification={notification}
            onClose={() => removeNotification(notification.id)}
          />
        ))}
      </AnimatePresence>

      <KeyboardShortcutsModal />

      {/* Screen reader announcements */}
      <div 
        id="live-region" 
        aria-live="polite" 
        aria-atomic="true" 
        className="sr-only"
      />
    </div>
  )
}

export default App
