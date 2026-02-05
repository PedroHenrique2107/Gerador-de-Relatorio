import React from 'react';
import './FormatSelector.css';

function FormatSelector({ value, onChange, disabled }) {
  const formats = [
    { id: 'csv', label: 'CSV', description: 'Planilha separada por ponto-e-vírgula' },
    { id: 'xls', label: 'Excel', description: 'Arquivo Excel (.xlsx)' },
    { id: 'txt', label: 'TXT', description: 'Texto formatado em colunas' }
  ];
  
  return (
    <div className="format-selector">
      <label className="selector-label">Formato de Exportação</label>
      <div className="format-options" data-testid="format-selector">
        {formats.map(format => (
          <button
            key={format.id}
            type="button"
            className={`format-option ${value === format.id ? 'active' : ''}`}
            onClick={() => onChange(format.id)}
            disabled={disabled}
            data-testid={`format-option-${format.id}`}
          >
            <div className="format-icon">
              {format.id === 'csv' && (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
              )}
              {format.id === 'xls' && (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                </svg>
              )}
              {format.id === 'txt' && (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="12" y1="18" x2="12" y2="12"></line>
                  <line x1="9" y1="15" x2="15" y2="15"></line>
                </svg>
              )}
            </div>
            <div className="format-info">
              <div className="format-label">{format.label}</div>
              <div className="format-description">{format.description}</div>
            </div>
            <div className="format-radio">
              <input
                type="radio"
                name="format"
                checked={value === format.id}
                onChange={() => onChange(format.id)}
                disabled={disabled}
              />
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default FormatSelector;
