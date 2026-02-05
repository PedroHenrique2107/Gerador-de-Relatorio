import { useState, useEffect, useRef } from 'react';
import api from '../services/api';

export function useJobPolling(jobId) {
  const [job, setJob] = useState(null);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);
  
  useEffect(() => {
    if (!jobId) {
      setJob(null);
      return;
    }
    
    const fetchJobStatus = async () => {
      try {
        const response = await api.get(`/api/reports/jobs/${jobId}`);
        setJob(response.data);
        
        // Se job completou ou falhou, para o polling
        if (response.data.status !== 'processing') {
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
          }
        }
      } catch (err) {
        setError(err.message);
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      }
    };
    
    // Primeira chamada imediata
    fetchJobStatus();
    
    // Polling a cada 2 segundos
    intervalRef.current = setInterval(fetchJobStatus, 2000);
    
    // Cleanup
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [jobId]);
  
  return { job, error };
}
