import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Monitor, 
  Cpu, 
  Database, 
  Download, 
  Upload, 
  Moon, 
  Sun,
  Volume2,
  VolumeX,
  Wifi,
  WifiOff,
  Shield,
  Info,
  Save,
  RotateCcw,
  HardDrive,
  Clock,
  Target,
  Settings as SettingsIcon
} from 'lucide-react'
import useStore from '../../store/useStore'
import clsx from 'clsx'

const Settings = () => {
  const { 
    settings, 
    updateSettings, 
    theme, 
    setTheme,
    addNotification 
  } = useStore()

  const [tempSettings, setTempSettings] = useState(settings)
  const [hasChanges, setHasChanges] = useState(false)

  const handleSettingChange = (key, value) => {
    setTempSettings(prev => ({
      ...prev,
      [key]: value
    }))
    setHasChanges(true)
  }

  const handleSaveSettings = () => {
    updateSettings(tempSettings)
    setHasChanges(false)
    
    if (tempSettings.theme !== theme) {
      setTheme(tempSettings.theme)
    }
    
    addNotification({
      type: 'success',
      title: 'Settings Saved',
      message: 'Your preferences have been updated successfully.'
    })
  }

  const handleResetSettings = () => {
    setTempSettings(settings)
    setHasChanges(false)
  }

  const hardwareTiers = [
    {
      id: 'auto',
      name: 'Auto-detect',
      description: 'Automatically detect and use the best settings for your device',
      icon: Monitor,
      recommended: true
    },
    {
      id: 'low',
      name: 'Low Power',
      description: 'Optimized for older devices or battery saving',
      icon: Cpu,
      specs: ['Lightweight models', 'Reduced animations', 'Simple UI']
    },
    {
      id: 'medium',
      name: 'Balanced',
      description: 'Good performance on most modern devices',
      icon: Database,
      specs: ['Standard models', 'Normal animations', 'Enhanced UI']
    },
    {
      id: 'high',
      name: 'High Performance',
      description: 'Best experience on powerful devices',
      icon: SettingsIcon,
      specs: ['Large models', 'Rich animations', 'Advanced features']
    }
  ]

  const llmProviders = [
    {
      id: 'local',
      name: 'Local Models',
      description: 'Run AI models on your device for privacy',
      icon: HardDrive,
      pros: ['Privacy-focused', 'No internet required', 'Free to use'],
      cons: ['Slower processing', 'Limited model size', 'Device dependent']
    },
    {
      id: 'cloud',
      name: 'Cloud API',
      description: 'Use powerful cloud-based AI services',
      icon: Wifi,
      pros: ['Fast processing', 'Latest models', 'Consistent performance'],
      cons: ['Requires internet', 'Data sent to cloud', 'Usage costs']
    }
  ]

  const settingSections = [
    {
      id: 'appearance',
      title: 'Appearance',
      icon: theme === 'dark' ? Moon : Sun,
      description: 'Customize the look and feel'
    },
    {
      id: 'review',
      title: 'Review Preferences',
      icon: Target,
      description: 'Configure your learning experience'
    },
    {
      id: 'hardware',
      title: 'Hardware & Performance',
      icon: Monitor,
      description: 'Optimize for your device'
    },
    {
      id: 'llm',
      title: 'AI & Language Models',
      icon: Database,
      description: 'Configure AI processing'
    },
    {
      id: 'data',
      title: 'Data & Privacy',
      icon: Shield,
      description: 'Manage your data and privacy'
    }
  ]

  const [activeSection, setActiveSection] = useState('appearance')

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6 h-full overflow-y-auto custom-scrollbar">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Settings
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Customize your learning experience
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {hasChanges && (
            <div className="flex items-center space-x-2 text-warning">
              <div className="w-2 h-2 bg-warning rounded-full animate-pulse"></div>
              <span className="text-sm">Unsaved changes</span>
            </div>
          )}
          <button
            onClick={handleResetSettings}
            className="btn btn-secondary"
            disabled={!hasChanges}
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset
          </button>
          <button
            onClick={handleSaveSettings}
            className="btn btn-primary"
            disabled={!hasChanges}
          >
            <Save className="w-4 h-4 mr-2" />
            Save Changes
          </button>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Settings Navigation */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="lg:col-span-1"
        >
          <div className="card">
            <div className="card-body p-4">
              <nav className="space-y-1">
                {settingSections.map((section) => {
                  const Icon = section.icon
                  return (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={clsx(
                        'w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors duration-150',
                        activeSection === section.id
                          ? 'bg-primary text-white'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                      )}
                    >
                      <Icon className="w-5 h-5 flex-shrink-0" />
                      <div className="min-w-0">
                        <div className="font-medium truncate">{section.title}</div>
                        <div className={clsx(
                          'text-xs truncate',
                          activeSection === section.id 
                            ? 'text-white/80' 
                            : 'text-gray-500 dark:text-gray-400'
                        )}>
                          {section.description}
                        </div>
                      </div>
                    </button>
                  )
                })}
              </nav>
            </div>
          </div>
        </motion.div>

        {/* Settings Content */}
        <motion.div
          key={activeSection}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-3"
        >
          {/* Appearance Settings */}
          {activeSection === 'appearance' && (
            <div className="space-y-6">
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    Theme
                  </h3>
                </div>
                <div className="card-body space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {['light', 'dark', 'auto'].map((themeOption) => (
                      <button
                        key={themeOption}
                        onClick={() => handleSettingChange('theme', themeOption)}
                        className={clsx(
                          'p-4 rounded-lg border-2 transition-all duration-150 text-left',
                          tempSettings.theme === themeOption
                            ? 'border-primary bg-primary/5'
                            : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                        )}
                      >
                        <div className="flex items-center space-x-3 mb-2">
                          {themeOption === 'light' && <Sun className="w-5 h-5" />}
                          {themeOption === 'dark' && <Moon className="w-5 h-5" />}
                          {themeOption === 'auto' && <Monitor className="w-5 h-5" />}
                          <span className="font-medium capitalize">{themeOption}</span>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {themeOption === 'light' && 'Light mode for daytime use'}
                          {themeOption === 'dark' && 'Dark mode for low-light conditions'}
                          {themeOption === 'auto' && 'Follow system preference'}
                        </p>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    Accessibility
                  </h3>
                </div>
                <div className="card-body space-y-4">
                  <div className="space-y-3">
                    <label className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={tempSettings.soundEnabled}
                        onChange={(e) => handleSettingChange('soundEnabled', e.target.checked)}
                        className="rounded border-gray-300 text-primary focus:ring-primary"
                      />
                      <div className="flex items-center space-x-2">
                        {tempSettings.soundEnabled ? (
                          <Volume2 className="w-4 h-4 text-primary" />
                        ) : (
                          <VolumeX className="w-4 h-4 text-gray-400" />
                        )}
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          Enable sound effects
                        </span>
                      </div>
                    </label>
                    
                    <label className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={tempSettings.notifications}
                        onChange={(e) => handleSettingChange('notifications', e.target.checked)}
                        className="rounded border-gray-300 text-primary focus:ring-primary"
                      />
                      <span className="text-sm text-gray-700 dark:text-gray-300">
                        Enable notifications
                      </span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Review Preferences */}
          {activeSection === 'review' && (
            <div className="space-y-6">
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    Session Settings
                  </h3>
                </div>
                <div className="card-body space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        <Clock className="w-4 h-4 inline mr-1" />
                        Session Duration (minutes)
                      </label>
                      <select
                        value={tempSettings.reviewSessionDuration}
                        onChange={(e) => handleSettingChange('reviewSessionDuration', parseInt(e.target.value))}
                        className="input"
                      >
                        <option value={15}>15 minutes</option>
                        <option value={30}>30 minutes</option>
                        <option value={45}>45 minutes</option>
                        <option value={60}>60 minutes</option>
                        <option value={90}>90 minutes</option>
                        <option value={0}>No limit</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        <Target className="w-4 h-4 inline mr-1" />
                        Card Order Preference
                      </label>
                      <select
                        value={tempSettings.cardOrder}
                        onChange={(e) => handleSettingChange('cardOrder', e.target.value)}
                        className="input"
                      >
                        <option value="due-first">Due cards first</option>
                        <option value="new-first">New cards first</option>
                        <option value="random">Random order</option>
                        <option value="difficulty">By difficulty</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Hardware Settings */}
          {activeSection === 'hardware' && (
            <div className="space-y-6">
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    Hardware Tier
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Choose the performance level that matches your device
                  </p>
                </div>
                <div className="card-body">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {hardwareTiers.map((tier) => {
                      const Icon = tier.icon
                      return (
                        <button
                          key={tier.id}
                          onClick={() => handleSettingChange('hardwareTier', tier.id)}
                          className={clsx(
                            'p-4 rounded-lg border-2 transition-all duration-150 text-left relative',
                            tempSettings.hardwareTier === tier.id
                              ? 'border-primary bg-primary/5'
                              : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                          )}
                        >
                          {tier.recommended && (
                            <span className="absolute top-2 right-2 px-2 py-1 bg-success text-white text-xs rounded-full">
                              Recommended
                            </span>
                          )}
                          
                          <div className="flex items-center space-x-3 mb-3">
                            <Icon className={clsx(
                              'w-6 h-6',
                              tempSettings.hardwareTier === tier.id ? 'text-primary' : 'text-gray-500 dark:text-gray-400'
                            )} />
                            <span className="font-medium text-gray-900 dark:text-gray-100">
                              {tier.name}
                            </span>
                          </div>
                          
                          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                            {tier.description}
                          </p>
                          
                          {tier.specs && (
                            <ul className="space-y-1">
                              {tier.specs.map((spec, index) => (
                                <li key={index} className="text-xs text-gray-500 dark:text-gray-400 flex items-center">
                                  <span className="w-1 h-1 bg-gray-400 rounded-full mr-2"></span>
                                  {spec}
                                </li>
                              ))}
                            </ul>
                          )}
                        </button>
                      )
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* LLM Settings */}
          {activeSection === 'llm' && (
            <div className="space-y-6">
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    AI Model Provider
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Choose where your AI models run
                  </p>
                </div>
                <div className="card-body">
                  <div className="space-y-4">
                    {llmProviders.map((provider) => {
                      const Icon = provider.icon
                      return (
                        <button
                          key={provider.id}
                          onClick={() => handleSettingChange('llmProvider', provider.id)}
                          className={clsx(
                            'w-full p-4 rounded-lg border-2 transition-all duration-150 text-left',
                            tempSettings.llmProvider === provider.id
                              ? 'border-primary bg-primary/5'
                              : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                          )}
                        >
                          <div className="flex items-center space-x-3 mb-3">
                            <Icon className={clsx(
                              'w-6 h-6',
                              tempSettings.llmProvider === provider.id ? 'text-primary' : 'text-gray-500 dark:text-gray-400'
                            )} />
                            <span className="font-medium text-gray-900 dark:text-gray-100">
                              {provider.name}
                            </span>
                          </div>
                          
                          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                            {provider.description}
                          </p>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <p className="text-xs font-medium text-success mb-1">Pros:</p>
                              <ul className="space-y-1">
                                {provider.pros.map((pro, index) => (
                                  <li key={index} className="text-xs text-gray-500 dark:text-gray-400 flex items-center">
                                    <span className="w-1 h-1 bg-success rounded-full mr-2"></span>
                                    {pro}
                                  </li>
                                ))}
                              </ul>
                            </div>
                            
                            <div>
                              <p className="text-xs font-medium text-error mb-1">Cons:</p>
                              <ul className="space-y-1">
                                {provider.cons.map((con, index) => (
                                  <li key={index} className="text-xs text-gray-500 dark:text-gray-400 flex items-center">
                                    <span className="w-1 h-1 bg-error rounded-full mr-2"></span>
                                    {con}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </button>
                      )
                    })}
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    Model Management
                  </h3>
                </div>
                <div className="card-body">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-gray-100">
                          Local Model: Llama 3.2 3B
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Downloaded • 2.1 GB • Ready to use
                        </p>
                      </div>
                      <button className="btn btn-success btn-sm">
                        <Download className="w-4 h-4 mr-2" />
                        Update
                      </button>
                    </div>
                    
                    <button className="w-full p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-primary transition-colors duration-150">
                      <Download className="w-5 h-5 mx-auto mb-2 text-gray-400" />
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Browse available models
                      </p>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Data & Privacy */}
          {activeSection === 'data' && (
            <div className="space-y-6">
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    Data Management
                  </h3>
                </div>
                <div className="card-body space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <button className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150">
                      <Upload className="w-6 h-6 text-primary mx-auto mb-2" />
                      <p className="font-medium text-gray-900 dark:text-gray-100 mb-1">
                        Export Data
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Backup your decks and progress
                      </p>
                    </button>
                    
                    <button className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150">
                      <Download className="w-6 h-6 text-primary mx-auto mb-2" />
                      <p className="font-medium text-gray-900 dark:text-gray-100 mb-1">
                        Import Data
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Restore from backup file
                      </p>
                    </button>
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    Privacy & Sync
                  </h3>
                </div>
                <div className="card-body space-y-4">
                  <label className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      checked={tempSettings.autoSync}
                      onChange={(e) => handleSettingChange('autoSync', e.target.checked)}
                      className="rounded border-gray-300 text-primary focus:ring-primary"
                    />
                    <div className="flex items-center space-x-2">
                      {tempSettings.autoSync ? (
                        <Wifi className="w-4 h-4 text-primary" />
                      ) : (
                        <WifiOff className="w-4 h-4 text-gray-400" />
                      )}
                      <span className="text-sm text-gray-700 dark:text-gray-300">
                        Enable automatic sync
                      </span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}

export default Settings
