import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

export function useHistory() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const fetchHistory = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/reports/history');
      setHistory(response.data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);
  
  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);
  
  const refreshHistory = useCallback(() => {
    fetchHistory();
  }, [fetchHistory]);
  
  return { history, loading, error, refreshHistory };
}
