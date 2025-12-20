import React from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  LayoutDashboard, 
  BookOpen, 
  Upload, 
  RotateCcw, 
  Settings, 
  Info,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import useStore from '../../store/useStore'
import clsx from 'clsx'

const navigationItems = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    path: '/dashboard',
    description: 'Overview and statistics'
  },
  {
    id: 'decks',
    label: 'Decks',
    icon: BookOpen,
    path: '/decks',
    description: 'Manage your card decks'
  },
  {
    id: 'ingestion',
    label: 'Ingestion',
    icon: Upload,
    path: '/ingestion',
    description: 'Import content for learning'
  },
  {
    id: 'review',
    label: 'Review',
    icon: RotateCcw,
    path: '/review',
    description: 'Start review session'
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: Settings,
    path: '/settings',
    description: 'App configuration'
  },
  {
    id: 'about',
    label: 'About',
    icon: Info,
    path: '/about',
    description: 'App information'
  }
]

const Sidebar = () => {
  const { sidebarOpen, setSidebarOpen } = useStore()
  const location = useLocation()

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen)

  return (
    <div className="h-full bg-surface-light dark:bg-surface-dark border-r border-gray-200 dark:border-gray-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <motion.div
          className="flex items-center space-x-3"
          animate={{ opacity: sidebarOpen ? 1 : 0 }}
          transition={{ duration: 0.2 }}
        >
          {sidebarOpen && (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">LP</span>
              </div>
              <div>
                <h1 className="font-semibold text-gray-900 dark:text-gray-100">
                  Learning Platform
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Desktop Edition
                </p>
              </div>
            </div>
          )}
        </motion.div>

        {/* Toggle button */}
        <button
          onClick={toggleSidebar}
          className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
        >
          {sidebarOpen ? (
            <ChevronLeft className="w-4 h-4 text-gray-600 dark:text-gray-400" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-600 dark:text-gray-400" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav 
        id="sidebar"
        className="flex-1 p-4 space-y-2 overflow-y-auto custom-scrollbar"
        role="navigation"
        aria-label="Main navigation"
      >
        {navigationItems.map((item) => {
          const isActive = location.pathname === item.path
          const Icon = item.icon

          return (
            <NavLink
              key={item.id}
              to={item.path}
              className={({ isActive }) => clsx(
                'nav-item group relative',
                isActive ? 'nav-item-active' : 'nav-item-inactive'
              )}
              title={!sidebarOpen ? item.label : undefined}
              aria-label={item.label}
              aria-current={isActive ? 'page' : undefined}
            >
              <Icon 
                className={clsx(
                  'w-5 h-5 flex-shrink-0',
                  sidebarOpen ? 'mr-3' : 'mx-auto'
                )} 
              />
              {sidebarOpen && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2, delay: 0.1 }}
                  className="flex-1 min-w-0"
                >
                  <div className="font-medium truncate">{item.label}</div>
                  <div className="text-xs opacity-75 truncate">
                    {item.description}
                  </div>
                </motion.div>
              )}

              {/* Tooltip for collapsed state */}
              {!sidebarOpen && (
                <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-sm rounded-md opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50">
                  {item.label}
                  <div className="absolute right-full top-1/2 transform -translate-y-1/2 border-4 border-transparent border-r-gray-900 dark:border-r-gray-100" />
                </div>
              )}
            </NavLink>
          )
        })}
      </nav>

      {/* Footer */}
      {sidebarOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="p-4 border-t border-gray-200 dark:border-gray-700"
        >
          <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
            <div>Version 1.0.0</div>
            <div className="mt-1">© 2024 Learning Platform</div>
          </div>
        </motion.div>
      )}
    </div>
  )
}

export default Sidebar
