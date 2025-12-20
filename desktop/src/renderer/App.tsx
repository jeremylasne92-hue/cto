import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Types
interface UserProfile {
  user: {
    id: number;
    handle: string;
    is_private: boolean;
  };
  profile: {
    user_id: number;
    bio: string;
    interests: string[];
    learning_style: string;
    privacy_bio: boolean;
    privacy_interests: boolean;
    privacy_learning_style: boolean;
  };
  skills: Array<{
    skill_id: string;
    mastery_level: number;
    visibility: boolean;
  }>;
  metrics: {
    hours_studied: number;
    xp_total: number;
    streak_days: number;
    certifications: string[];
  };
}

interface Follower {
  id: number;
  handle: string;
  followed_at: string;
  profile_summary: {
    bio: string;
    interests: string[];
  };
}

interface SkillComparison {
  skill_id: string;
  user1_level: number;
  user2_level: number;
  difference: number;
}

const API_BASE_URL = 'http://localhost:5000/api/profile';

// Main App Component
const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'profile' | 'skills' | 'social' | 'compare'>('profile');
  const [userId, setUserId] = useState<number>(1); // Mock user ID
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [followers, setFollowers] = useState<Follower[]>([]);
  const [following, setFollowing] = useState<Follower[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadUserData();
  }, [userId]);

  const loadUserData = async () => {
    setLoading(true);
    setError('');
    try {
      const [profileResponse, followersResponse, followingResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/${userId}?include_private=true`),
        axios.get(`${API_BASE_URL}/followers/${userId}`),
        axios.get(`${API_BASE_URL}/following/${userId}`)
      ]);

      if (profileResponse.data.success) {
        setProfile(profileResponse.data.profile);
      }
      if (followersResponse.data.success) {
        setFollowers(followersResponse.data.followers);
      }
      if (followingResponse.data.success) {
        setFollowing(followingResponse.data.following);
      }
    } catch (err) {
      setError('Failed to load user data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: '👤' },
    { id: 'skills', label: 'Skills', icon: '🎯' },
    { id: 'social', label: 'Social', icon: '👥' },
    { id: 'compare', label: 'Compare', icon: '📊' }
  ];

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Social Learning Platform</h1>
      
      {/* Tab Navigation */}
      <div style={{ display: 'flex', marginBottom: '20px', borderBottom: '1px solid #ccc' }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            style={{
              padding: '10px 20px',
              border: 'none',
              background: activeTab === tab.id ? '#007bff' : '#f8f9fa',
              color: activeTab === tab.id ? 'white' : 'black',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Error Display */}
      {error && (
        <div style={{ backgroundColor: '#f8d7da', color: '#721c24', padding: '10px', borderRadius: '4px', marginBottom: '20px' }}>
          {error}
        </div>
      )}

      {/* Loading Display */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          Loading...
        </div>
      )}

      {/* Tab Content */}
      {activeTab === 'profile' && profile && <ProfileDashboard profile={profile} onUpdate={loadUserData} />}
      {activeTab === 'skills' && profile && <SkillsManager profile={profile} onUpdate={loadUserData} />}
      {activeTab === 'social' && (
        <SocialTab 
          followers={followers} 
          following={following} 
          userId={userId}
          onUpdate={loadUserData}
        />
      )}
      {activeTab === 'compare' && profile && <ComparisonModal currentUserId={userId} />}
    </div>
  );
};

// Profile Dashboard Component
const ProfileDashboard: React.FC<{ profile: UserProfile; onUpdate: () => void }> = ({ profile, onUpdate }) => {
  const [bio, setBio] = useState(profile.profile.bio);
  const [learningStyle, setLearningStyle] = useState(profile.profile.learning_style);
  const [interests, setInterests] = useState<string[]>(profile.profile.interests);
  const [newInterest, setNewInterest] = useState('');

  const handleSaveProfile = async () => {
    try {
      await axios.post(`${API_BASE_URL}/upsert`, {
        user_id: profile.user.id,
        handle: profile.user.handle,
        bio,
        interests,
        learning_style
      });
      onUpdate();
    } catch (err) {
      console.error('Failed to save profile', err);
    }
  };

  const addInterest = () => {
    if (newInterest && !interests.includes(newInterest)) {
      setInterests([...interests, newInterest]);
      setNewInterest('');
    }
  };

  const removeInterest = (interest: string) => {
    setInterests(interests.filter(i => i !== interest));
  };

  return (
    <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <h2>Profile Dashboard</h2>
      
      {/* Bio Section */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Bio</label>
        <textarea
          value={bio}
          onChange={(e) => setBio(e.target.value)}
          placeholder="Tell us about yourself..."
          style={{ width: '100%', height: '100px', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
        />
      </div>

      {/* Learning Style Section */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Learning Style</label>
        <input
          type="text"
          value={learningStyle}
          onChange={(e) => setLearningStyle(e.target.value)}
          placeholder="e.g., Visual, Auditory, Kinesthetic"
          style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
        />
      </div>

      {/* Interests Section */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Interests</label>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
          <input
            type="text"
            value={newInterest}
            onChange={(e) => setNewInterest(e.target.value)}
            placeholder="Add interest..."
            style={{ flex: 1, padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
          />
          <button onClick={addInterest} style={{ padding: '8px 16px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px' }}>
            Add
          </button>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {interests.map((interest, index) => (
            <span
              key={index}
              style={{
                backgroundColor: '#e9ecef',
                padding: '4px 8px',
                borderRadius: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              {interest}
              <button
                onClick={() => removeInterest(interest)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#dc3545',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      {/* Metrics Board */}
      <div style={{ marginBottom: '20px' }}>
        <h3>Learning Metrics</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px' }}>
          <MetricCard title="Hours Studied" value={profile.metrics?.hours_studied?.toFixed(1) || '0.0'} unit="hours" icon="⏰" />
          <MetricCard title="XP Total" value={profile.metrics?.xp_total?.toString() || '0'} unit="points" icon="⭐" />
          <MetricCard title="Streak" value={profile.metrics?.streak_days?.toString() || '0'} unit="days" icon="🔥" />
          <MetricCard title="Certifications" value={profile.metrics?.certifications?.length?.toString() || '0'} unit="certs" icon="🏆" />
        </div>
      </div>

      {/* Save Button */}
      <button
        onClick={handleSaveProfile}
        style={{
          padding: '10px 20px',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        Save Profile
      </button>
    </div>
  );
};

// Metric Card Component
const MetricCard: React.FC<{ title: string; value: string; unit: string; icon: string }> = ({ title, value, unit, icon }) => (
  <div style={{
    backgroundColor: '#f8f9fa',
    padding: '15px',
    borderRadius: '8px',
    textAlign: 'center',
    border: '1px solid #dee2e6'
  }}>
    <div style={{ fontSize: '24px', marginBottom: '5px' }}>{icon}</div>
    <div style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '2px' }}>{value}</div>
    <div style={{ fontSize: '12px', color: '#6c757d' }}>{unit}</div>
    <div style={{ fontSize: '14px', color: '#495057' }}>{title}</div>
  </div>
);

// Skills Manager Component
const SkillsManager: React.FC<{ profile: UserProfile; onUpdate: () => void }> = ({ profile, onUpdate }) => {
  const [skills, setSkills] = useState(profile.skills);
  const [newSkill, setNewSkill] = useState({ skill_id: '', mastery_level: 1, visibility: true });

  const handleSaveSkills = async () => {
    try {
      await axios.post(`${API_BASE_URL}/skills/update`, {
        user_id: profile.user.id,
        skills: skills
      });
      onUpdate();
    } catch (err) {
      console.error('Failed to save skills', err);
    }
  };

  const updateSkill = (index: number, field: string, value: any) => {
    const updatedSkills = [...skills];
    updatedSkills[index] = { ...updatedSkills[index], [field]: value };
    setSkills(updatedSkills);
  };

  const addSkill = () => {
    if (newSkill.skill_id) {
      setSkills([...skills, newSkill]);
      setNewSkill({ skill_id: '', mastery_level: 1, visibility: true });
    }
  };

  const removeSkill = (index: number) => {
    setSkills(skills.filter((_, i) => i !== index));
  };

  return (
    <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <h2>Skills Management</h2>
      
      {/* Add New Skill */}
      <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
        <h4>Add New Skill</h4>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <input
            type="text"
            placeholder="Skill ID (e.g., python, javascript)"
            value={newSkill.skill_id}
            onChange={(e) => setNewSkill({ ...newSkill, skill_id: e.target.value })}
            style={{ flex: 1, padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
          />
          <select
            value={newSkill.mastery_level}
            onChange={(e) => setNewSkill({ ...newSkill, mastery_level: parseInt(e.target.value) })}
            style={{ padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
          >
            {[1, 2, 3, 4, 5].map(level => (
              <option key={level} value={level}>Level {level}</option>
            ))}
          </select>
          <label style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <input
              type="checkbox"
              checked={newSkill.visibility}
              onChange={(e) => setNewSkill({ ...newSkill, visibility: e.target.checked })}
            />
            Public
          </label>
          <button onClick={addSkill} style={{ padding: '8px 16px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px' }}>
            Add
          </button>
        </div>
      </div>

      {/* Skills List */}
      <div style={{ marginBottom: '20px' }}>
        <h4>Your Skills</h4>
        {skills.length === 0 ? (
          <p style={{ color: '#6c757d', fontStyle: 'italic' }}>No skills added yet. Add your first skill above!</p>
        ) : (
          skills.map((skill, index) => (
            <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px', marginBottom: '8px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
              <input
                type="text"
                value={skill.skill_id}
                onChange={(e) => updateSkill(index, 'skill_id', e.target.value)}
                style={{ flex: 1, padding: '6px', border: '1px solid #ccc', borderRadius: '4px' }}
              />
              <select
                value={skill.mastery_level}
                onChange={(e) => updateSkill(index, 'mastery_level', parseInt(e.target.value))}
                style={{ padding: '6px', border: '1px solid #ccc', borderRadius: '4px' }}
              >
                {[1, 2, 3, 4, 5].map(level => (
                  <option key={level} value={level}>Level {level}</option>
                ))}
              </select>
              <label style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '14px' }}>
                <input
                  type="checkbox"
                  checked={skill.visibility}
                  onChange={(e) => updateSkill(index, 'visibility', e.target.checked)}
                />
                Public
              </label>
              <button
                onClick={() => removeSkill(index)}
                style={{
                  backgroundColor: '#dc3545',
                  color: 'white',
                  border: 'none',
                  padding: '6px 8px',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Remove
              </button>
            </div>
          ))
        )}
      </div>

      {/* Save Button */}
      <button
        onClick={handleSaveSkills}
        style={{
          padding: '10px 20px',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        Save Skills
      </button>
    </div>
  );
};

// Social Tab Component
const SocialTab: React.FC<{ followers: Follower[]; following: Follower[]; userId: number; onUpdate: () => void }> = ({ 
  followers, following, userId, onUpdate 
}) => {
  const [compareUserId, setCompareUserId] = useState('');

  const handleFollow = async (targetUserId: number) => {
    try {
      await axios.post(`${API_BASE_URL}/follow`, {
        follower_id: userId,
        followee_id: targetUserId
      });
      onUpdate();
    } catch (err) {
      console.error('Failed to follow user', err);
    }
  };

  const handleUnfollow = async (targetUserId: number) => {
    try {
      await axios.post(`${API_BASE_URL}/unfollow`, {
        follower_id: userId,
        followee_id: targetUserId
      });
      onUpdate();
    } catch (err) {
      console.error('Failed to unfollow user', err);
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
      {/* Followers */}
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h3>Followers ({followers.length})</h3>
        {followers.length === 0 ? (
          <p style={{ color: '#6c757d', fontStyle: 'italic' }}>No followers yet</p>
        ) : (
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {followers.map(follower => (
              <div key={follower.id} style={{ padding: '10px', borderBottom: '1px solid #eee' }}>
                <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>@{follower.handle}</div>
                {follower.profile_summary?.bio && (
                  <div style={{ fontSize: '14px', color: '#6c757d', marginBottom: '4px' }}>
                    {follower.profile_summary.bio}
                  </div>
                )}
                <div style={{ fontSize: '12px', color: '#adb5bd' }}>
                  Following since {new Date(follower.followed_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Following */}
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h3>Following ({following.length})</h3>
        {following.length === 0 ? (
          <p style={{ color: '#6c757d', fontStyle: 'italic' }}>Not following anyone yet</p>
        ) : (
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {following.map(user => (
              <div key={user.id} style={{ padding: '10px', borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>@{user.handle}</div>
                  {user.profile_summary?.bio && (
                    <div style={{ fontSize: '14px', color: '#6c757d', marginBottom: '4px' }}>
                      {user.profile_summary.bio}
                    </div>
                  )}
                  <div style={{ fontSize: '12px', color: '#adb5bd' }}>
                    Following since {new Date(user.followed_at).toLocaleDateString()}
                  </div>
                </div>
                <button
                  onClick={() => handleUnfollow(user.id)}
                  style={{
                    backgroundColor: '#dc3545',
                    color: 'white',
                    border: 'none',
                    padding: '6px 12px',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '12px'
                  }}
                >
                  Unfollow
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Comparison Modal Component
const ComparisonModal: React.FC<{ currentUserId: number }> = ({ currentUserId }) => {
  const [compareUserId, setCompareUserId] = useState('');
  const [comparison, setComparison] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleCompare = async () => {
    if (!compareUserId) return;
    
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/compare`, {
        user1_id: currentUserId,
        user2_id: parseInt(compareUserId)
      });
      
      if (response.data.success) {
        setComparison(response.data.comparison);
      }
    } catch (err) {
      console.error('Failed to compare users', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <h2>Skill Comparison</h2>
      
      {/* Comparison Input */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
          Compare with User ID:
        </label>
        <div style={{ display: 'flex', gap: '10px' }}>
          <input
            type="number"
            value={compareUserId}
            onChange={(e) => setCompareUserId(e.target.value)}
            placeholder="Enter user ID to compare with"
            style={{ flex: 1, padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
          />
          <button
            onClick={handleCompare}
            disabled={!compareUserId || loading}
            style={{
              padding: '8px 16px',
              backgroundColor: compareUserId && !loading ? '#007bff' : '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: compareUserId && !loading ? 'pointer' : 'not-allowed'
            }}
          >
            {loading ? 'Comparing...' : 'Compare'}
          </button>
        </div>
      </div>

      {/* Comparison Results */}
      {comparison && (
        <div style={{ marginTop: '20px' }}>
          <h3>Comparison Results</h3>
          
          {/* Summary */}
          <div style={{ backgroundColor: '#f8f9fa', padding: '15px', borderRadius: '8px', marginBottom: '15px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px', textAlign: 'center' }}>
              <div>
                <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{comparison.summary?.total_common || 0}</div>
                <div style={{ fontSize: '12px', color: '#6c757d' }}>Common Skills</div>
              </div>
              <div>
                <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{comparison.summary?.user1_unique_count || 0}</div>
                <div style={{ fontSize: '12px', color: '#6c757d' }}>Your Unique</div>
              </div>
              <div>
                <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{comparison.summary?.user2_unique_count || 0}</div>
                <div style={{ fontSize: '12px', color: '#6c757d' }}>Their Unique</div>
              </div>
              <div>
                <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{comparison.summary?.overlap_percentage?.toFixed(1) || 0}%</div>
                <div style={{ fontSize: '12px', color: '#6c757d' }}>Overlap</div>
              </div>
            </div>
          </div>

          {/* Common Skills */}
          {comparison.common_skills?.length > 0 && (
            <div style={{ marginBottom: '15px' }}>
              <h4>Common Skills</h4>
              {comparison.common_skills.map((skill: SkillComparison, index: number) => (
                <div key={index} style={{ padding: '8px', backgroundColor: '#f8f9fa', marginBottom: '5px', borderRadius: '4px' }}>
                  <div style={{ fontWeight: 'bold' }}>{skill.skill_id}</div>
                  <div style={{ fontSize: '14px', color: '#6c757d' }}>
                    You: Level {skill.user1_level} | Them: Level {skill.user2_level}
                    {skill.difference !== 0 && (
                      <span style={{ color: skill.difference > 0 ? '#28a745' : '#dc3545', marginLeft: '10px' }}>
                        {skill.difference > 0 ? '+' : ''}{skill.difference} levels
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Recommendations */}
          {comparison.recommendations?.length > 0 && (
            <div>
              <h4>Learning Recommendations</h4>
              {comparison.recommendations.map((rec: any, index: number) => (
                <div key={index} style={{ padding: '8px', backgroundColor: '#e7f3ff', marginBottom: '5px', borderRadius: '4px', borderLeft: '3px solid #007bff' }}>
                  <div style={{ fontWeight: 'bold' }}>Learn: {rec.skill_id}</div>
                  <div style={{ fontSize: '14px', color: '#6c757d' }}>{rec.reason}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default App;