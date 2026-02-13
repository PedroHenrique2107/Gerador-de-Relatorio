import React, { useState, useEffect } from 'react';
import FormatSelector from './FormatSelector';
import GenerateButton from './GenerateButton';
import ProgressPanel from './ProgressPanel';
import HistoryList from './HistoryList';
import { useJobPolling } from '../hooks/useJobPolling';
import { useHistory } from '../hooks/useHistory';
import api from '../services/api';
import './Dashboard.css';

function Dashboard() {
  const [formato, setFormato] = useState('csv');
  const [syncBeforeRun, setSyncBeforeRun] = useState(false);
  const [currentJobId, setCurrentJobId] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);
  
  const { job, error: jobError } = useJobPolling(currentJobId);
  const { history, refreshHistory } = useHistory();
  
  const handleGenerate = async () => {
    try {
      setError(null);
      setIsGenerating(true);
      
      const response = await api.post('/api/reports/generate', {
        formato,
        syncBeforeRun,
      });
      setCurrentJobId(response.data.jobId);
      
    } catch (error) {
      setError(`Erro ao iniciar geração: ${error.message}`);
      setIsGenerating(false);
    }
  };
  
  // Quando job completa, atualiza histórico e reseta
  useEffect(() => {
    if (job && job.status === 'completed') {
      setIsGenerating(false);
      setCurrentJobId(null);
      refreshHistory();
    } else if (job && job.status === 'failed') {
      setIsGenerating(false);
      setError(job.error);
      setCurrentJobId(null);
    }
  }, [job, refreshHistory]);
  
  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
          </div>
          <div>
            <h1>Sistema de Relatórios Sienge</h1>
            <p>Geração automatizada de relatórios financeiros</p>
          </div>
        </div>
      </header>
      
      <main className="dashboard-content">
        <section className="control-panel">
          <div className="panel-card">
            <h2>Novo Relatório</h2>
            
            <FormatSelector 
              value={formato} 
              onChange={setFormato}
              disabled={isGenerating}
            />

            <label className="sync-option">
              <input
                type="checkbox"
                checked={syncBeforeRun}
                onChange={(e) => setSyncBeforeRun(e.target.checked)}
                disabled={isGenerating}
              />
              <span>Sincronizar dados do Sienge</span>
            </label>
            
            <GenerateButton 
              onClick={handleGenerate}
              disabled={isGenerating}
              isGenerating={isGenerating}
            />
            
            {error && (
              <div className="error-message" data-testid="error-message">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="8" x2="12" y2="12"></line>
                  <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                {error}
              </div>
            )}
            
            {isGenerating && job && (
              <ProgressPanel job={job} />
            )}
          </div>
        </section>
        
        <section className="history-section">
          <div className="section-header">
            <h2>Histórico de Relatórios</h2>
            <span className="records-count">Últimos 10 relatórios</span>
          </div>
          <HistoryList history={history} />
        </section>
      </main>
    </div>
  );
}

export default Dashboard;
