import React, { useState, useEffect } from 'react';
import { FullProfile } from '../../types/profile';
import './ProfileDashboard.css';

interface ProfileDashboardProps {
  userId: number;
}

const ProfileDashboard: React.FC<ProfileDashboardProps> = ({ userId }) => {
  const [profile, setProfile] = useState<FullProfile | null>(null);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    bio: '',
    interests: '',
    learning_style: '',
    privacy_bio: 0,
    privacy_interests: 0,
    privacy_learning_style: 0
  });

  useEffect(() => {
    loadProfile();
  }, [userId]);

  const loadProfile = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/profile/me`, {
        headers: { 'X-User-Id': userId.toString() }
      });
      const data = await response.json();
      setProfile(data);
      
      if (data.profile) {
        setFormData({
          bio: data.profile.bio || '',
          interests: data.profile.interests || '',
          learning_style: data.profile.learning_style || '',
          privacy_bio: data.profile.privacy_bio || 0,
          privacy_interests: data.profile.privacy_interests || 0,
          privacy_learning_style: data.profile.privacy_learning_style || 0
        });
      }
    } catch (error) {
      console.error('Failed to load profile:', error);
    }
  };

  const handleSave = async () => {
    try {
      await fetch('http://localhost:5000/api/profile/upsert', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId.toString()
        },
        body: JSON.stringify({
          bio: formData.bio,
          interests: formData.interests,
          learning_style: formData.learning_style
        })
      });

      await fetch('http://localhost:5000/api/profile/privacy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId.toString()
        },
        body: JSON.stringify({
          privacy_bio: formData.privacy_bio,
          privacy_interests: formData.privacy_interests,
          privacy_learning_style: formData.privacy_learning_style
        })
      });

      await loadProfile();
      setEditing(false);
    } catch (error) {
      console.error('Failed to save profile:', error);
    }
  };

  const refreshMetrics = async () => {
    try {
      await fetch('http://localhost:5000/api/profile/metrics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId.toString()
        }
      });
      await loadProfile();
    } catch (error) {
      console.error('Failed to refresh metrics:', error);
    }
  };

  if (!profile) {
    return <div className="loading">Loading profile...</div>;
  }

  return (
    <div className="profile-dashboard">
      <div className="profile-header">
        <h2>@{profile.user.handle}</h2>
        <button onClick={() => setEditing(!editing)}>
          {editing ? 'Cancel' : 'Edit Profile'}
        </button>
      </div>

      {editing ? (
        <div className="profile-form">
          <div className="form-group">
            <label>Bio</label>
            <textarea
              value={formData.bio}
              onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
              rows={4}
            />
            <label className="privacy-label">
              <input
                type="checkbox"
                checked={formData.privacy_bio === 1}
                onChange={(e) => setFormData({ ...formData, privacy_bio: e.target.checked ? 1 : 0 })}
              />
              Private
            </label>
          </div>

          <div className="form-group">
            <label>Interests (comma-separated)</label>
            <input
              type="text"
              value={formData.interests}
              onChange={(e) => setFormData({ ...formData, interests: e.target.value })}
            />
            <label className="privacy-label">
              <input
                type="checkbox"
                checked={formData.privacy_interests === 1}
                onChange={(e) => setFormData({ ...formData, privacy_interests: e.target.checked ? 1 : 0 })}
              />
              Private
            </label>
          </div>

          <div className="form-group">
            <label>Learning Style</label>
            <select
              value={formData.learning_style}
              onChange={(e) => setFormData({ ...formData, learning_style: e.target.value })}
            >
              <option value="">Select...</option>
              <option value="visual">Visual</option>
              <option value="auditory">Auditory</option>
              <option value="kinesthetic">Kinesthetic</option>
              <option value="reading_writing">Reading/Writing</option>
            </select>
            <label className="privacy-label">
              <input
                type="checkbox"
                checked={formData.privacy_learning_style === 1}
                onChange={(e) => setFormData({ ...formData, privacy_learning_style: e.target.checked ? 1 : 0 })}
              />
              Private
            </label>
          </div>

          <button className="save-btn" onClick={handleSave}>
            Save Changes
          </button>
        </div>
      ) : (
        <div className="profile-view">
          <div className="profile-section">
            <h3>Bio</h3>
            <p>{profile.profile?.bio || 'No bio yet'}</p>
          </div>

          <div className="profile-section">
            <h3>Interests</h3>
            <div className="interest-chips">
              {profile.profile?.interests?.split(',').map((interest, idx) => (
                <span key={idx} className="chip">{interest.trim()}</span>
              )) || <span className="empty">No interests added</span>}
            </div>
          </div>

          <div className="profile-section">
            <h3>Learning Style</h3>
            <p>{profile.profile?.learning_style || 'Not specified'}</p>
          </div>
        </div>
      )}

      <div className="metrics-board">
        <div className="metrics-header">
          <h3>Learning Metrics</h3>
          <button onClick={refreshMetrics}>Refresh</button>
        </div>
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-value">{profile.metrics?.hours_studied?.toFixed(1) || 0}</div>
            <div className="metric-label">Hours Studied</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{profile.metrics?.xp_total || 0}</div>
            <div className="metric-label">Total XP</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{profile.metrics?.streak_days || 0}</div>
            <div className="metric-label">Day Streak</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{profile.metrics?.certifications?.length || 0}</div>
            <div className="metric-label">Certifications</div>
          </div>
        </div>
      </div>

      <div className="skills-summary">
        <h3>Top Skills</h3>
        <div className="skills-list">
          {profile.skills?.slice(0, 5).map((skill) => (
            <div key={skill.id} className="skill-item">
              <div className="skill-info">
                <span className="skill-name">{skill.skill_name}</span>
                <span className="skill-mastery">{(skill.mastery * 100).toFixed(0)}%</span>
              </div>
              <div className="skill-bar">
                <div 
                  className="skill-bar-fill" 
                  style={{ width: `${skill.mastery * 100}%` }}
                />
              </div>
            </div>
          )) || <p className="empty">No skills added yet</p>}
        </div>
      </div>
    </div>
  );
};

export default ProfileDashboard;
