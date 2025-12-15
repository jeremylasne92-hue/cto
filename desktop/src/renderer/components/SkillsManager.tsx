import React, { useState, useEffect } from 'react';
import { UserSkill } from '../../types/profile';
import './SkillsManager.css';

interface SkillsManagerProps {
  userId: number;
}

const SkillsManager: React.FC<SkillsManagerProps> = ({ userId }) => {
  const [skills, setSkills] = useState<UserSkill[]>([]);
  const [newSkill, setNewSkill] = useState({
    skill_id: '',
    skill_name: '',
    mastery: 0,
    visibility: 'public'
  });

  useEffect(() => {
    loadSkills();
  }, [userId]);

  const loadSkills = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/profile/me`, {
        headers: { 'X-User-Id': userId.toString() }
      });
      const data = await response.json();
      setSkills(data.skills || []);
    } catch (error) {
      console.error('Failed to load skills:', error);
    }
  };

  const handleAddSkill = async () => {
    if (!newSkill.skill_name || !newSkill.skill_id) {
      alert('Please fill in skill name and ID');
      return;
    }

    try {
      await fetch('http://localhost:5000/api/profile/skills/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId.toString()
        },
        body: JSON.stringify({
          skills: [...skills.map(s => ({
            skill_id: s.skill_id,
            skill_name: s.skill_name,
            mastery: s.mastery,
            visibility: s.visibility
          })), newSkill]
        })
      });

      setNewSkill({
        skill_id: '',
        skill_name: '',
        mastery: 0,
        visibility: 'public'
      });

      await loadSkills();
    } catch (error) {
      console.error('Failed to add skill:', error);
    }
  };

  const handleUpdateSkill = async (skill: UserSkill, updates: Partial<UserSkill>) => {
    const updatedSkills = skills.map(s => 
      s.id === skill.id ? { ...s, ...updates } : s
    );

    try {
      await fetch('http://localhost:5000/api/profile/skills/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId.toString()
        },
        body: JSON.stringify({
          skills: updatedSkills.map(s => ({
            skill_id: s.skill_id,
            skill_name: s.skill_name,
            mastery: s.mastery,
            visibility: s.visibility
          }))
        })
      });

      await loadSkills();
    } catch (error) {
      console.error('Failed to update skill:', error);
    }
  };

  return (
    <div className="skills-manager">
      <h2>Manage Your Skills</h2>

      <div className="add-skill-form">
        <h3>Add New Skill</h3>
        <div className="form-row">
          <input
            type="text"
            placeholder="Skill ID (e.g., python-basics)"
            value={newSkill.skill_id}
            onChange={(e) => setNewSkill({ ...newSkill, skill_id: e.target.value })}
          />
          <input
            type="text"
            placeholder="Skill Name (e.g., Python Basics)"
            value={newSkill.skill_name}
            onChange={(e) => setNewSkill({ ...newSkill, skill_name: e.target.value })}
          />
          <input
            type="number"
            placeholder="Mastery (0-1)"
            min="0"
            max="1"
            step="0.1"
            value={newSkill.mastery}
            onChange={(e) => setNewSkill({ ...newSkill, mastery: parseFloat(e.target.value) })}
          />
          <select
            value={newSkill.visibility}
            onChange={(e) => setNewSkill({ ...newSkill, visibility: e.target.value })}
          >
            <option value="public">Public</option>
            <option value="private">Private</option>
          </select>
          <button onClick={handleAddSkill}>Add Skill</button>
        </div>
      </div>

      <div className="skills-list">
        <h3>Current Skills</h3>
        {skills.length === 0 ? (
          <p className="empty">No skills added yet</p>
        ) : (
          <div className="skills-table">
            {skills.map((skill) => (
              <div key={skill.id} className="skill-row">
                <div className="skill-col skill-name-col">
                  <strong>{skill.skill_name}</strong>
                  <span className="skill-id">({skill.skill_id})</span>
                </div>
                <div className="skill-col mastery-col">
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={skill.mastery}
                    onChange={(e) => handleUpdateSkill(skill, { mastery: parseFloat(e.target.value) })}
                  />
                  <span className="mastery-value">{(skill.mastery * 100).toFixed(0)}%</span>
                </div>
                <div className="skill-col visibility-col">
                  <select
                    value={skill.visibility}
                    onChange={(e) => handleUpdateSkill(skill, { visibility: e.target.value })}
                  >
                    <option value="public">Public</option>
                    <option value="private">Private</option>
                  </select>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SkillsManager;
