import React from 'react';
import './GraphControls.css';

interface GraphControlsProps {
  depth?: number;
  setDepth: (depth: number | undefined) => void;
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  showPrerequisites: boolean;
  setShowPrerequisites: (show: boolean) => void;
  showDependencies: boolean;
  setShowDependencies: (show: boolean) => void;
  use3D: boolean;
  setUse3D: (use3D: boolean) => void;
  useWebGL: boolean;
  setUseWebGL: (useWebGL: boolean) => void;
  onRefresh: () => void;
  onIntegrityCheck: () => void;
  onSaveLayout: () => void;
}

export const GraphControls: React.FC<GraphControlsProps> = ({
  depth,
  setDepth,
  searchTerm,
  setSearchTerm,
  showPrerequisites,
  setShowPrerequisites,
  showDependencies,
  setShowDependencies,
  use3D,
  setUse3D,
  useWebGL,
  setUseWebGL,
  onRefresh,
  onIntegrityCheck,
  onSaveLayout,
}) => {
  return (
    <div className="graph-controls">
      <div className="controls-section">
        <div className="control-group">
          <label>Search</label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filter concepts..."
            className="search-input"
          />
        </div>
        
        <div className="control-group">
          <label>Depth</label>
          <input
            type="number"
            min="1"
            max="10"
            value={depth || ''}
            onChange={(e) => setDepth(e.target.value ? parseInt(e.target.value) : undefined)}
            placeholder="All"
            className="depth-input"
          />
        </div>
      </div>
      
      <div className="controls-section filters">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={showPrerequisites}
            onChange={(e) => setShowPrerequisites(e.target.checked)}
          />
          <span>Prerequisites</span>
        </label>
        
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={showDependencies}
            onChange={(e) => setShowDependencies(e.target.checked)}
          />
          <span>Dependencies</span>
        </label>
      </div>
      
      <div className="controls-section rendering">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={use3D}
            onChange={(e) => setUse3D(e.target.checked)}
          />
          <span>3D Mode</span>
        </label>
        
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={useWebGL}
            onChange={(e) => setUseWebGL(e.target.checked)}
          />
          <span>WebGL</span>
        </label>
      </div>
      
      <div className="controls-section actions">
        <button className="btn-icon" onClick={onRefresh} title="Refresh">
          ↻
        </button>
        <button className="btn-icon" onClick={onSaveLayout} title="Save Layout">
          💾
        </button>
        <button className="btn-icon" onClick={onIntegrityCheck} title="Integrity Check">
          ✓
        </button>
      </div>
    </div>
  );
};
