import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Plus, 
  Search, 
  MoreVertical, 
  Edit, 
  Trash2, 
  Play,
  BookOpen,
  Target,
  Zap,
  Calendar,
  Filter,
  Grid,
  List
} from 'lucide-react'
import useStore from '../../store/useStore'
import clsx from 'clsx'

const Decks = () => {
  const { 
    decks, 
    currentDeck, 
    setCurrentDeck, 
    addDeck, 
    updateDeck, 
    deleteDeck,
    addNotification 
  } = useStore()

  const [viewMode, setViewMode] = useState('grid')
  const [searchQuery, setSearchQuery] = useState('')
  const [showNewDeckModal, setShowNewDeckModal] = useState(false)
  const [selectedDeck, setSelectedDeck] = useState(null)
  const [sortBy, setSortBy] = useState('name')

  const [newDeck, setNewDeck] = useState({
    name: '',
    description: ''
  })

  const filteredDecks = decks
    .filter(deck => 
      deck.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      deck.description.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name)
        case 'cards':
          return b.totalCards - a.totalCards
        case 'due':
          return b.dueCards - a.dueCards
        case 'created':
          return new Date(b.createdAt) - new Date(a.createdAt)
        default:
          return 0
      }
    })

  const handleCreateDeck = () => {
    if (!newDeck.name.trim()) {
      addNotification({
        type: 'error',
        title: 'Name Required',
        message: 'Please provide a name for your deck.'
      })
      return
    }

    addDeck({
      name: newDeck.name,
      description: newDeck.description,
      totalCards: 0,
      dueCards: 0,
      newCards: 0,
      createdAt: new Date().toISOString(),
      lastReviewed: null
    })

    setNewDeck({ name: '', description: '' })
    setShowNewDeckModal(false)
    
    addNotification({
      type: 'success',
      title: 'Deck Created',
      message: `"${newDeck.name}" has been created successfully.`
    })
  }

  const handleDeleteDeck = (deckId) => {
    if (decks.length <= 1) {
      addNotification({
        type: 'error',
        title: 'Cannot Delete',
        message: 'You must have at least one deck.'
      })
      return
    }

    deleteDeck(deckId)
    addNotification({
      type: 'success',
      title: 'Deck Deleted',
      message: 'Deck has been removed successfully.'
    })
  }

  const handleStartReview = (deckId) => {
    setCurrentDeck(deckId)
    addNotification({
      type: 'info',
      title: 'Review Session',
      message: 'Starting review session for selected deck...'
    })
    // In a real app, this would navigate to the review page with the selected deck
  }

  const DeckCard = ({ deck }) => (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className={clsx(
        'card cursor-pointer transition-all duration-150 hover:shadow-md',
        currentDeck === deck.id && 'ring-2 ring-primary border-primary'
      )}
      onClick={() => setCurrentDeck(deck.id)}
    >
      <div className="card-body">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                {deck.name}
              </h3>
              {deck.description && (
                <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-1">
                  {deck.description}
                </p>
              )}
            </div>
          </div>

          <div className="relative">
            <button
              className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              onClick={(e) => {
                e.stopPropagation()
                setSelectedDeck(selectedDeck === deck.id ? null : deck.id)
              }}
            >
              <MoreVertical className="w-4 h-4 text-gray-500" />
            </button>

            {selectedDeck === deck.id && (
              <div className="absolute right-0 mt-1 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-10">
                <button
                  className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2"
                  onClick={(e) => {
                    e.stopPropagation()
                    // Handle edit
                    setSelectedDeck(null)
                  }}
                >
                  <Edit className="w-4 h-4" />
                  <span>Edit Deck</span>
                </button>
                <button
                  className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleStartReview(deck.id)
                    setSelectedDeck(null)
                  }}
                >
                  <Play className="w-4 h-4" />
                  <span>Start Review</span>
                </button>
                <hr className="my-1 border-gray-200 dark:border-gray-600" />
                <button
                  className="w-full px-3 py-2 text-left text-sm text-error hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDeleteDeck(deck.id)
                    setSelectedDeck(null)
                  }}
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Delete Deck</span>
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-1 mb-1">
              <Target className="w-4 h-4 text-success" />
              <span className="text-lg font-bold text-gray-900 dark:text-gray-100">
                {deck.totalCards}
              </span>
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400">Total Cards</p>
          </div>
          
          <div className="text-center">
            <div className="flex items-center justify-center space-x-1 mb-1">
              <Calendar className="w-4 h-4 text-warning" />
              <span className="text-lg font-bold text-gray-900 dark:text-gray-100">
                {deck.dueCards}
              </span>
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400">Due Today</p>
          </div>
          
          <div className="text-center">
            <div className="flex items-center justify-center space-x-1 mb-1">
              <Zap className="w-4 h-4 text-primary" />
              <span className="text-lg font-bold text-gray-900 dark:text-gray-100">
                {deck.newCards}
              </span>
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400">New Cards</p>
          </div>
        </div>

        {deck.lastReviewed && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Last reviewed: {new Date(deck.lastReviewed).toLocaleDateString()}
            </p>
          </div>
        )}
      </div>
    </motion.div>
  )

  return (
    <div className="p-6 space-y-6 h-full overflow-y-auto custom-scrollbar">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Deck Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Organize your learning content into manageable decks
          </p>
        </div>
        
        <button
          onClick={() => setShowNewDeckModal(true)}
          className="btn btn-primary"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Deck
        </button>
      </motion.div>

      {/* Controls */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-col sm:flex-row gap-4 items-center justify-between"
      >
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search decks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input pl-10"
          />
        </div>

        {/* Filters and View Controls */}
        <div className="flex items-center space-x-3">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="input text-sm"
          >
            <option value="name">Sort by Name</option>
            <option value="cards">Sort by Total Cards</option>
            <option value="due">Sort by Due Cards</option>
            <option value="created">Sort by Created Date</option>
          </select>

          <div className="flex border border-gray-200 dark:border-gray-600 rounded-lg">
            <button
              onClick={() => setViewMode('grid')}
              className={clsx(
                'p-2 rounded-l-lg transition-colors duration-150',
                viewMode === 'grid'
                  ? 'bg-primary text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
              )}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={clsx(
                'p-2 rounded-r-lg transition-colors duration-150 border-l border-gray-200 dark:border-gray-600',
                viewMode === 'list'
                  ? 'bg-primary text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
              )}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </motion.div>

      {/* Stats Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 sm:grid-cols-4 gap-4"
      >
        <div className="card">
          <div className="card-body text-center">
            <p className="text-2xl font-bold text-primary">{decks.length}</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Total Decks</p>
          </div>
        </div>
        <div className="card">
          <div className="card-body text-center">
            <p className="text-2xl font-bold text-success">
              {decks.reduce((sum, deck) => sum + deck.totalCards, 0)}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Total Cards</p>
          </div>
        </div>
        <div className="card">
          <div className="card-body text-center">
            <p className="text-2xl font-bold text-warning">
              {decks.reduce((sum, deck) => sum + deck.dueCards, 0)}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Due Today</p>
          </div>
        </div>
        <div className="card">
          <div className="card-body text-center">
            <p className="text-2xl font-bold text-error">
              {decks.reduce((sum, deck) => sum + deck.newCards, 0)}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">New Cards</p>
          </div>
        </div>
      </motion.div>

      {/* Deck Grid/List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        {filteredDecks.length === 0 ? (
          <div className="text-center py-12">
            <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              {searchQuery ? 'No decks found' : 'No decks yet'}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {searchQuery 
                ? 'Try adjusting your search criteria.' 
                : 'Create your first deck to get started with learning.'
              }
            </p>
            {!searchQuery && (
              <button
                onClick={() => setShowNewDeckModal(true)}
                className="btn btn-primary"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Deck
              </button>
            )}
          </div>
        ) : (
          <div className={clsx(
            viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
              : 'space-y-4'
          )}>
            <AnimatePresence>
              {filteredDecks.map((deck) => (
                <DeckCard key={deck.id} deck={deck} />
              ))}
            </AnimatePresence>
          </div>
        )}
      </motion.div>

      {/* New Deck Modal */}
      <AnimatePresence>
        {showNewDeckModal && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="modal-overlay"
              onClick={() => setShowNewDeckModal(false)}
            />
            <div className="modal-content">
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="modal-panel"
              >
                <div className="card-header">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                    Create New Deck
                  </h2>
                </div>
                <div className="card-body space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Deck Name *
                    </label>
                    <input
                      type="text"
                      value={newDeck.name}
                      onChange={(e) => setNewDeck({...newDeck, name: e.target.value})}
                      className="input"
                      placeholder="Enter deck name..."
                      autoFocus
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Description
                    </label>
                    <textarea
                      value={newDeck.description}
                      onChange={(e) => setNewDeck({...newDeck, description: e.target.value})}
                      className="textarea"
                      placeholder="Describe what this deck contains..."
                      rows={3}
                    />
                  </div>
                </div>
                <div className="card-footer flex justify-end space-x-3">
                  <button
                    onClick={() => {
                      setShowNewDeckModal(false)
                      setNewDeck({ name: '', description: '' })
                    }}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleCreateDeck}
                    className="btn btn-primary"
                  >
                    Create Deck
                  </button>
                </div>
              </motion.div>
            </div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}

export default Decks
