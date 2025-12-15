import React, { useState } from 'react';
import './ConceptSidebar.css';

interface ConceptSidebarProps {
  node: any;
  onClose: () => void;
  onUpdate: (id: string, name?: string, description?: string, metadata?: any) => Promise<any>;
  onDelete: (id: string) => Promise<boolean>;
  onCreate: (name: string, description?: string, metadata?: any) => Promise<any>;
  onCreateRelation: (sourceId: string, targetId: string, type: string, strength: number) => Promise<any>;
  graphData: any;
}

export const ConceptSidebar: React.FC<ConceptSidebarProps> = ({
  node,
  onClose,
  onUpdate,
  onDelete,
  onCreate,
  onCreateRelation,
  graphData,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(node.name);
  const [description, setDescription] = useState(node.description || '');
  const [showAddRelation, setShowAddRelation] = useState(false);
  const [relationTarget, setRelationTarget] = useState('');
  const [relationType, setRelationType] = useState('related');
  const [relationStrength, setRelationStrength] = useState(1.0);
  
  const handleSave = async () => {
    await onUpdate(node.id, name, description);
    setIsEditing(false);
  };
  
  const handleDelete = async () => {
    if (window.confirm(`Are you sure you want to delete "${node.name}"?`)) {
      await onDelete(node.id);
    }
  };
  
  const handleAddRelation = async () => {
    if (!relationTarget) return;
    
    await onCreateRelation(node.id, relationTarget, relationType, relationStrength);
    setShowAddRelation(false);
    setRelationTarget('');
  };
  
  const getMasteryLabel = (mastery: number) => {
    if (mastery > 80) return 'Mastered';
    if (mastery >= 50) return 'Learning';
    if (mastery >= 20) return 'Beginner';
    return 'Not Started';
  };
  
  const connectedNodes = graphData.edges
    .filter((e: any) => e.source === node.id || e.target === node.id)
    .map((e: any) => {
      const targetId = e.source === node.id ? e.target : e.source;
      const targetNode = graphData.nodes.find((n: any) => n.id === targetId);
      return { edge: e, node: targetNode };
    })
    .filter((item: any) => item.node);
  
  return (
    <div className="concept-sidebar">
      <div className="sidebar-header">
        <h2>{isEditing ? 'Edit Concept' : 'Concept Details'}</h2>
        <button className="close-button" onClick={onClose}>×</button>
      </div>
      
      <div className="sidebar-content">
        {isEditing ? (
          <div className="edit-form">
            <div className="form-group">
              <label>Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Concept name"
              />
            </div>
            
            <div className="form-group">
              <label>Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Concept description"
                rows={4}
              />
            </div>
            
            <div className="button-group">
              <button className="btn-primary" onClick={handleSave}>Save</button>
              <button className="btn-secondary" onClick={() => setIsEditing(false)}>Cancel</button>
            </div>
          </div>
        ) : (
          <div className="view-mode">
            <div className="info-section">
              <h3>{node.name}</h3>
              {node.description && <p className="description">{node.description}</p>}
            </div>
            
            <div className="mastery-section">
              <div className="mastery-bar">
                <div
                  className="mastery-fill"
                  style={{
                    width: `${node.mastery || 0}%`,
                    backgroundColor: node.color,
                  }}
                />
              </div>
              <div className="mastery-info">
                <span className="mastery-label">{getMasteryLabel(node.mastery || 0)}</span>
                <span className="mastery-percent">{Math.round(node.mastery || 0)}%</span>
              </div>
              <div className="review-count">
                Reviews: {node.review_count || 0}
              </div>
              {node.last_assessed && (
                <div className="last-assessed">
                  Last assessed: {new Date(node.last_assessed).toLocaleDateString()}
                </div>
              )}
            </div>
            
            <div className="connections-section">
              <h4>Connections ({connectedNodes.length})</h4>
              <ul className="connections-list">
                {connectedNodes.map((item: any) => (
                  <li key={item.edge.id} className="connection-item">
                    <span className="connection-name">{item.node.name}</span>
                    <span className="connection-type">{item.edge.type}</span>
                  </li>
                ))}
              </ul>
              
              <button
                className="btn-secondary add-relation-btn"
                onClick={() => setShowAddRelation(!showAddRelation)}
              >
                + Add Relation
              </button>
              
              {showAddRelation && (
                <div className="add-relation-form">
                  <select
                    value={relationTarget}
                    onChange={(e) => setRelationTarget(e.target.value)}
                  >
                    <option value="">Select concept...</option>
                    {graphData.nodes
                      .filter((n: any) => n.id !== node.id)
                      .map((n: any) => (
                        <option key={n.id} value={n.id}>{n.name}</option>
                      ))}
                  </select>
                  
                  <select
                    value={relationType}
                    onChange={(e) => setRelationType(e.target.value)}
                  >
                    <option value="related">Related</option>
                    <option value="prerequisite">Prerequisite</option>
                    <option value="dependency">Dependency</option>
                  </select>
                  
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    value={relationStrength}
                    onChange={(e) => setRelationStrength(parseFloat(e.target.value))}
                    placeholder="Strength"
                  />
                  
                  <button className="btn-primary" onClick={handleAddRelation}>
                    Add
                  </button>
                </div>
              )}
            </div>
            
            <div className="button-group">
              <button className="btn-primary" onClick={() => setIsEditing(true)}>Edit</button>
              <button className="btn-danger" onClick={handleDelete}>Delete</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
