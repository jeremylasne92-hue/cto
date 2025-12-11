import React from 'react'
import { motion } from 'framer-motion'
import { 
  User, 
  Bell, 
  Sync, 
  Wifi, 
  WifiOff,
  Moon,
  Sun,
  Volume2,
  VolumeX
} from 'lucide-react'
import useStore from '../../store/useStore'
import clsx from 'clsx'

const TopBar = () => {
  const { 
    theme, 
    setTheme, 
    stats, 
    settings,
    ingestion,
    notifications 
  = useStore()

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light')
  }

  const hasUnreadNotifications = notifications.length > 0

  return (
    <header 
      id="top-bar"
      className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6"
      role="banner"
    >
      {/* Left side - Quick stats and status */}
      <div className="flex items-center space-x-6">
        {/* Cards reviewed today */}
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-success rounded-full"></div>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {stats.cardsReviewedToday} cards today
          </span>
        </div>

        {/* Current streak */}
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-primary rounded-full"></div>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {stats.currentStreak} day streak
          </span>
        </div>

        {/* Ingestion status */}
        {ingestion.isActive && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center space-x-2 px-3 py-1 bg-warning/10 text-warning rounded-lg"
          >
            <Sync className="w-4 h-4 animate-spin" />
            <span className="text-sm font-medium">
              Ingesting... {Math.round(ingestion.progress)}%
            </span>
          </motion.div>
        )}
      </div>

      {/* Right side - Controls */}
      <div className="flex items-center space-x-3">
        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
        >
          {theme === 'light' ? (
            <Moon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          ) : (
            <Sun className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          )}
        </button>

        {/* Sound toggle */}
        <button
          className={clsx(
            "p-2 rounded-lg transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
            settings.soundEnabled 
              ? "hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400" 
              : "text-gray-400 dark:text-gray-600"
          )}
          aria-label={settings.soundEnabled ? 'Disable sounds' : 'Enable sounds'}
        >
          {settings.soundEnabled ? (
            <Volume2 className="w-5 h-5" />
          ) : (
            <VolumeX className="w-5 h-5" />
          )}
        </button>

        {/* Sync status */}
        <div className="flex items-center space-x-2">
          <Wifi className="w-5 h-5 text-success" />
          <span className="text-sm text-gray-600 dark:text-gray-400">
            Synced
          </span>
        </div>

        {/* Notifications */}
        <div className="relative">
          <button
            className={clsx(
              "p-2 rounded-lg transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
              hasUnreadNotifications 
                ? "hover:bg-gray-100 dark:hover:bg-gray-700 text-primary" 
                : "hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400"
            )}
            aria-label={`Notifications ${hasUnreadNotifications ? `(${notifications.length} new)` : ''}`}
          >
            <Bell className="w-5 h-5" />
            {hasUnreadNotifications && (
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-1 -right-1 w-5 h-5 bg-error text-white text-xs rounded-full flex items-center justify-center font-medium"
              >
                {notifications.length > 9 ? '9+' : notifications.length}
              </motion.span>
            )}
          </button>
        </div>

        {/* User menu */}
        <div className="relative">
          <button
            className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
            aria-label="User menu"
          >
            <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
            <div className="hidden md:block text-left">
              <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                Student
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                {stats.totalXP} XP
              </div>
            </div>
          </button>
        </div>
      </div>

      {/* Accessibility announcements */}
      <div className="sr-only" aria-live="polite">
        {ingestion.isActive && `Ingestion in progress: ${Math.round(ingestion.progress)} percent complete`}
      </div>
    </header>
  )
}

export default TopBar
