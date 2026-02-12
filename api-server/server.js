/**
 * ============================================================
 * ARQUIVO PRINCIPAL DO SERVIDOR API
 * ============================================================
 * 
 * Responsável por:
 * - Inicializar o servidor Express
 * - Configurar middlewares de segurança
 * - Registrar rotas da aplicação
 * - Criar health check
 * - Tratar erros globais
 * - Subir a API na porta definida
 * 
 * Esse é o ponto de entrada da aplicação backend.
 * ============================================================
 */

// Importa o framework principal da API
const express = require('express');

// Middleware para permitir requisições de outros domínios (CORS)
const cors = require('cors');

// Middleware de segurança HTTP (headers seguros)
const helmet = require('helmet');

// Carrega variáveis de ambiente do arquivo .env
require('dotenv').config();

// Importa utilitário de logs do sistema
const logger = require('./utils/logger');

// Importa arquivos de rotas da aplicação
const reportsRouter = require('./routes/reports');
const downloadsRouter = require('./routes/downloads');
const siengeRouter = require('./routes/sienge');

// Cria instância do servidor Express
const app = express();

// Define a porta do servidor:
// - Usa a do .env se existir
// - Senão usa 3001
const PORT = process.env.PORT || 3001;

// Adiciona proteção de headers HTTP
app.use(helmet());

// Habilita CORS (permite frontend acessar API)
app.use(cors());

// Permite receber JSON no body das requisições
app.use(express.json());

// Registra todas as chamadas feitas na API
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.path}`);
  next();
});

// Rotas de relatórios
app.use('/api/reports', reportsRouter);

// Rotas de integração com Sienge
app.use('/api/sienge', siengeRouter);

// Rotas de download de arquivos
app.use('/downloads', downloadsRouter);

// Endpoint para verificar se a API está online
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
  });
});

// Tratamento global de erros
app.use((err, req, res, next) => {
  logger.error(`Error: ${err.message}`);
  res.status(500).json({
    error: err.message,
  });
});

// Sobe a API na porta definida
app.listen(PORT, '0.0.0.0', () => {
  logger.info(`API Server rodando na porta ${PORT}`);
  logger.info(`Environment: ${process.env.NODE_ENV}`);
});
