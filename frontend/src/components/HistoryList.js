import React from 'react';
import './HistoryList.css';
<<<<<<< HEAD
=======
import { BACKEND_BASE_URL } from '../services/api';
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)

function HistoryList({ history }) {
  if (!history || history.length === 0) {
    return (
      <div className="history-empty" data-testid="history-empty">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
        </svg>
        <p>Nenhum relatório gerado ainda</p>
        <span>Gere seu primeiro relatório usando o formulário acima</span>
      </div>
    );
  }
  
  return (
    <div className="history-list" data-testid="history-list">
      {history.map((item, index) => (
        <HistoryItem key={item.jobId || index} item={item} />
      ))}
    </div>
  );
}

function HistoryItem({ item }) {
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  const getFormatBadge = (formato) => {
    const badges = {
      csv: { label: 'CSV', color: '#48bb78' },
      xls: { label: 'Excel', color: '#4299e1' },
      txt: { label: 'TXT', color: '#9f7aea' }
    };
    return badges[formato] || { label: formato.toUpperCase(), color: '#718096' };
  };
  
  const badge = getFormatBadge(item.formato);
  
  return (
    <div className="history-item" data-testid="history-item">
      <div className="history-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
        </svg>
      </div>
      
      <div className="history-content">
        <div className="history-header">
          <div className="history-title">
            <span className="history-date" data-testid="history-date">{formatDate(item.createdAt)}</span>
            <span 
              className="format-badge" 
              style={{ background: badge.color }}
              data-testid="format-badge"
            >
              {badge.label}
            </span>
          </div>
          <div className="history-meta">
            <span data-testid="record-count">{item.recordCount?.toLocaleString()} registros</span>
            <span>•</span>
            <span data-testid="file-size">{item.fileSize}</span>
            <span>•</span>
            <span data-testid="processing-time">{item.processingTime}</span>
          </div>
        </div>
        
        <div className="history-actions">
          {item.status === 'completed' ? (
            <>
              <span className="status-badge status-completed" data-testid="status-completed">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                Concluído
              </span>
              <a 
<<<<<<< HEAD
                href={`${process.env.REACT_APP_BACKEND_URL || 'http://localhost:3001'}${item.downloadUrl}`}
=======
                href={`${BACKEND_BASE_URL}${item.downloadUrl}`}
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
                className="download-link"
                download
                data-testid="download-link"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7 10 12 15 17 10"></polyline>
                  <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                Baixar
              </a>
            </>
          ) : (
            <span className="status-badge status-failed" data-testid="status-failed">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
              </svg>
              Falhou
            </span>
          )}
        </div>
        
        {item.error && (
          <div className="history-error" data-testid="history-error">
            Erro: {item.error}
          </div>
        )}
      </div>
    </div>
  );
}

export default HistoryList;
