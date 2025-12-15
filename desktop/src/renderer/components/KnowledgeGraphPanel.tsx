import React, { useState, useCallback, useRef, useEffect } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import ForceGraph3D from 'react-force-graph-3d';
import { useKnowledgeGraph } from '../hooks/useKnowledgeGraph';
import { ConceptSidebar } from './ConceptSidebar';
import { GraphControls } from './GraphControls';
import { MasteryLegend } from './MasteryLegend';
import './KnowledgeGraphPanel.css';

interface KnowledgeGraphPanelProps {
  userId?: number;
  initialDepth?: number;
}

export const KnowledgeGraphPanel: React.FC<KnowledgeGraphPanelProps> = ({
  userId,
  initialDepth,
}) => {
  const [depth, setDepth] = useState(initialDepth);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [showPrerequisites, setShowPrerequisites] = useState(true);
  const [showDependencies, setShowDependencies] = useState(true);
  const [masteryFilter, setMasteryFilter] = useState<string | null>(null);
  const [use3D, setUse3D] = useState(false);
  const graphRef = useRef<any>();
  
  const {
    graphData,
    loading,
    error,
    useWebGL,
    setUseWebGL,
    refetch,
    createConcept,
    updateConcept,
    deleteConcept,
    createRelation,
    saveLayoutPositions,
    runIntegrityCheck,
  } = useKnowledgeGraph({ userId, depth, searchTerm });
  
  const filteredGraphData = React.useMemo(() => {
    if (!graphData) return null;
    
    let nodes = [...graphData.nodes];
    let edges = [...graphData.edges];
    
    if (masteryFilter) {
      nodes = nodes.filter(node => {
        const mastery = node.mastery || 0;
        switch (masteryFilter) {
          case 'green':
            return mastery > 80;
          case 'yellow':
            return mastery >= 50 && mastery <= 80;
          case 'orange':
            return mastery >= 20 && mastery < 50;
          case 'gray':
            return mastery < 20;
          default:
            return true;
        }
      });
      
      const nodeIds = new Set(nodes.map(n => n.id));
      edges = edges.filter(e => nodeIds.has(e.source) && nodeIds.has(e.target));
    }
    
    if (!showPrerequisites) {
      edges = edges.filter(e => !e.is_prerequisite);
    }
    
    if (!showDependencies) {
      edges = edges.filter(e => !e.is_dependency);
    }
    
    return { ...graphData, nodes, edges };
  }, [graphData, showPrerequisites, showDependencies, masteryFilter]);
  
  const handleNodeClick = useCallback((node: any) => {
    setSelectedNode(node);
  }, []);
  
  const handleNodeRightClick = useCallback((node: any, event: MouseEvent) => {
    event.preventDefault();
    setSelectedNode(node);
  }, []);
  
  const handleBackgroundClick = useCallback(() => {
    setSelectedNode(null);
  }, []);
  
  const handleSaveLayout = useCallback(() => {
    if (!graphRef.current || !filteredGraphData) return;
    
    const positions: Record<string, any> = {};
    filteredGraphData.nodes.forEach(node => {
      positions[node.id] = {
        x: node.x || 0,
        y: node.y || 0,
        z: node.z || 0,
      };
    });
    
    saveLayoutPositions(positions);
  }, [filteredGraphData, saveLayoutPositions]);
  
  useEffect(() => {
    const interval = setInterval(handleSaveLayout, 5000);
    return () => clearInterval(interval);
  }, [handleSaveLayout]);
  
  const handleIntegrityCheck = async () => {
    const report = await runIntegrityCheck();
    if (report) {
      if (report.has_issues) {
        alert(`Integrity issues found:\n${JSON.stringify(report.summary, null, 2)}`);
      } else {
        alert('No integrity issues found!');
      }
    }
  };
  
  if (loading && !graphData) {
    return (
      <div className="knowledge-graph-loading">
        <div className="spinner"></div>
        <p>Loading knowledge graph...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="knowledge-graph-error">
        <h3>Error loading graph</h3>
        <p>{error}</p>
        <button onClick={refetch}>Retry</button>
      </div>
    );
  }
  
  if (!filteredGraphData) {
    return <div>No graph data available</div>;
  }
  
  const ForceGraphComponent = use3D ? ForceGraph3D : ForceGraph2D;
  
  return (
    <div className="knowledge-graph-panel">
      <GraphControls
        depth={depth}
        setDepth={setDepth}
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        showPrerequisites={showPrerequisites}
        setShowPrerequisites={setShowPrerequisites}
        showDependencies={showDependencies}
        setShowDependencies={setShowDependencies}
        use3D={use3D}
        setUse3D={setUse3D}
        useWebGL={useWebGL}
        setUseWebGL={setUseWebGL}
        onRefresh={refetch}
        onIntegrityCheck={handleIntegrityCheck}
        onSaveLayout={handleSaveLayout}
      />
      
      <div className="graph-container">
        <ForceGraphComponent
          ref={graphRef}
          graphData={filteredGraphData}
          nodeLabel="name"
          nodeColor={(node: any) => node.color || '#6b7280'}
          nodeRelSize={6}
          nodeVal={(node: any) => Math.max(node.review_count || 1, 1)}
          linkLabel={(link: any) => link.type}
          linkColor={() => '#94a3b8'}
          linkWidth={(link: any) => link.strength || 1}
          linkDirectionalArrowLength={3.5}
          linkDirectionalArrowRelPos={1}
          onNodeClick={handleNodeClick}
          onNodeRightClick={handleNodeRightClick}
          onBackgroundClick={handleBackgroundClick}
          enableNodeDrag={true}
          cooldownTicks={100}
          d3AlphaDecay={0.02}
          d3VelocityDecay={0.3}
        />
        
        <MasteryLegend
          masteryFilter={masteryFilter}
          setMasteryFilter={setMasteryFilter}
        />
      </div>
      
      {selectedNode && (
        <ConceptSidebar
          node={selectedNode}
          onClose={() => setSelectedNode(null)}
          onUpdate={updateConcept}
          onDelete={async (id) => {
            const success = await deleteConcept(id);
            if (success) {
              setSelectedNode(null);
            }
          }}
          onCreate={createConcept}
          onCreateRelation={createRelation}
          graphData={filteredGraphData}
        />
      )}
    </div>
  );
};
