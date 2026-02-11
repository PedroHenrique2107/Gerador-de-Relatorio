<<<<<<< HEAD
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
=======
// Controller responsável por iniciar geração de relatórios,
// consultar status de jobs e retornar histórico.
// NÃO gera arquivos diretamente — apenas gerencia requisições HTTP.

const jobManager = require('../services/jobManager');      // Serviço que cria e controla jobs de relatório
const historyManager = require('../services/historyManager'); // Serviço que retorna histórico de relatórios
const logger = require('../utils/logger');                 // Logger centralizado da aplicação

/**
 * POST /reports
 * Cria um novo job de geração de relatório.
 * Retorna imediatamente o jobId para acompanhamento assíncrono.
 */
exports.generateReport = async (req, res) => {
  try {
    const { formato, syncBeforeRun = false } = req.body;

    // Normaliza xlsx para xls (sistema trata ambos como o mesmo tipo)
    const formatoNormalizado = formato === 'xlsx' ? 'xls' : formato;

    // Validação de formato permitido
    if (!formatoNormalizado || !['csv', 'xls', 'txt'].includes(formatoNormalizado)) {
      return res.status(400).json({
        error: 'Formato invalido. Use: csv, xls/xlsx ou txt'
      });
    }

    // Cria job assíncrono de geração
    const job = jobManager.createJob(formatoNormalizado, { syncBeforeRun });

    // Log para auditoria e debug futuro
    logger.info(`Relatorio solicitado: ${job.jobId} - Formato: ${formatoNormalizado}`);

    // Retorna dados mínimos para o cliente acompanhar o processamento
    res.json({
      jobId: job.jobId,
      status: job.status,
      message: 'Relatorio sendo gerado...',
      createdAt: job.timing.startTime
    });

  } catch (error) {
    // Erro inesperado na criação do job
    logger.error(`Erro ao gerar relatorio: ${error.message}`);
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
    res.status(500).json({ error: error.message });
  }
};

/**
<<<<<<< HEAD
 * GET /api/reports/jobs/:jobId
 * Retorna status de um job
=======
 * GET /reports/jobs/:jobId
 * Retorna o status completo de um job específico.
 * Usado pelo frontend para acompanhar progresso.
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
 */
exports.getJobStatus = (req, res) => {
  try {
    const { jobId } = req.params;
<<<<<<< HEAD
    
    const job = jobManager.getJob(jobId);
    
    if (!job) {
      return res.status(404).json({ error: 'Job não encontrado' });
    }
    
    res.json(job);
    
=======

    // Busca job pelo ID
    const job = jobManager.getJob(jobId);

    // Se não existir, retorna 404
    if (!job) {
      return res.status(404).json({ error: 'Job nao encontrado' });
    }

    // Retorna objeto completo do job
    res.json(job);

>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
  } catch (error) {
    logger.error(`Erro ao buscar status do job: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
};

/**
<<<<<<< HEAD
 * GET /api/reports/history
 * Retorna histórico de relatórios
=======
 * GET /reports/history
 * Retorna histórico de relatórios já processados.
 * Normalmente usado para exibir últimos relatórios gerados.
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
 */
exports.getHistory = async (req, res) => {
  try {
    const history = await historyManager.getHistory();
<<<<<<< HEAD
    res.json(history);
    
  } catch (error) {
    logger.error(`Erro ao buscar histórico: ${error.message}`);
=======

    // Retorna lista de relatórios anteriores
    res.json(history);

  } catch (error) {
    logger.error(`Erro ao buscar historico: ${error.message}`);
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
    res.status(500).json({ error: error.message });
  }
};
