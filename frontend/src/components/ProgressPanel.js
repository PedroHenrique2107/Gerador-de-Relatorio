import React from 'react';
import './ProgressPanel.css';

function ProgressPanel({ job }) {
  if (!job) return null;
  
  const { currentStep, progress, timing } = job;
  
  const formatElapsedTime = (seconds) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };
  
  const elapsedSeconds = Math.floor(
    (new Date() - new Date(timing.startTime)) / 1000
  );
  
  return (
    <div className="progress-panel" data-testid="progress-panel">
      <div className="progress-header">
        <span className="progress-step" data-testid="progress-step">
          Etapa {currentStep.number}/{currentStep.total}
        </span>
        <span className="progress-time" data-testid="progress-time">
          {formatElapsedTime(elapsedSeconds)}
        </span>
      </div>
      
      <div className="progress-description" data-testid="progress-description">
        {currentStep.description}
      </div>
      
      <div className="progress-bar-container">
        <div 
          className="progress-bar-fill" 
          style={{ width: `${progress.percentage}%` }}
          data-testid="progress-bar"
        />
      </div>
      
      <div className="progress-details">
        <span data-testid="progress-percentage">{progress.percentage}%</span>
        <span data-testid="progress-records">
          {progress.recordsProcessed.toLocaleString()} / {progress.totalRecords.toLocaleString()} registros
        </span>
      </div>
    </div>
  );
}

export default ProgressPanel;
