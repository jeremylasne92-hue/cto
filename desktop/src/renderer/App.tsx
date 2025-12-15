import React, { useState } from 'react';
import './App.css';
import ProfileDashboard from './components/ProfileDashboard';
import SkillsManager from './components/SkillsManager';
import FollowersTab from './components/FollowersTab';
import ComparisonModal from './components/ComparisonModal';

function App() {
  const [activeTab, setActiveTab] = useState<'profile' | 'skills' | 'followers'>('profile');
  const [showComparison, setShowComparison] = useState(false);
  const [currentUserId] = useState(1);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Social Learning Profile</h1>
      </header>

      <nav className="tab-navigation">
        <button
          className={activeTab === 'profile' ? 'active' : ''}
          onClick={() => setActiveTab('profile')}
        >
          Profile
        </button>
        <button
          className={activeTab === 'skills' ? 'active' : ''}
          onClick={() => setActiveTab('skills')}
        >
          Skills
        </button>
        <button
          className={activeTab === 'followers' ? 'active' : ''}
          onClick={() => setActiveTab('followers')}
        >
          Social
        </button>
        <button
          className="compare-btn"
          onClick={() => setShowComparison(true)}
        >
          Compare Skills
        </button>
      </nav>

      <main className="app-content">
        {activeTab === 'profile' && <ProfileDashboard userId={currentUserId} />}
        {activeTab === 'skills' && <SkillsManager userId={currentUserId} />}
        {activeTab === 'followers' && <FollowersTab userId={currentUserId} />}
      </main>

      {showComparison && (
        <ComparisonModal
          userId={currentUserId}
          onClose={() => setShowComparison(false)}
        />
      )}
    </div>
  );
}

export default App;
