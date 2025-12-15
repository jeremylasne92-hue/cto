import React, { useState, useEffect } from 'react';
import { User } from '../../types/profile';
import './FollowersTab.css';

interface FollowersTabProps {
  userId: number;
}

const FollowersTab: React.FC<FollowersTabProps> = ({ userId }) => {
  const [followers, setFollowers] = useState<User[]>([]);
  const [following, setFollowing] = useState<User[]>([]);
  const [searchHandle, setSearchHandle] = useState('');
  const [activeView, setActiveView] = useState<'followers' | 'following'>('followers');

  useEffect(() => {
    loadSocialData();
  }, [userId]);

  const loadSocialData = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/profile/me`, {
        headers: { 'X-User-Id': userId.toString() }
      });
      const data = await response.json();
      setFollowers(data.followers || []);
      setFollowing(data.following || []);
    } catch (error) {
      console.error('Failed to load social data:', error);
    }
  };

  const handleFollow = async () => {
    if (!searchHandle.trim()) {
      alert('Please enter a handle');
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/profile/follow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId.toString()
        },
        body: JSON.stringify({ handle: searchHandle })
      });

      const result = await response.json();
      if (result.success) {
        setSearchHandle('');
        await loadSocialData();
      } else {
        alert(result.error || 'Failed to follow user');
      }
    } catch (error) {
      console.error('Failed to follow user:', error);
      alert('Failed to follow user');
    }
  };

  const handleUnfollow = async (handle: string) => {
    if (!confirm(`Unfollow @${handle}?`)) {
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/profile/unfollow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId.toString()
        },
        body: JSON.stringify({ handle })
      });

      const result = await response.json();
      if (result.success) {
        await loadSocialData();
      } else {
        alert(result.error || 'Failed to unfollow user');
      }
    } catch (error) {
      console.error('Failed to unfollow user:', error);
      alert('Failed to unfollow user');
    }
  };

  return (
    <div className="followers-tab">
      <h2>Social Connections</h2>

      <div className="follow-user-form">
        <h3>Follow a User</h3>
        <div className="follow-input-group">
          <input
            type="text"
            placeholder="Enter user handle"
            value={searchHandle}
            onChange={(e) => setSearchHandle(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleFollow()}
          />
          <button onClick={handleFollow}>Follow</button>
        </div>
      </div>

      <div className="social-tabs">
        <button
          className={activeView === 'followers' ? 'active' : ''}
          onClick={() => setActiveView('followers')}
        >
          Followers ({followers.length})
        </button>
        <button
          className={activeView === 'following' ? 'active' : ''}
          onClick={() => setActiveView('following')}
        >
          Following ({following.length})
        </button>
      </div>

      <div className="user-list">
        {activeView === 'followers' ? (
          followers.length === 0 ? (
            <p className="empty">No followers yet</p>
          ) : (
            followers.map((user) => (
              <div key={user.id} className="user-card">
                <div className="user-info">
                  <strong>@{user.handle}</strong>
                  <span className="user-visibility">{user.visibility_default}</span>
                </div>
              </div>
            ))
          )
        ) : (
          following.length === 0 ? (
            <p className="empty">Not following anyone yet</p>
          ) : (
            following.map((user) => (
              <div key={user.id} className="user-card">
                <div className="user-info">
                  <strong>@{user.handle}</strong>
                  <span className="user-visibility">{user.visibility_default}</span>
                </div>
                <button
                  className="unfollow-btn"
                  onClick={() => handleUnfollow(user.handle)}
                >
                  Unfollow
                </button>
              </div>
            ))
          )
        )}
      </div>
    </div>
  );
};

export default FollowersTab;
