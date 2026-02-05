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
  logger.info(`Environment: ${process.env.NODE_ENV}`);
});
