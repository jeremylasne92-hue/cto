import React from 'react'
import { motion } from 'framer-motion'
import useStore from '../../store/useStore'
import Sidebar from './Sidebar'
import TopBar from './TopBar'

const MainLayout = ({ children }) => {
  const { sidebarOpen } = useStore()

  return (
    <div className="flex h-screen bg-background-light dark:bg-background-dark overflow-hidden">
      {/* Sidebar */}
      <motion.div
        className={`${sidebarOpen ? 'w-64' : 'w-16'} transition-all duration-300 ease-in-out flex-shrink-0`}
        animate={{ width: sidebarOpen ? 256 : 64 }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
      >
        <Sidebar />
      </motion.div>

      {/* Main content area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <TopBar />

        {/* Main content */}
        <main 
          id="main-content"
          className="flex-1 overflow-auto custom-scrollbar bg-background-light dark:bg-background-dark"
          role="main"
          aria-label="Main content"
        >
          <div className="h-full">
            {children}
          </div>
        </main>
      </div>

      {/* Accessibility skip links */}
      <div className="sr-only">
        <a href="#sidebar" className="skip-link">Skip to sidebar navigation</a>
        <a href="#main-content" className="skip-link">Skip to main content</a>
        <a href="#top-bar" className="skip-link">Skip to top bar</a>
      </div>
    </div>
  )
}

export default MainLayout
