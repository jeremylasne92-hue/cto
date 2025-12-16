import React, { useEffect, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import ForceGraph3D from 'react-force-graph-3d';
import { useKnowledgeGraph } from '../hooks/useKnowledgeGraph';

const KnowledgeGraphPanel: React.FC = () => {
  const { data, fetchGraph, runIntegrityCheck } = useKnowledgeGraph();
  const [hasGPU, setHasGPU] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  
  useEffect(() => {
    window.electronAPI.callBackend('hardware-info', 'GET')
      .then((info: any) => {
          if (info && info.has_gpu === false) {
              setHasGPU(false);
          }
      })
      .catch(console.error);

    fetchGraph();
  }, [fetchGraph]);

  const handleSearch = () => {
      fetchGraph(2, searchTerm);
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div className="toolbar" style={{ padding: '10px', background: '#f0f0f0', display: 'flex', gap: '10px' }}>
        <input 
            type="text" 
            value={searchTerm} 
            onChange={e => setSearchTerm(e.target.value)} 
            placeholder="Search concepts..."
            style={{ padding: '5px' }}
        />
        <button onClick={handleSearch}>Search</button>
        <button onClick={() => runIntegrityCheck().then(res => alert(JSON.stringify(res)))}>Integrity Check</button>
      </div>
      <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
        {hasGPU ? (
            <ForceGraph3D
                graphData={data}
                nodeAutoColorBy="group"
                nodeColor={node => (node as any).color}
                nodeLabel="name"
                linkDirectionalArrowLength={3.5}
                linkDirectionalArrowRelPos={1}
            />
        ) : (
            <ForceGraph2D
                graphData={data}
                nodeColor={node => (node as any).color}
                nodeLabel="name"
                linkDirectionalArrowLength={3.5}
                linkDirectionalArrowRelPos={1}
            />
        )}
      </div>
      <div className="legend" style={{ padding: '10px', background: '#fff', borderTop: '1px solid #ccc' }}>
          <div style={{ display: 'flex', gap: '20px' }}>
            <div><span style={{color: 'green'}}>●</span> &gt;80% Mastery</div>
            <div><span style={{color: 'yellow'}}>●</span> 50-80% Mastery</div>
            <div><span style={{color: 'orange'}}>●</span> 20-50% Mastery</div>
            <div><span style={{color: 'gray'}}>●</span> &lt;20% Mastery</div>
          </div>
      </div>
    </div>
  );
};

export default KnowledgeGraphPanel;
