import React, { useMemo } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  Target, 
  Zap, 
  Calendar,
  BookOpen,
  Upload,
  BarChart3,
  Play,
  AlertTriangle
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import useStore from '../../store/useStore'
import { useNavigate } from 'react-router-dom'
import clsx from 'clsx'

const Dashboard = () => {
  const navigate = useNavigate()
  const { stats, decks, reviewHistory, setCurrentView, addNotification } = useStore()

  // Generate sample data for charts
  const chartData = useMemo(() => {
    const data = []
    for (let i = 29; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      data.push({
        date: date.toISOString().split('T')[0],
        reviews: Math.floor(Math.random() * 50) + 10,
        retention: Math.random() * 20 + 75
      })
    }
    return data
  }, [])

  // Calculate upcoming cards
  const upcomingCards = useMemo(() => {
    const due = decks.reduce((sum, deck) => sum + deck.dueCards, 0)
    const newCards = decks.reduce((sum, deck) => sum + deck.newCards, 0)
    return { due, new: newCards }
  }, [decks])

  const quickActions = [
    {
      title: 'Start Review Session',
      description: 'Begin learning with due cards',
      icon: Play,
      action: () => {
        setCurrentView('review')
        navigate('/review')
      },
      color: 'primary',
      count: upcomingCards.due
    },
    {
      title: 'Ingest Content',
      description: 'Import new learning material',
      icon: Upload,
      action: () => {
        setCurrentView('ingestion')
        navigate('/ingestion')
      },
      color: 'success',
      count: null
    },
    {
      title: 'View Statistics',
      description: 'Analyze your progress',
      icon: BarChart3,
      action: () => {
        addNotification({
          type: 'info',
          title: 'Statistics',
          message: 'Detailed analytics coming soon!'
        })
      },
      color: 'warning',
      count: null
    },
    {
      title: 'Manage Decks',
      description: 'Organize your content',
      icon: BookOpen,
      action: () => {
        setCurrentView('decks')
        navigate('/decks')
      },
      color: 'secondary',
      count: decks.length
    }
  ]

  const statCards = [
    {
      title: 'Cards Reviewed Today',
      value: stats.cardsReviewedToday,
      icon: Target,
      color: 'success',
      trend: '+12%'
    },
    {
      title: 'Current Streak',
      value: stats.currentStreak,
      icon: Zap,
      color: 'primary',
      trend: '+2 days'
    },
    {
      title: 'Total XP',
      value: stats.totalXP.toLocaleString(),
      icon: TrendingUp,
      color: 'warning',
      trend: '+150 XP'
    },
    {
      title: 'Retention Rate',
      value: `${stats.retentionRate}%`,
      icon: Calendar,
      color: 'error',
      trend: '+5%'
    }
  ]

  return (
    <div className="p-6 space-y-6 h-full overflow-y-auto custom-scrollbar">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Welcome back!
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Ready to continue your learning journey?
          </p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
          <Calendar className="w-4 h-4" />
          <span>{new Date().toLocaleDateString()}</span>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card"
            >
              <div className="card-body">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {stat.title}
                    </p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                      {stat.value}
                    </p>
                    <p className={clsx(
                      'text-xs mt-1',
                      stat.color === 'success' && 'text-success',
                      stat.color === 'primary' && 'text-primary',
                      stat.color === 'warning' && 'text-warning',
                      stat.color === 'error' && 'text-error'
                    )}>
                      {stat.trend}
                    </p>
                  </div>
                  <div className={clsx(
                    'w-12 h-12 rounded-lg flex items-center justify-center',
                    stat.color === 'success' && 'bg-success/10',
                    stat.color === 'primary' && 'bg-primary/10',
                    stat.color === 'warning' && 'bg-warning/10',
                    stat.color === 'error' && 'bg-error/10'
                  )}>
                    <Icon className={clsx(
                      'w-6 h-6',
                      stat.color === 'success' && 'text-success',
                      stat.color === 'primary' && 'text-primary',
                      stat.color === 'warning' && 'text-warning',
                      stat.color === 'error' && 'text-error'
                    )} />
                  </div>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Review Count Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Daily Reviews (Last 30 Days)
            </h3>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorReviews" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366F1" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#6366F1" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis 
                  dataKey="date" 
                  stroke="#6B7280"
                  fontSize={12}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis stroke="#6B7280" fontSize={12} />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#374151',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#F9FAFB'
                  }}
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <Area 
                  type="monotone" 
                  dataKey="reviews" 
                  stroke="#6366F1" 
                  fillOpacity={1} 
                  fill="url(#colorReviews)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Retention Rate Chart */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="card"
        >
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Retention Rate Trend
            </h3>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis 
                  dataKey="date" 
                  stroke="#6B7280"
                  fontSize={12}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis stroke="#6B7280" fontSize={12} domain={[70, 100]} />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#374151',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#F9FAFB'
                  }}
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <Line 
                  type="monotone" 
                  dataKey="retention" 
                  stroke="#10B981" 
                  strokeWidth={2}
                  dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* Upcoming and Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="card"
        >
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Upcoming
            </h3>
          </div>
          <div className="card-body space-y-4">
            <div className="flex items-center justify-between p-3 bg-warning/10 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-warning/20 rounded-lg flex items-center justify-center">
                  <BookOpen className="w-4 h-4 text-warning" />
                </div>
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    Cards Due
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Ready for review
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-warning">
                  {upcomingCards.due}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  cards
                </p>
              </div>
            </div>

            <div className="flex items-center justify-between p-3 bg-primary/10 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-primary/20 rounded-lg flex items-center justify-center">
                  <Zap className="w-4 h-4 text-primary" />
                </div>
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    New Cards
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Available to learn
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-primary">
                  {upcomingCards.new}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  cards
                </p>
              </div>
            </div>

            {upcomingCards.due === 0 && upcomingCards.new === 0 && (
              <div className="text-center py-8">
                <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600 dark:text-gray-400">
                  No cards due for review. Great job!
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                  Import some content to continue learning.
                </p>
              </div>
            )}
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="card"
        >
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Quick Actions
            </h3>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 gap-3">
              {quickActions.map((action, index) => {
                const Icon = action.icon
                return (
                  <button
                    key={action.title}
                    onClick={action.action}
                    className={clsx(
                      'p-4 rounded-lg border-2 border-transparent transition-all duration-150 text-left hover:shadow-md',
                      action.color === 'primary' && 'bg-primary/5 hover:bg-primary/10 hover:border-primary/20',
                      action.color === 'success' && 'bg-success/5 hover:bg-success/10 hover:border-success/20',
                      action.color === 'warning' && 'bg-warning/5 hover:bg-warning/10 hover:border-warning/20',
                      action.color === 'secondary' && 'bg-gray-50 hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600'
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={clsx(
                          'w-10 h-10 rounded-lg flex items-center justify-center',
                          action.color === 'primary' && 'bg-primary/20',
                          action.color === 'success' && 'bg-success/20',
                          action.color === 'warning' && 'bg-warning/20',
                          action.color === 'secondary' && 'bg-gray-200 dark:bg-gray-600'
                        )}>
                          <Icon className={clsx(
                            'w-5 h-5',
                            action.color === 'primary' && 'text-primary',
                            action.color === 'success' && 'text-success',
                            action.color === 'warning' && 'text-warning',
                            action.color === 'secondary' && 'text-gray-600 dark:text-gray-300'
                          )} />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-gray-100">
                            {action.title}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {action.description}
                          </p>
                        </div>
                      </div>
                      {action.count !== null && (
                        <div className="text-right">
                          <span className={clsx(
                            'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                            action.color === 'primary' && 'bg-primary/20 text-primary',
                            action.color === 'success' && 'bg-success/20 text-success',
                            action.color === 'warning' && 'bg-warning/20 text-warning',
                            action.color === 'secondary' && 'bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300'
                          )}>
                            {action.count}
                          </span>
                        </div>
                      )}
                    </div>
                  </button>
                )
              })}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default Dashboard
