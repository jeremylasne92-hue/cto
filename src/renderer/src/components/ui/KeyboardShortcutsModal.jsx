import React, { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Keyboard } from 'lucide-react'

const KeyboardShortcutsModal = () => {
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    const handleGlobalKeyDown = (event) => {
      // Close modal with Escape
      if (event.key === 'Escape' && isOpen) {
        setIsOpen(false)
      }
      
      // Open shortcuts modal with F1
      if (event.key === 'F1') {
        event.preventDefault()
        setIsOpen(true)
      }
    }

    document.addEventListener('keydown', handleGlobalKeyDown)
    return () => document.removeEventListener('keydown', handleGlobalKeyDown)
  }, [isOpen])

  useEffect(() => {
    // Check if modal should be open based on URL hash or other conditions
    if (window.location.hash === '#shortcuts') {
      setIsOpen(true)
    }
  }, [])

  const shortcuts = [
    {
      category: 'Navigation',
      items: [
        { key: 'F1', description: 'Show keyboard shortcuts' },
        { key: 'Ctrl+1-6', description: 'Navigate to main sections' },
        { key: 'Ctrl+,', description: 'Open settings' },
        { key: 'Esc', description: 'Close modal or cancel action' }
      ]
    },
    {
      category: 'Review Session',
      items: [
        { key: 'Space', description: 'Show card answer' },
        { key: '1-4', description: 'Grade card (1=Again, 2=Hard, 3=Good, 4=Easy)' },
        { key: 'Enter', description: 'Submit answer in quiz' },
        { key: 'Ctrl+P', description: 'Pause/resume session' },
        { key: 'Ctrl+E', description: 'End session' }
      ]
    },
    {
      category: 'General',
      items: [
        { key: 'Ctrl+S', description: 'Save current work' },
        { key: 'Ctrl+N', description: 'New deck' },
        { key: 'Ctrl+O', description: 'Import content' },
        { key: 'Ctrl+T', description: 'Toggle theme' },
        { key: 'Ctrl+/', description: 'Focus search' }
      ]
    }
  ]

  const KeyComponent = ({ children }) => (
    <kbd className="inline-flex items-center px-2 py-1 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded text-xs font-mono font-medium text-gray-800 dark:text-gray-200">
      {children}
    </kbd>
  )

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="modal-overlay"
            onClick={() => setIsOpen(false)}
            aria-hidden="true"
          />

          {/* Modal */}
          <div className="modal-content" role="dialog" aria-modal="true" aria-labelledby="shortcuts-title">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ duration: 0.2 }}
              className="modal-panel max-w-2xl w-full"
            >
              {/* Header */}
              <div className="card-header flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Keyboard className="w-5 h-5 text-primary" />
                  <h2 id="shortcuts-title" className="text-lg font-semibold">
                    Keyboard Shortcuts
                  </h2>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
                  aria-label="Close shortcuts modal"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Content */}
              <div className="card-body max-h-96 overflow-y-auto custom-scrollbar">
                <div className="space-y-6">
                  {shortcuts.map((category, categoryIndex) => (
                    <div key={category.category}>
                      <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
                        {category.category}
                      </h3>
                      <div className="space-y-2">
                        {category.items.map((item, itemIndex) => (
                          <div
                            key={`${categoryIndex}-${itemIndex}`}
                            className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50"
                          >
                            <span className="text-sm text-gray-700 dark:text-gray-300">
                              {item.description}
                            </span>
                            <div className="flex items-center space-x-1">
                              {item.key.split('+').map((key, keyIndex) => (
                                <React.Fragment key={keyIndex}>
                                  <KeyComponent>{key}</KeyComponent>
                                  {keyIndex < item.key.split('+').length - 1 && (
                                    <span className="text-gray-400">+</span>
                                  )}
                                </React.Fragment>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Footer */}
              <div className="card-footer flex items-center justify-between">
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Press <KeyComponent>Esc</KeyComponent> to close this dialog
                </p>
                <button
                  onClick={() => setIsOpen(false)}
                  className="btn btn-primary btn-sm"
                >
                  Got it
                </button>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  )
}

export default KeyboardShortcutsModal
