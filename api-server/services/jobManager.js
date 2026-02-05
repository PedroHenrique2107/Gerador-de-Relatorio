const { v4: uuidv4 } = require('uuid');
const EventEmitter = require('events');
const pythonRunner = require('./pythonRunner');
const historyManager = require('./historyManager');
const logger = require('../utils/logger');

class JobManager extends EventEmitter {
  constructor() {
    super();
    this.jobs = new Map();
    this.TTL_HOURS = 1;
    
    // Limpa jobs antigos a cada 10 minutos
    setInterval(() => this.cleanupOldJobs(), 10 * 60 * 1000);
  }
  
  /**
   * Cria um novo job de geração de relatório
   */
  createJob(formato) {
    const jobId = uuidv4();
    const job = {
      jobId,
      formato,
      status: 'processing',
      currentStep: { number: 1, total: 4, description: 'Inicializando...' },
      progress: { percentage: 0, recordsProcessed: 0, totalRecords: 19000 },
      timing: {
        startTime: new Date().toISOString(),
        endTime: null,
        elapsedSeconds: 0
      },
      result: {
        downloadUrl: null,
        fileName: null,
        fileSize: null,
        recordCount: null
      },
      error: null,
      createdAt: new Date()
    };
    
    this.jobs.set(jobId, job);
    logger.info(`Job criado: ${jobId} - Formato: ${formato}`);
    
    // Inicia processamento assíncrono
    this.processJob(jobId);
    
    return job;
  }
  
  /**
   * Processa job executando 4 etapas sequenciais
   */
  async processJob(jobId) {
    const job = this.jobs.get(jobId);
    if (!job) return;
    
    try {
      // ETAPA 1: Inserir dados do JSON no banco (backend/scripts/main.py)
      await this.runStep(jobId, 1, 'Lendo JSON e inserindo no banco...', async () => {
        await pythonRunner.runBackendInsert();
        job.progress.percentage = 25;
      });
      
      // ETAPA 2: Executar query consolidada (query/execute_query.py)
      await this.runStep(jobId, 2, 'Processando query consolidada...', async () => {
        await pythonRunner.runQuery();
        job.progress.percentage = 50;
      });
      
      // ETAPA 3: Gerar arquivo de relatório (relatorio/generate_report.py)
      await this.runStep(jobId, 3, 'Gerando arquivo de relatório...', async () => {
        const result = await pythonRunner.runReportGeneration(job.formato);
        job.result.fileName = result.fileName;
        job.result.fileSize = result.fileSize;
        job.result.recordCount = result.recordCount;
        job.result.downloadUrl = `/downloads/${result.fileName}`;
        job.progress.percentage = 75;
      });
      
      // ETAPA 4: Finalização
      await this.runStep(jobId, 4, 'Finalizando...', async () => {
        job.progress.percentage = 100;
      });
      
      // Job completo
      job.status = 'completed';
      job.timing.endTime = new Date().toISOString();
      job.timing.elapsedSeconds = Math.floor(
        (new Date(job.timing.endTime) - new Date(job.timing.startTime)) / 1000
      );
      
      // Salvar no histórico
      await historyManager.addToHistory(job);
      
      logger.info(`Job concluído: ${jobId} em ${job.timing.elapsedSeconds}s`);
      
    } catch (error) {
      job.status = 'failed';
      job.error = error.message;
      job.timing.endTime = new Date().toISOString();
      
      logger.error(`Job falhou: ${jobId} - ${error.message}`);
    }
  }
  
  /**
   * Executa uma etapa do job
   */
  async runStep(jobId, stepNumber, description, asyncFn) {
    const job = this.jobs.get(jobId);
    if (!job) return;
    
    job.currentStep = {
      number: stepNumber,
      total: 4,
      description
    };
    
    logger.info(`[${jobId}] Etapa ${stepNumber}/4: ${description}`);
    
    await asyncFn();
  }
  
  /**
   * Retorna status de um job
   */
  getJob(jobId) {
    return this.jobs.get(jobId) || null;
  }
  
  /**
   * Remove jobs mais antigos que TTL
   */
  cleanupOldJobs() {
    const now = new Date();
    const ttlMs = this.TTL_HOURS * 60 * 60 * 1000;
    
    for (const [jobId, job] of this.jobs.entries()) {
      if (now - job.createdAt > ttlMs) {
        this.jobs.delete(jobId);
        logger.info(`Job removido (TTL): ${jobId}`);
      }
    }
  }
}

module.exports = new JobManager();
