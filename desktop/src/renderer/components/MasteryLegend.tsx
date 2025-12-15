import React from 'react';
import './MasteryLegend.css';

interface MasteryLegendProps {
  masteryFilter: string | null;
  setMasteryFilter: (filter: string | null) => void;
}

export const MasteryLegend: React.FC<MasteryLegendProps> = ({
  masteryFilter,
  setMasteryFilter,
}) => {
  const masteryLevels = [
    { key: 'green', color: '#10b981', label: 'Mastered (>80%)', range: '> 80%' },
    { key: 'yellow', color: '#fbbf24', label: 'Learning (50-80%)', range: '50-80%' },
    { key: 'orange', color: '#f97316', label: 'Beginner (20-50%)', range: '20-50%' },
    { key: 'gray', color: '#6b7280', label: 'Not Started (<20%)', range: '< 20%' },
  ];
  
  return (
    <div className="mastery-legend">
      <h4>Mastery Level</h4>
      <div className="legend-items">
        {masteryLevels.map(({ key, color, label, range }) => (
          <div
            key={key}
            className={`legend-item ${masteryFilter === key ? 'active' : ''}`}
            onClick={() => setMasteryFilter(masteryFilter === key ? null : key)}
          >
            <div
              className="legend-color"
              style={{ backgroundColor: color }}
            />
            <div className="legend-label">
              <span className="legend-name">{label}</span>
              <span className="legend-range">{range}</span>
            </div>
          </div>
        ))}
      </div>
      {masteryFilter && (
        <button
          className="clear-filter-btn"
          onClick={() => setMasteryFilter(null)}
        >
          Clear Filter
        </button>
      )}
    </div>
  );
};
