const express = require('express');
const router = express.Router();
const reportController = require('../controllers/reportController');

// POST /api/reports/generate - Gera novo relatório
router.post('/generate', reportController.generateReport);

// GET /api/reports/jobs/:jobId - Status de um job
router.get('/jobs/:jobId', reportController.getJobStatus);

// GET /api/reports/history - Histórico de relatórios
router.get('/history', reportController.getHistory);

module.exports = router;
