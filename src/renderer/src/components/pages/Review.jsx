import React, { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Play, 
  Pause, 
  Square, 
  SkipForward,
  Clock,
  Target,
  RotateCcw,
  CheckCircle,
  XCircle,
  RotateCw,
  Award
} from 'lucide-react'
import useStore from '../../store/useStore'
import clsx from 'clsx'

const Review = () => {
  const { 
    reviewSession,
    decks,
    startReviewSession,
    nextCard,
    answerCard,
    endReviewSession,
    updateStats,
    addNotification
  } = useStore()

  const [currentCardIndex, setCurrentCardIndex] = useState(0)
  const [showAnswer, setShowAnswer] = useState(false)
  const [sessionStartTime] = useState(Date.now())
  const [currentTime, setCurrentTime] = useState(Date.now())
  const [sessionPaused, setSessionPaused] = useState(false)
  
  // Mock cards data
  const mockCards = [
    {
      id: 1,
      type: 'flashcard',
      front: 'What is the capital of France?',
      back: 'Paris',
      difficulty: 'easy'
    },
    {
      id: 2,
      type: 'quiz',
      question: 'Which of the following is a prime number?',
      options: [15, 17, 21, 25],
      correctAnswer: 1,
      explanation: '17 is a prime number because it has no divisors other than 1 and itself.'
    },
    {
      id: 3,
      type: 'flashcard',
      front: 'Explain the concept of machine learning',
      back: 'Machine learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed.',
      difficulty: 'medium'
    }
  ]

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (sessionPaused) return

      switch (event.key) {
        case ' ': // Space to show/hide answer
          event.preventDefault()
          setShowAnswer(!showAnswer)
          break
        case '1': // Again
        case '2': // Hard
        case '3': // Good
        case '4': // Easy
          if (showAnswer) {
            event.preventDefault()
            handleGrade(event.key)
          }
          break
        case 'Enter':
          if (currentCard?.type === 'quiz') {
            event.preventDefault()
            setShowAnswer(true)
          }
          break
        case 'Escape':
          event.preventDefault()
          togglePause()
          break
        default:
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [showAnswer, sessionPaused, currentCard])

  // Timer effect
  useEffect(() => {
    if (!sessionPaused && reviewSession.isActive) {
      const interval = setInterval(() => {
        setCurrentTime(Date.now())
      }, 1000)
      return () => clearInterval(interval)
    }
  }, [sessionPaused, reviewSession.isActive])

  const currentCard = reviewSession.currentCard || mockCards[currentCardIndex]

  const handleStartSession = () => {
    startReviewSession(mockCards)
    setCurrentCardIndex(0)
    setShowAnswer(false)
    setCurrentTime(Date.now())
    addNotification({
      type: 'success',
      title: 'Session Started',
      message: 'Begin your review session!'
    })
  }

  const handleGrade = useCallback((grade) => {
    if (!currentCard) return

    const isCorrect = grade === '3' || grade === '4' // Good or Easy
    
    // Update stats
    answerCard(isCorrect)
    
    if (isCorrect) {
      updateStats({
        cardsReviewedToday: useStore.getState().stats.cardsReviewedToday + 1,
        currentStreak: useStore.getState().stats.currentStreak + 1,
        totalXP: useStore.getState().stats.totalXP + (grade === '4' ? 15 : 10)
      })
    }

    // Move to next card
    setTimeout(() => {
      if (currentCardIndex < mockCards.length - 1) {
        setCurrentCardIndex(currentCardIndex + 1)
        setShowAnswer(false)
      } else {
        handleEndSession()
      }
    }, 1000)
  }, [currentCard, currentCardIndex, answerCard, updateStats, addNotification])

  const handleEndSession = () => {
    const sessionDuration = Math.round((currentTime - sessionStartTime) / 1000 / 60)
    const averageTime = Math.round((currentTime - sessionStartTime) / mockCards.length / 1000)
    
    endReviewSession()
    setSessionPaused(false)
    
    addNotification({
      type: 'success',
      title: 'Session Completed!',
      message: `Reviewed ${mockCards.length} cards in ${sessionDuration} minutes. Average time: ${averageTime}s per card.`
    })
  }

  const togglePause = () => {
    setSessionPaused(!sessionPaused)
  }

  const formatTime = (milliseconds) => {
    const seconds = Math.floor(milliseconds / 1000)
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const gradingButtons = [
    {
      grade: '1',
      label: 'Again',
      description: 'Complete failure',
      color: 'error',
      shortcut: '1'
    },
    {
      grade: '2', 
      label: 'Hard',
      description: 'Difficult but correct',
      color: 'warning',
      shortcut: '2'
    },
    {
      grade: '3',
      label: 'Good',
      description: 'Correct with effort',
      color: 'success',
      shortcut: '3'
    },
    {
      grade: '4',
      label: 'Easy',
      description: 'Perfect recall',
      color: 'primary',
      shortcut: '4'
    }
  ]

  if (!reviewSession.isActive) {
    return (
      <div className="p-6 max-w-4xl mx-auto space-y-6 h-full flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center space-y-6"
        >
          <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
            <RotateCcw className="w-10 h-10 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Review Session
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Test your knowledge with flashcards, quizzes, and interactive content
            </p>
          </div>

          {/* Session Stats Preview */}
          <div className="grid grid-cols-3 gap-6 py-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-primary">
                {decks.reduce((sum, deck) => sum + deck.dueCards, 0)}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Cards Due</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-success">
                {decks.reduce((sum, deck) => sum + deck.newCards, 0)}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">New Cards</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-warning">
                {useStore.getState().stats.currentStreak}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Day Streak</p>
            </div>
          </div>

          <button
            onClick={handleStartSession}
            className="btn btn-primary btn-lg"
          >
            <Play className="w-5 h-5 mr-2" />
            Start Review Session
          </button>

          <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
            <p>Use keyboard shortcuts during the session:</p>
            <div className="flex justify-center space-x-4">
              <span><kbd className="px-1 bg-gray-200 dark:bg-gray-700 rounded">Space</kbd> Show answer</span>
              <span><kbd className="px-1 bg-gray-200 dark:bg-gray-700 rounded">1-4</kbd> Grade card</span>
              <span><kbd className="px-1 bg-gray-200 dark:bg-gray-700 rounded">Esc</kbd> Pause</span>
            </div>
          </div>
        </motion.div>
      </div>
    )
  }

  if (sessionPaused) {
    return (
      <div className="p-6 max-w-4xl mx-auto space-y-6 h-full flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center space-y-6 card"
        >
          <div className="card-body">
            <Pause className="w-16 h-16 text-primary mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Session Paused
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Take a break! Your progress is saved.
            </p>
            
            <div className="flex justify-center space-x-4">
              <button
                onClick={togglePause}
                className="btn btn-primary"
              >
                <Play className="w-4 h-4 mr-2" />
                Resume
              </button>
              <button
                onClick={handleEndSession}
                className="btn btn-secondary"
              >
                <Square className="w-4 h-4 mr-2" />
                End Session
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6 h-full">
      {/* Session Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <Clock className="w-5 h-5 text-gray-500" />
            <span className="text-sm font-mono text-gray-700 dark:text-gray-300">
              {formatTime(currentTime - sessionStartTime)}
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            <Target className="w-5 h-5 text-gray-500" />
            <span className="text-sm text-gray-700 dark:text-gray-300">
              {currentCardIndex + 1} / {mockCards.length}
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={togglePause}
            className="btn btn-ghost btn-sm"
            aria-label="Pause session"
          >
            <Pause className="w-4 h-4" />
          </button>
          <button
            onClick={handleEndSession}
            className="btn btn-ghost btn-sm"
            aria-label="End session"
          >
            <Square className="w-4 h-4" />
          </button>
        </div>
      </motion.div>

      {/* Progress Bar */}
      <div className="progress">
        <motion.div
          className="progress-bar"
          initial={{ width: 0 }}
          animate={{ width: `${((currentCardIndex + 1) / mockCards.length) * 100}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>

      {/* Card Display */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentCardIndex}
          initial={{ opacity: 0, x: 100 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -100 }}
          transition={{ duration: 0.3 }}
          className="card min-h-96 flex-1"
        >
          <div className="card-body flex flex-col justify-center items-center text-center space-y-6">
            {/* Card Type Indicator */}
            <div className="flex items-center space-x-2">
              {currentCard.type === 'flashcard' && (
                <span className="px-3 py-1 bg-primary/10 text-primary text-sm rounded-full">
                  Flashcard
                </span>
              )}
              {currentCard.type === 'quiz' && (
                <span className="px-3 py-1 bg-warning/10 text-warning text-sm rounded-full">
                  Quiz
                </span>
              )}
              {currentCard.difficulty && (
                <span className={clsx(
                  'px-3 py-1 text-sm rounded-full',
                  currentCard.difficulty === 'easy' && 'bg-success/10 text-success',
                  currentCard.difficulty === 'medium' && 'bg-warning/10 text-warning',
                  currentCard.difficulty === 'hard' && 'bg-error/10 text-error'
                )}>
                  {currentCard.difficulty}
                </span>
              )}
            </div>

            {/* Card Content */}
            <div className="flex-1 flex flex-col justify-center space-y-6 max-w-2xl">
              {currentCard.type === 'flashcard' ? (
                <>
                  {!showAnswer ? (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="space-y-4"
                    >
                      <h2 className="text-2xl font-medium text-gray-900 dark:text-gray-100">
                        {currentCard.front}
                      </h2>
                      <button
                        onClick={() => setShowAnswer(true)}
                        className="btn btn-secondary"
                      >
                        <RotateCw className="w-4 h-4 mr-2" />
                        Show Answer (Space)
                      </button>
                    </motion.div>
                  ) : (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="space-y-4"
                    >
                      <div className="p-4 bg-success/10 rounded-lg border border-success/20">
                        <p className="text-lg text-gray-700 dark:text-gray-300">
                          {currentCard.back}
                        </p>
                      </div>
                    </motion.div>
                  )}
                </>
              ) : currentCard.type === 'quiz' ? (
                <div className="space-y-6">
                  <h2 className="text-xl font-medium text-gray-900 dark:text-gray-100">
                    {currentCard.question}
                  </h2>
                  
                  {!showAnswer ? (
                    <div className="space-y-3">
                      {currentCard.options.map((option, index) => (
                        <button
                          key={index}
                          onClick={() => setShowAnswer(true)}
                          className="w-full p-3 text-left border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150"
                        >
                          {String.fromCharCode(65 + index)}. {option}
                        </button>
                      ))}
                      <button
                        onClick={() => setShowAnswer(true)}
                        className="btn btn-secondary"
                      >
                        Submit Answer (Enter)
                      </button>
                    </div>
                  ) : (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="space-y-4"
                    >
                      <div className="space-y-2">
                        {currentCard.options.map((option, index) => (
                          <div
                            key={index}
                            className={clsx(
                              'p-3 rounded-lg border',
                              index === currentCard.correctAnswer
                                ? 'bg-success/10 border-success text-success'
                                : 'bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600'
                            )}
                          >
                            <div className="flex items-center space-x-2">
                              {index === currentCard.correctAnswer ? (
                                <CheckCircle className="w-5 h-5" />
                              ) : (
                                <XCircle className="w-5 h-5 text-gray-400" />
                              )}
                              <span>
                                {String.fromCharCode(65 + index)}. {option}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      {currentCard.explanation && (
                        <div className="p-4 bg-primary/5 rounded-lg border border-primary/20">
                          <p className="text-sm text-gray-700 dark:text-gray-300">
                            <strong>Explanation:</strong> {currentCard.explanation}
                          </p>
                        </div>
                      )}
                    </motion.div>
                  )}
                </div>
              ) : null}
            </div>
          </div>
        </motion.div>
      </AnimatePresence>

      {/* Grading Buttons */}
      <AnimatePresence>
        {showAnswer && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-3"
          >
            {gradingButtons.map((button) => (
              <button
                key={button.grade}
                onClick={() => handleGrade(button.grade)}
                className={clsx(
                  'p-4 rounded-lg border-2 transition-all duration-150 text-left hover:shadow-md',
                  button.color === 'error' && 'border-error bg-error/5 hover:bg-error/10',
                  button.color === 'warning' && 'border-warning bg-warning/5 hover:bg-warning/10',
                  button.color === 'success' && 'border-success bg-success/5 hover:bg-success/10',
                  button.color === 'primary' && 'border-primary bg-primary/5 hover:bg-primary/10'
                )}
              >
                <div className="flex items-center space-x-3">
                  <div className={clsx(
                    'w-10 h-10 rounded-lg flex items-center justify-center font-bold text-white',
                    button.color === 'error' && 'bg-error',
                    button.color === 'warning' && 'bg-warning',
                    button.color === 'success' && 'bg-success',
                    button.color === 'primary' && 'bg-primary'
                  )}>
                    {button.grade}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">
                      {button.label}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      {button.description}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">
                      Press {button.shortcut}
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default Review
