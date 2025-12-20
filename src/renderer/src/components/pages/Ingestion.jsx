import React, { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Upload, 
  Link, 
  Video, 
  FileText, 
  X, 
  Play, 
  Pause,
  CheckCircle,
  AlertCircle,
  Loader
} from 'lucide-react'
import useStore from '../../store/useStore'
import clsx from 'clsx'

const Ingestion = () => {
  const { 
    ingestion, 
    startIngestion, 
    updateIngestionProgress, 
    completeIngestion, 
    failIngestion,
    addNotification 
  } = useStore()

  const [inputMethod, setInputMethod] = useState('file')
  const [inputValue, setInputValue] = useState('')
  const [ingestConfig, setIngestConfig] = useState({
    chunkSize: 1000,
    overlap: 100,
    generateQuiz: true,
    generateMindMap: false
  })

  const inputMethods = [
    {
      id: 'file',
      title: 'File Upload',
      description: 'Upload PDF, TXT, or MD files',
      icon: FileText,
      placeholder: 'Select a file to upload...'
    },
    {
      id: 'url',
      title: 'URL',
      description: 'Import content from web pages',
      icon: Link,
      placeholder: 'Enter website URL...'
    },
    {
      id: 'video',
      title: 'Video Link',
      description: 'Extract content from videos',
      icon: Video,
      placeholder: 'Enter video URL (YouTube, Vimeo...)'
    }
  ]

  const simulateIngestion = useCallback(async () => {
    if (!inputValue.trim()) {
      addNotification({
        type: 'error',
        title: 'Input Required',
        message: 'Please provide content to ingest.'
      })
      return
    }

    const job = {
      id: Date.now().toString(),
      method: inputMethod,
      source: inputValue,
      config: ingestConfig,
      startTime: new Date().toISOString()
    }

    startIngestion(job)

    // Simulate ingestion progress
    const steps = [
      { progress: 10, status: 'Analyzing content...' },
      { progress: 25, status: 'Parsing text...' },
      { progress: 40, status: 'Splitting into chunks...' },
      { progress: 60, status: 'Generating embeddings...' },
      { progress: 80, status: 'Creating cards...' },
      { progress: 90, status: 'Generating quiz questions...' },
      { progress: 95, status: 'Finalizing...' },
      { progress: 100, status: 'Completed' }
    ]

    for (const step of steps) {
      await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000))
      
      if (step.status === 'Completed') {
        completeIngestion()
        addNotification({
          type: 'success',
          title: 'Ingestion Complete',
          message: `Successfully processed ${inputValue.split('/').pop()}. Created 15 new cards.`
        })
      } else {
        updateIngestionProgress(step.progress, step.status)
      }
    }

    // Reset form
    setInputValue('')
  }, [inputMethod, inputValue, ingestConfig, startIngestion, updateIngestionProgress, completeIngestion, addNotification])

  const handleFileSelect = () => {
    // Simulate file selection
    const mockFileName = 'sample-document.pdf'
    setInputValue(mockFileName)
    addNotification({
      type: 'info',
      title: 'File Selected',
      message: `${mockFileName} ready for ingestion`
    })
  }

  const cancelIngestion = () => {
    failIngestion('Cancelled by user')
    addNotification({
      type: 'warning',
      title: 'Ingestion Cancelled',
      message: 'Content ingestion was cancelled.'
    })
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6 h-full overflow-y-auto custom-scrollbar">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          Content Ingestion
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Import learning content from various sources to create interactive study materials
        </p>
      </motion.div>

      {/* Input Methods */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card"
      >
        <div className="card-header">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Choose Input Method
          </h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {inputMethods.map((method) => {
              const Icon = method.icon
              return (
                <button
                  key={method.id}
                  onClick={() => setInputMethod(method.id)}
                  className={clsx(
                    'p-4 rounded-lg border-2 transition-all duration-150 text-left',
                    inputMethod === method.id
                      ? 'border-primary bg-primary/5'
                      : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                  )}
                >
                  <div className="flex items-center space-x-3 mb-2">
                    <Icon className={clsx(
                      'w-6 h-6',
                      inputMethod === method.id ? 'text-primary' : 'text-gray-500 dark:text-gray-400'
                    )} />
                    <h3 className="font-medium text-gray-900 dark:text-gray-100">
                      {method.title}
                    </h3>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {method.description}
                  </p>
                </button>
              )
            })}
          </div>

          {/* Input Field */}
          <div className="space-y-4">
            <div className="flex space-x-2">
              <div className="flex-1">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder={inputMethods.find(m => m.id === inputMethod)?.placeholder}
                  className="input"
                  disabled={ingestion.isActive}
                />
              </div>
              
              {inputMethod === 'file' && (
                <button
                  onClick={handleFileSelect}
                  disabled={ingestion.isActive}
                  className="btn btn-secondary"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Browse
                </button>
              )}
            </div>

            {/* Advanced Configuration */}
            <details className="group">
              <summary className="cursor-pointer text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100">
                Advanced Configuration
              </summary>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Chunk Size
                  </label>
                  <input
                    type="number"
                    value={ingestConfig.chunkSize}
                    onChange={(e) => setIngestConfig({...ingestConfig, chunkSize: parseInt(e.target.value)})}
                    className="input"
                    min="100"
                    max="5000"
                    disabled={ingestion.isActive}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Overlap
                  </label>
                  <input
                    type="number"
                    value={ingestConfig.overlap}
                    onChange={(e) => setIngestConfig({...ingestConfig, overlap: parseInt(e.target.value)})}
                    className="input"
                    min="0"
                    max="500"
                    disabled={ingestion.isActive}
                  />
                </div>
                <div className="md:col-span-2 space-y-2">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={ingestConfig.generateQuiz}
                      onChange={(e) => setIngestConfig({...ingestConfig, generateQuiz: e.target.checked})}
                      disabled={ingestion.isActive}
                      className="rounded border-gray-300 text-primary focus:ring-primary"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      Generate quiz questions
                    </span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={ingestConfig.generateMindMap}
                      onChange={(e) => setIngestConfig({...ingestConfig, generateMindMap: e.target.checked})}
                      disabled={ingestion.isActive}
                      className="rounded border-gray-300 text-primary focus:ring-primary"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      Generate mind map
                    </span>
                  </label>
                </div>
              </div>
            </details>

            {/* Action Buttons */}
            <div className="flex space-x-3">
              {!ingestion.isActive ? (
                <button
                  onClick={simulateIngestion}
                  disabled={!inputValue.trim()}
                  className="btn btn-primary flex-1"
                >
                  <Play className="w-4 h-4 mr-2" />
                  Start Ingestion
                </button>
              ) : (
                <button
                  onClick={cancelIngestion}
                  className="btn btn-error flex-1"
                >
                  <Pause className="w-4 h-4 mr-2" />
                  Cancel Ingestion
                </button>
              )}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Progress Section */}
      <AnimatePresence>
        {ingestion.isActive && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="card"
          >
            <div className="card-body">
              <div className="space-y-4">
                {/* Status */}
                <div className="flex items-center space-x-3">
                  <Loader className="w-5 h-5 text-primary animate-spin" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">
                      {ingestion.status || 'Processing...'}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {ingestion.currentJob?.source}
                    </p>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Progress</span>
                    <span className="text-gray-900 dark:text-gray-100">
                      {Math.round(ingestion.progress)}%
                    </span>
                  </div>
                  <div className="progress">
                    <motion.div
                      className="progress-bar"
                      initial={{ width: 0 }}
                      animate={{ width: `${ingestion.progress}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-primary">
                      {Math.round((ingestion.progress / 100) * 15)}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Cards Created
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-success">
                      {ingestConfig.generateQuiz ? Math.round((ingestion.progress / 100) * 8) : 0}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Quiz Questions
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-warning">
                      {ingestConfig.generateMindMap ? Math.round((ingestion.progress / 100) * 1) : 0}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Mind Maps
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Success State */}
      <AnimatePresence>
        {ingestion.status === 'completed' && !ingestion.isActive && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="card border-success bg-success/5"
          >
            <div className="card-body">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-6 h-6 text-success" />
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    Ingestion Completed Successfully!
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Your content has been processed and is ready for review.
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error State */}
      <AnimatePresence>
        {ingestion.status === 'failed' && !ingestion.isActive && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="card border-error bg-error/5"
          >
            <div className="card-body">
              <div className="flex items-center space-x-3">
                <AlertCircle className="w-6 h-6 text-error" />
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    Ingestion Failed
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {ingestion.error || 'An unknown error occurred during processing.'}
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Help Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card"
      >
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Supported Formats
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Documents</h4>
              <ul className="space-y-1 text-gray-600 dark:text-gray-400">
                <li>• PDF files</li>
                <li>• Plain text (.txt)</li>
                <li>• Markdown (.md)</li>
                <li>• Word documents (.docx)</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Web Content</h4>
              <ul className="space-y-1 text-gray-600 dark:text-gray-400">
                <li>• Blog posts</li>
                <li>• Documentation</li>
                <li>• Articles</li>
                <li>• Wikipedia pages</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Video Content</h4>
              <ul className="space-y-1 text-gray-600 dark:text-gray-400">
                <li>• YouTube videos</li>
                <li>• Vimeo videos</li>
                <li>• Educational content</li>
                <li>• Lectures & tutorials</li>
              </ul>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default Ingestion
