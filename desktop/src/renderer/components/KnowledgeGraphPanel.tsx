"""
Knowledge Graph Panel - Main visualization component for desktop
"""
import React, { useState, useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { 
  useKnowledgeGraph, 
  type GraphNode, 
  type GraphLink,
  type ConceptData,
  type RelationData,
  type SearchResult
} from '../hooks/useKnowledgeGraph';

interface KnowledgeGraphPanelProps {
  userId?: string;
  className?: string;
}

const KnowledgeGraphPanel: React.FC<KnowledgeGraphPanelProps> = ({ 
  userId = 'default',
  className = '' 
}) => {
  const {
    graphData,
    selectedNode,
    isLoading,
    error,
    stats,
    hardwareInfo,
    loadGraph,
    searchConcepts,
    createConcept,
    updateConcept,
    deleteConcept,
    createRelation,
    findRelated,
    runIntegrityCheck,
    updateMastery,
    setSelectedNode,
    clearError
  } = useKnowledgeGraph(userId);

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showIntegrityCheck, setShowIntegrityCheck] = useState(false);
  const [integrityResults, setIntegrityResults] = useState<any>(null);
  const [rendererType, setRendererType] = useState<'webgl' | 'canvas'>('canvas');
  const [conceptFilter, setConceptFilter] = useState<string>('all');

  const graphRef = useRef<any>();

  // Determine renderer type based on hardware capabilities
  useEffect(() => {
    if (hardwareInfo) {
      const preferred = hardwareInfo.recommendedRenderer;
      setRendererType(preferred);
    }
  }, [hardwareInfo]);

  // Handle search
  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    const results = await searchConcepts(query);
    setSearchResults(results);
  };

  // Handle node selection
  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node);
  };

  // Handle concept creation
  const handleCreateConcept = async (conceptData: ConceptData) => {
    try {
      await createConcept(conceptData);
      setShowCreateForm(false);
    } catch (err) {
      console.error('Failed to create concept:', err);
    }
  };

  // Handle concept deletion
  const handleDeleteConcept = async (node: GraphNode) => {
    if (window.confirm(`Delete concept "${node.name}"? This will remove all related relations.`)) {
      try {
        await deleteConcept(node.id, true); // Force delete to remove relations
        setSelectedNode(null);
      } catch (err) {
        console.error('Failed to delete concept:', err);
      }
    }
  };

  // Handle relation creation
  const handleCreateRelation = async (sourceId: number, targetName: string) => {
    // Find target concept by name
    const targetConcept = graphData?.nodes.find(n => n.name === targetName);
    if (!targetConcept) {
      alert('Target concept not found');
      return;
    }

    const relationData: RelationData = {
      target_concept_id: targetConcept.id,
      relation_type: 'prerequisite',
      strength: 1.0
    };

    try {
      await createRelation(sourceId, relationData);
    } catch (err) {
      console.error('Failed to create relation:', err);
    }
  };

  // Get color for node based on mastery
  const getNodeColor = (node: GraphNode): string => {
    switch (node.color) {
      case 'green': return '#10B981'; // emerald-500
      case 'yellow': return '#F59E0B'; // amber-500
      case 'orange': return '#F97316'; // orange-500
      case 'gray': return '#6B7280'; // gray-500
      default: return '#6B7280';
    }
  };

  // Filter nodes based on selected filter
  const getFilteredData = () => {
    if (!graphData) return null;

    let filteredNodes = graphData.nodes;
    let filteredLinks = graphData.links;

    // Apply concept filter
    if (conceptFilter !== 'all') {
      filteredNodes = graphData.nodes.filter(node => node.color === conceptFilter);
      const nodeIds = new Set(filteredNodes.map(n => n.id));
      filteredLinks = graphData.links.filter(link => 
        nodeIds.has(link.source as number) && nodeIds.has(link.target as number)
      );
    }

    return {
      nodes: filteredNodes.map(node => ({
        ...node,
        val: Math.max(5, node.review_count * 2), // Node size based on review count
        color: getNodeColor(node),
        fontSize: Math.max(10, 14 - (node.name.length * 0.5)) // Adjust font size based on name length
      })),
      links: filteredLinks
    };
  };

  const filteredData = getFilteredData();

  return (
    <div className={`knowledge-graph-panel ${className}`}>
      {/* Header */}
      <div className="panel-header">
        <div className="header-left">
          <h2>Knowledge Graph</h2>
          {stats && (
            <span className="stats">
              {stats.total_concepts} concepts • {stats.total_relations} relations
            </span>
          )}
        </div>
        
        <div className="header-right">
          <select 
            value={conceptFilter} 
            onChange={(e) => setConceptFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Concepts</option>
            <option value="green">Mastered (80%+)</option>
            <option value="yellow">Learning (50-80%)</option>
            <option value="orange">Struggling (20-50%)</option>
            <option value="gray">Not Started (<20%)</option>
          </select>
          
          <button 
            onClick={() => setShowCreateForm(true)}
            className="btn btn-primary"
          >
            + Add Concept
          </button>
          
          <button 
            onClick={() => setShowIntegrityCheck(true)}
            className="btn btn-secondary"
          >
            Integrity Check
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search concepts..."
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            handleSearch(e.target.value);
          }}
          className="search-input"
        />
        
        {searchResults.length > 0 && (
          <div className="search-results">
            {searchResults.map(result => (
              <div 
                key={result.concept_id}
                className="search-result-item"
                onClick={() => {
                  const node = graphData?.nodes.find(n => n.id === result.concept_id);
                  if (node) {
                    handleNodeClick(node);
                  }
                  setSearchResults([]);
                  setSearchQuery('');
                }}
              >
                <div className="result-name">{result.name}</div>
                <div className="result-description">{result.description}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button onClick={clearError} className="btn-close">×</button>
        </div>
      )}

      {/* Main Content */}
      <div className="graph-container">
        {/* Graph Visualization */}
        <div className="graph-canvas">
          {isLoading ? (
            <div className="loading-spinner">
              <div className="spinner"></div>
              <span>Loading knowledge graph...</span>
            </div>
          ) : filteredData && filteredData.nodes.length > 0 ? (
            <ForceGraph2D
              ref={graphRef}
              graphData={filteredData}
              nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
                const label = node.name;
                const fontSize = node.fontSize / globalScale;
                const textWidth = ctx.measureText(label).width;
                const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);

                // Draw node circle
                ctx.fillStyle = node.color;
                ctx.beginPath();
                ctx.arc(node.x, node.y, node.val / 2, 0, 2 * Math.PI, false);
                ctx.fill();

                // Draw label background
                ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
                ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);

                // Draw label text
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillStyle = '#1F2937';
                ctx.font = `${fontSize}px Sans-Serif`;
                ctx.fillText(label, node.x, node.y);

                // Highlight selected node
                if (selectedNode && node.id === selectedNode.id) {
                  ctx.strokeStyle = '#3B82F6';
                  ctx.lineWidth = 3;
                  ctx.beginPath();
                  ctx.arc(node.x, node.y, (node.val / 2) + 3, 0, 2 * Math.PI, false);
                  ctx.stroke();
                }
              }}
              linkColor={() => '#9CA3AF'}
              linkWidth={2}
              linkDirectionalParticles={2}
              linkDirectionalParticleSpeed={0.005}
              onNodeClick={handleNodeClick}
              onBackgroundClick={() => setSelectedNode(null)}
              nodePointerAreaPaint={(node: any, color: string, ctx: CanvasRenderingContext2D, globalScale: number) => {
                ctx.fillStyle = color;
                ctx.beginPath();
                ctx.arc(node.x, node.y, (node.val / 2) + 5, 0, 2 * Math.PI, false);
                ctx.fill();
              }}
            />
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📊</div>
              <h3>No concepts found</h3>
              <p>Create your first concept to start building your knowledge graph.</p>
              <button 
                onClick={() => setShowCreateForm(true)}
                className="btn btn-primary"
              >
                Create First Concept
              </button>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="graph-sidebar">
          {/* Legend */}
          <div className="legend">
            <h4>Mastery Levels</h4>
            <div className="legend-items">
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#10B981' }}></div>
                <span>Mastered (80%+)</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#F59E0B' }}></div>
                <span>Learning (50-80%)</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#F97316' }}></div>
                <span>Struggling (20-50%)</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#6B7280' }}></div>
                <span>Not Started (<20%)</span>
              </div>
            </div>
          </div>

          {/* Selected Node Details */}
          {selectedNode && (
            <div className="node-details">
              <h4>Concept Details</h4>
              <div className="concept-info">
                <div className="concept-name">{selectedNode.name}</div>
                <div className="concept-description">{selectedNode.description}</div>
                
                <div className="mastery-info">
                  <div className="mastery-level">
                    <span>Mastery: {selectedNode.mastery.toFixed(1)}%</span>
                    <div className="mastery-bar">
                      <div 
                        className="mastery-progress" 
                        style={{ 
                          width: `${selectedNode.mastery}%`,
                          backgroundColor: getNodeColor(selectedNode)
                        }}
                      ></div>
                    </div>
                  </div>
                  <div className="review-count">
                    Reviews: {selectedNode.review_count}
                  </div>
                </div>

                {selectedNode.prerequisites && selectedNode.prerequisites.length > 0 && (
                  <div className="relations">
                    <h5>Prerequisites:</h5>
                    <ul>
                      {selectedNode.prerequisites.map(prereqId => {
                        const prereqNode = graphData?.nodes.find(n => n.id === prereqId);
                        return prereqNode ? (
                          <li key={prereqId}>{prereqNode.name}</li>
                        ) : null;
                      })}
                    </ul>
                  </div>
                )}

                {selectedNode.dependencies && selectedNode.dependencies.length > 0 && (
                  <div className="relations">
                    <h5>Dependencies:</h5>
                    <ul>
                      {selectedNode.dependencies.map(depId => {
                        const depNode = graphData?.nodes.find(n => n.id === depId);
                        return depNode ? (
                          <li key={depId}>{depNode.name}</li>
                        ) : null;
                      })}
                    </ul>
                  </div>
                )}

                <div className="node-actions">
                  <button 
                    onClick={() => handleDeleteConcept(selectedNode)}
                    className="btn btn-danger btn-sm"
                  >
                    Delete Concept
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Create Concept Modal */}
      {showCreateForm && (
        <CreateConceptModal
          onClose={() => setShowCreateForm(false)}
          onSubmit={handleCreateConcept}
        />
      )}

      {/* Integrity Check Modal */}
      {showIntegrityCheck && (
        <IntegrityCheckModal
          onClose={() => setShowIntegrityCheck(false)}
          onRunCheck={runIntegrityCheck}
          results={integrityResults}
          onResults={setIntegrityResults}
        />
      )}
    </div>
  );
};

