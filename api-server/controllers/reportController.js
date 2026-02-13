// Controller responsavél por iniciar geraÃ§Ã£o de relatÃ³rios,
// consultar status de jobs e retornar histÃ³rico.
// NÃƒO gera arquivos diretamente â€” apenas gerencia requisiÃ§Ãµes HTTP.

const jobManager = require('../services/jobManager');      // ServiÃ§o que cria e controla jobs de relatÃ³rio
const historyManager = require('../services/historyManager'); // ServiÃ§o que retorna histÃ³rico de relatÃ³rios
const logger = require('../utils/logger');                 // Logger centralizado da aplicaÃ§Ã£o

/**
 * POST /reports
 * Cria um novo job de geraÃ§Ã£o de relatÃ³rio.
 * Retorna imediatamente o jobId para acompanhamento assÃ­ncrono.
 */
exports.generateReport = async (req, res) => {
  try {
    const { formato, syncBeforeRun = false } = req.body;

    // Normaliza xlsx para xls (sistema trata ambos como o mesmo tipo)
    const formatoNormalizado = formato === 'xlsx' ? 'xls' : formato;

    // ValidaÃ§Ã£o de formato permitido
    if (!formatoNormalizado || !['csv', 'xls', 'txt'].includes(formatoNormalizado)) {
      return res.status(400).json({
        error: 'Formato invalido. Use: csv, xls/xlsx ou txt'
      });
    }

    // Cria job assÃ­ncrono de geraÃ§Ã£o
    const job = jobManager.createJob(formatoNormalizado, { syncBeforeRun });

    // Log para auditoria e debug futuro
    logger.info(`Relatorio solicitado: ${job.jobId} - Formato: ${formatoNormalizado}`);

    // Retorna dados mÃ­nimos para o cliente acompanhar o processamento
    res.json({
      jobId: job.jobId,
      status: job.status,
      message: 'Relatorio sendo gerado...',
      createdAt: job.timing.startTime
    });

  } catch (error) {
    // Erro inesperado na criaÃ§Ã£o do job
    logger.error(`Erro ao gerar relatorio: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
};

/**
 * GET /reports/jobs/:jobId
 * Retorna o status completo de um job especÃ­fico.
 * Usado pelo frontend para acompanhar progresso.
 */
exports.getJobStatus = (req, res) => {
  try {
    const { jobId } = req.params;

    // Busca job pelo ID
    const job = jobManager.getJob(jobId);

    // Se nÃ£o existir, retorna 404
    if (!job) {
      return res.status(404).json({ error: 'Job nao encontrado' });
    }

    // Retorna objeto completo do job
    res.json(job);

  } catch (error) {
    logger.error(`Erro ao buscar status do job: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
};

/**
 * GET /reports/history
 * Retorna histÃ³rico de relatÃ³rios jÃ¡ processados.
 * Normalmente usado para exibir Ãºltimos relatÃ³rios gerados.
 */
exports.getHistory = async (req, res) => {
  try {
    const history = await historyManager.getHistory();

    // Retorna lista de relatÃ³rios anteriores
    res.json(history);

  } catch (error) {
    logger.error(`Erro ao buscar historico: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
};
