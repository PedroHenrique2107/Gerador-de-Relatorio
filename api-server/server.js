<<<<<<< HEAD
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const path = require('path');
require('dotenv').config();

const logger = require('./utils/logger');
const reportsRouter = require('./routes/reports');
const downloadsRouter = require('./routes/downloads');

const app = express();
const PORT = process.env.PORT || 3001;

// Middlewares
app.use(helmet());
app.use(cors());
app.use(express.json());

// Request logging
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.path}`);
  next();
});

// Routes
app.use('/api/reports', reportsRouter);
app.use('/downloads', downloadsRouter);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Error handler
app.use((err, req, res, next) => {
  logger.error(`Error: ${err.message}`);
  res.status(500).json({ error: err.message });
});

// Start server
app.listen(PORT, () => {
  logger.info(`API Server rodando na porta ${PORT}`);
=======
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



/**
 * ============================================================
 * MIDDLEWARES GLOBAIS
 * ============================================================
 * Middlewares são funções executadas antes das rotas.
 * Servem para segurança, parsing, logs, etc.
 * ============================================================
 */


// Adiciona proteção de headers HTTP
app.use(helmet());


// Habilita CORS (permite frontend acessar API)
app.use(cors());


// Permite receber JSON no body das requisições
app.use(express.json());



/**
 * ============================================================
 * LOG DE REQUISIÇÕES
 * ============================================================
 * Registra todas as chamadas feitas na API.
 * Exemplo de log:
 * GET /api/reports
 * POST /api/sienge/sync
 * ============================================================
 */
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.path}`);
  next(); // Continua para próxima etapa
});



/**
 * ============================================================
 * REGISTRO DAS ROTAS
 * ============================================================
 * Aqui definimos os prefixos das rotas da API.
 * ============================================================
 */


// Rotas de relatórios
// Exemplo final: /api/reports/generate
app.use('/api/reports', reportsRouter);


// Rotas de integração com Sienge
// Exemplo final: /api/sienge/sync
app.use('/api/sienge', siengeRouter);


// Rotas de download de arquivos
// Exemplo final: /downloads/relatorio.pdf
app.use('/downloads', downloadsRouter);




/**
 * ============================================================
 * HEALTH CHECK
 * ============================================================
 * Endpoint para verificar se a API está online.
 * Muito usado por:
 * - Monitoramento
 * - Docker
 * - Kubernetes
 * - Load balancer
 * ============================================================
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
  });
});



/**
 * ============================================================
 * TRATAMENTO GLOBAL DE ERROS
 * ============================================================
 * Captura erros não tratados nas rotas.
 * Evita que a API quebre.
 * ============================================================
 */
app.use((err, req, res, next) => {

  // Registra erro no log
  logger.error(`Error: ${err.message}`);

  // Retorna erro padrão para o cliente
  res.status(500).json({
    error: err.message,
  });
});



/**
 * ============================================================
 * INICIALIZAÇÃO DO SERVIDOR
 * ============================================================
 * Sobe a API na porta definida.
 * ============================================================
 */
app.listen(PORT, '0.0.0.0', () => {

  // Log informando que o servidor iniciou
  logger.info(`API Server rodando na porta ${PORT}`);

  // Log do ambiente atual
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
  logger.info(`Environment: ${process.env.NODE_ENV}`);
});
