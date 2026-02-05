const jobManager = require('../services/jobManager');
const historyManager = require('../services/historyManager');
const logger = require('../utils/logger');

/**
 * POST /api/reports/generate
 * Cria novo job de geração de relatório
 */
exports.generateReport = async (req, res) => {
  try {
    const { formato } = req.body;
    
    // Validar formato
    if (!formato || !['csv', 'xls', 'txt'].includes(formato)) {
      return res.status(400).json({ 
        error: 'Formato inválido. Use: csv, xls ou txt' 
      });
    }
    
    // Criar job
    const job = jobManager.createJob(formato);
    
    logger.info(`Relatório solicitado: ${job.jobId} - Formato: ${formato}`);
    
    res.json({
      jobId: job.jobId,
      status: job.status,
      message: 'Relatório sendo gerado...',
      createdAt: job.timing.startTime
    });
    
  } catch (error) {
    logger.error(`Erro ao gerar relatório: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
};

/**
 * GET /api/reports/jobs/:jobId
 * Retorna status de um job
 */
exports.getJobStatus = (req, res) => {
  try {
    const { jobId } = req.params;
    
    const job = jobManager.getJob(jobId);
    
    if (!job) {
      return res.status(404).json({ error: 'Job não encontrado' });
    }
    
    res.json(job);
    
  } catch (error) {
    logger.error(`Erro ao buscar status do job: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
};

/**
 * GET /api/reports/history
 * Retorna histórico de relatórios
 */
exports.getHistory = async (req, res) => {
  try {
    const history = await historyManager.getHistory();
    res.json(history);
    
  } catch (error) {
    logger.error(`Erro ao buscar histórico: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
};
