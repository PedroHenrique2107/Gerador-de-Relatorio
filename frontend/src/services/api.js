import axios from 'axios';

const runtimeBackendUrl = `${window.location.protocol}//${window.location.hostname}:3001`;
const envBackendUrl = process.env.REACT_APP_BACKEND_URL;
const isAccessingFromLocalhost = ['localhost', '127.0.0.1'].includes(window.location.hostname);
const envPointsToLocalhost = /\/\/(localhost|127\.0\.0\.1)(:\d+)?/i.test(envBackendUrl || '');

// Se o app foi aberto via IP da rede, evita usar backend fixo em localhost.
export const BACKEND_BASE_URL = (envBackendUrl && !(envPointsToLocalhost && !isAccessingFromLocalhost))
  ? envBackendUrl
  : runtimeBackendUrl;

const api = axios.create({
  baseURL: BACKEND_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor de requisiÃ§Ã£o
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
      // RequisiÃ§Ã£o foi feita mas sem resposta
      return Promise.reject(new Error('Sem resposta do servidor'));
    } else {
      // Erro na configuraÃ§Ã£o da requisiÃ§Ã£o
      return Promise.reject(error);
    }
  }
);

export default api;
