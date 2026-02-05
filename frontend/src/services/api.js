import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_BACKEND_URL || 'http://localhost:3001',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor de requisição
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor de resposta
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Servidor respondeu com erro
      return Promise.reject(new Error(error.response.data.error || 'Erro no servidor'));
    } else if (error.request) {
      // Requisição foi feita mas sem resposta
      return Promise.reject(new Error('Sem resposta do servidor'));
    } else {
      // Erro na configuração da requisição
      return Promise.reject(error);
    }
  }
);

export default api;
