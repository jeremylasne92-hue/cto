import React, { useState } from 'react';
import { ComparisonResult } from '../../types/profile';
import './ComparisonModal.css';

interface ComparisonModalProps {
  userId: number;
  onClose: () => void;
}

const ComparisonModal: React.FC<ComparisonModalProps> = ({ userId, onClose }) => {
  const [compareUserId, setCompareUserId] = useState('');
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleCompare = async () => {
    if (!compareUserId) {
      alert('Please enter a user ID to compare with');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/profile/compare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId.toString()
        },
        body: JSON.stringify({ compare_with_id: parseInt(compareUserId) })
      });

      if (response.ok) {
        const data = await response.json();
        setComparison(data);
      } else {
        const error = await response.json();
        alert(error.error || 'Failed to compare skills');
      }
    } catch (error) {
      console.error('Failed to compare skills:', error);
      alert('Failed to compare skills');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Compare Skills</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>

        <div className="modal-body">
          <div className="comparison-input">
            <input
              type="number"
              placeholder="Enter user ID to compare with"
              value={compareUserId}
              onChange={(e) => setCompareUserId(e.target.value)}
            />
            <button onClick={handleCompare} disabled={loading}>
              {loading ? 'Comparing...' : 'Compare'}
            </button>
          </div>

          {comparison && (
            <div className="comparison-results">
              <div className="comparison-header">
                <div className="user-badge">@{comparison.user1.handle}</div>
                <span>vs</span>
                <div className="user-badge">@{comparison.user2.handle}</div>
              </div>

              {comparison.common_skills.length > 0 && (
                <div className="skills-section">
                  <h3>Common Skills</h3>
                  <div className="skills-comparison-list">
                    {comparison.common_skills.map((skill, idx) => (
                      <div key={idx} className="skill-comparison">
                        <div className="skill-name">{skill.skill_name}</div>
                        <div className="skill-bars">
                          <div className="skill-bar-row">
                            <span className="user-label">You</span>
                            <div className="skill-bar">
                              <div
                                className="skill-bar-fill user1"
                                style={{ width: `${skill.user1_mastery * 100}%` }}
                              />
                            </div>
                            <span className="mastery-value">{(skill.user1_mastery * 100).toFixed(0)}%</span>
                          </div>
                          <div className="skill-bar-row">
                            <span className="user-label">Them</span>
                            <div className="skill-bar">
                              <div
                                className="skill-bar-fill user2"
                                style={{ width: `${skill.user2_mastery * 100}%` }}
                              />
                            </div>
                            <span className="mastery-value">{(skill.user2_mastery * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                        {skill.difference !== 0 && (
                          <div className={`difference ${skill.difference > 0 ? 'ahead' : 'behind'}`}>
                            {skill.difference > 0 ? '+' : ''}{(skill.difference * 100).toFixed(0)}%
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="unique-skills-container">
                {comparison.user1_unique_skills.length > 0 && (
                  <div className="skills-section">
                    <h3>Your Unique Skills</h3>
                    <div className="unique-skills-list">
                      {comparison.user1_unique_skills.map((skill) => (
                        <div key={skill.id} className="unique-skill">
                          <span>{skill.skill_name}</span>
                          <span className="mastery">{(skill.mastery * 100).toFixed(0)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {comparison.user2_unique_skills.length > 0 && (
                  <div className="skills-section">
                    <h3>Their Unique Skills</h3>
                    <div className="unique-skills-list">
                      {comparison.user2_unique_skills.map((skill) => (
                        <div key={skill.id} className="unique-skill">
                          <span>{skill.skill_name}</span>
                          <span className="mastery">{(skill.mastery * 100).toFixed(0)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ComparisonModal;