// Create Concept Modal Component
interface CreateConceptModalProps {
  onClose: () => void;
  onSubmit: (data: ConceptData) => void;
}

const CreateConceptModal: React.FC<CreateConceptModalProps> = ({ onClose, onSubmit }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [content, setContent] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    onSubmit({
      name: name.trim(),
      description: description.trim(),
      content: content.trim()
    });
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h3>Create New Concept</h3>
          <button onClick={onClose} className="btn-close">×</button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Name *</label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter concept name"
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description of the concept"
              rows={3}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="content">Content</label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Detailed content or notes"
              rows={5}
            />
          </div>
          
          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Create Concept
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Integrity Check Modal Component
interface IntegrityCheckModalProps {
  onClose: () => void;
  onRunCheck: () => Promise<any>;
  results: any;
  onResults: (results: any) => void;
}

const IntegrityCheckModal: React.FC<IntegrityCheckModalProps> = ({ 
  onClose, 
  onRunCheck, 
  results, 
  onResults 
}) => {
  const [isRunning, setIsRunning] = useState(false);

  const handleRunCheck = async () => {
    setIsRunning(true);
    try {
      const checkResults = await onRunCheck();
      onResults(checkResults);
    } catch (err) {
      console.error('Integrity check failed:', err);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h3>Graph Integrity Check</h3>
          <button onClick={onClose} className="btn-close">×</button>
        </div>
        
        <div className="modal-body">
          <p>Check for graph integrity issues including orphans, cycles, and broken references.</p>
          
          <button 
            onClick={handleRunCheck}
            disabled={isRunning}
            className="btn btn-primary"
          >
            {isRunning ? 'Running Check...' : 'Run Integrity Check'}
          </button>
          
          {results && (
            <div className="integrity-results">
              <div className={`status ${results.status}`}>
                Status: {results.status === 'healthy' ? '✅ Healthy' : `⚠️ ${results.total_issues} Issues Found`}
              </div>
              
              {Object.entries(results.issues).map(([type, issueList]: [string, any]) => {
                if (!issueList || issueList.length === 0) return null;
                
                return (
                  <div key={type} className="issue-category">
                    <h5>{type.replace('_', ' ').toUpperCase()} ({issueList.length})</h5>
                    <ul>
                      {issueList.map((issue: any, index: number) => (
                        <li key={index}>{issue.description}</li>
                      ))}
                    </ul>
                  </div>
                );
              })}
            </div>
          )}
        </div>
        
        <div className="modal-actions">
          <button onClick={onClose} className="btn btn-secondary">
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeGraphPanel;