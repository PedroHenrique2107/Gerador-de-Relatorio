import React from 'react';
import './GenerateButton.css';

function GenerateButton({ onClick, disabled, isGenerating }) {
  return (
    <button
      type="button"
      className="generate-button"
      onClick={onClick}
      disabled={disabled}
      data-testid="generate-button"
    >
      {isGenerating ? (
        <>
          <svg className="spinner" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
          </svg>
          Processando...
        </>
      ) : (
        <>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          Gerar Relatório Padrão
        </>
      )}
    </button>
  );
}

export default GenerateButton;
