import React from 'react'
import { motion } from 'framer-motion'
import { 
  Info, 
  Heart, 
  Code, 
  Book, 
  Mail, 
  Github, 
  Globe,
  Award,
  Users,
  Star,
  ExternalLink,
  Download,
  Cpu,
  HardDrive
} from 'lucide-react'
import useStore from '../../store/useStore'

const About = () => {
  const { stats } = useStore()

  const features = [
    {
      icon: Book,
      title: 'Smart Content Ingestion',
      description: 'Import from PDFs, websites, videos, and documents with AI-powered processing'
    },
    {
      icon: Cpu,
      title: 'Local AI Processing',
      description: 'Run language models locally for privacy and offline capability'
    },
    {
      icon: Award,
      title: 'Adaptive Learning',
      description: 'Personalized spaced repetition algorithm for optimal retention'
    },
    {
      icon: Star,
      title: 'Interactive Content',
      description: 'Flashcards, quizzes, and mind maps for engaging learning experiences'
    }
  ]

  const techStack = [
    { name: 'Electron', description: 'Cross-platform desktop framework', version: 'v28.0.0' },
    { name: 'React', description: 'Modern UI library', version: 'v18.2.0' },
    { name: 'Framer Motion', description: 'Animation library', version: 'v10.16.4' },
    { name: 'Tailwind CSS', description: 'Utility-first CSS framework', version: 'v3.3.3' },
    { name: 'Zustand', description: 'State management', version: 'v4.4.1' },
    { name: 'D3.js', description: 'Data visualization', version: 'v7.8.5' }
  ]

  const systemInfo = {
    platform: window.electronAPI?.platform || 'Unknown',
    electronVersion: window.electronAPI?.versions?.electron || 'Unknown',
    chromeVersion: window.electronAPI?.versions?.chrome || 'Unknown',
    nodeVersion: window.electronAPI?.versions?.node || 'Unknown'
  }

  const statsCards = [
    {
      title: 'Cards Reviewed',
      value: stats.totalCards,
      icon: Book,
      color: 'primary'
    },
    {
      title: 'Current Streak',
      value: `${stats.currentStreak} days`,
      icon: Award,
      color: 'success'
    },
    {
      title: 'Total XP',
      value: stats.totalXP.toLocaleString(),
      icon: Star,
      color: 'warning'
    },
    {
      title: 'Retention Rate',
      value: `${stats.retentionRate}%`,
      icon: Users,
      color: 'error'
    }
  ]

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-8 h-full overflow-y-auto custom-scrollbar">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-4"
      >
        <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
          <Info className="w-10 h-10 text-primary" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            About Learning Platform
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Intelligent learning through adaptive spaced repetition and AI-powered content
          </p>
        </div>
        <div className="flex items-center justify-center space-x-6 text-sm text-gray-500 dark:text-gray-400">
          <span>Version 1.0.0</span>
          <span>•</span>
          <span>Desktop Edition</span>
          <span>•</span>
          <span>© 2024</span>
        </div>
      </motion.div>

      {/* User Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        {statsCards.map((stat, index) => {
          const Icon = stat.icon
          return (
            <div key={stat.title} className="card">
              <div className="card-body text-center">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center mx-auto mb-2 ${
                  stat.color === 'primary' ? 'bg-primary/10 text-primary' :
                  stat.color === 'success' ? 'bg-success/10 text-success' :
                  stat.color === 'warning' ? 'bg-warning/10 text-warning' :
                  'bg-error/10 text-error'
                }`}>
                  <Icon className="w-4 h-4" />
                </div>
                <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                  {stat.value}
                </p>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  {stat.title}
                </p>
              </div>
            </div>
          )
        })}
      </motion.div>

      {/* Features */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card"
      >
        <div className="card-header">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Key Features
          </h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <div key={feature.title} className="flex items-start space-x-4">
                  <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Icon className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-1">
                      {feature.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {feature.description}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </motion.div>

      {/* Tech Stack */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card"
      >
        <div className="card-header">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Technology Stack
          </h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {techStack.map((tech, index) => (
              <div key={tech.name} className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="flex items-center justify-between mb-1">
                  <h3 className="font-medium text-gray-900 dark:text-gray-100">
                    {tech.name}
                  </h3>
                  <span className="text-xs text-gray-500 dark:text-gray-400 font-mono">
                    {tech.version}
                  </span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {tech.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* System Information */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card"
      >
        <div className="card-header">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            System Information
          </h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-3">
                Platform Details
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Operating System:</span>
                  <span className="text-gray-900 dark:text-gray-100 capitalize">
                    {systemInfo.platform}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Electron Version:</span>
                  <span className="text-gray-900 dark:text-gray-100 font-mono">
                    {systemInfo.electronVersion}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Chrome Version:</span>
                  <span className="text-gray-900 dark:text-gray-100 font-mono">
                    {systemInfo.chromeVersion}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Node.js Version:</span>
                  <span className="text-gray-900 dark:text-gray-100 font-mono">
                    {systemInfo.nodeVersion}
                  </span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-3">
                Performance
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Hardware Tier:</span>
                  <span className="text-gray-900 dark:text-gray-100">
                    Auto-detected
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">AI Provider:</span>
                  <span className="text-gray-900 dark:text-gray-100">
                    Local Models
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Memory Usage:</span>
                  <span className="text-gray-900 dark:text-gray-100">
                    ~150 MB
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Storage Used:</span>
                  <span className="text-gray-900 dark:text-gray-100">
                    ~2.1 GB
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Support & Feedback */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="card"
      >
        <div className="card-header">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Support & Feedback
          </h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-3">
                Get Help
              </h3>
              <div className="space-y-3">
                <button className="flex items-center space-x-3 text-left w-full p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150">
                  <Mail className="w-5 h-5 text-primary" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">Email Support</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">support@learningplatform.dev</p>
                  </div>
                </button>
                
                <button className="flex items-center space-x-3 text-left w-full p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150">
                  <Github className="w-5 h-5 text-primary" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">GitHub Issues</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Report bugs and feature requests</p>
                  </div>
                </button>
                
                <button className="flex items-center space-x-3 text-left w-full p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150">
                  <Book className="w-5 h-5 text-primary" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">Documentation</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">User guide and tutorials</p>
                  </div>
                </button>
              </div>
            </div>

            <div>
              <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-3">
                Resources
              </h3>
              <div className="space-y-3">
                <button className="flex items-center space-x-3 text-left w-full p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150">
                  <Globe className="w-5 h-5 text-primary" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">Website</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Visit our homepage</p>
                  </div>
                  <ExternalLink className="w-4 h-4 text-gray-400 ml-auto" />
                </button>
                
                <button className="flex items-center space-x-3 text-left w-full p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150">
                  <Download className="w-5 h-5 text-primary" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">Updates</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Check for new versions</p>
                  </div>
                </button>
                
                <button className="flex items-center space-x-3 text-left w-full p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150">
                  <Users className="w-5 h-5 text-primary" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">Community</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Join our Discord server</p>
                  </div>
                  <ExternalLink className="w-4 h-4 text-gray-400 ml-auto" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Legal & Privacy */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="card"
      >
        <div className="card-body">
          <div className="flex items-center justify-center space-x-6 text-sm text-gray-500 dark:text-gray-400">
            <button className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors duration-150">
              Privacy Policy
            </button>
            <span>•</span>
            <button className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors duration-150">
              Terms of Service
            </button>
            <span>•</span>
            <button className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors duration-150">
              Licenses
            </button>
          </div>
          
          <div className="text-center mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <p className="text-gray-600 dark:text-gray-400">
              Made with{' '}
              <Heart className="w-4 h-4 inline text-error" fill="currentColor" />
              {' '}for learners everywhere
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
              © 2024 Learning Platform. All rights reserved.
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default About
