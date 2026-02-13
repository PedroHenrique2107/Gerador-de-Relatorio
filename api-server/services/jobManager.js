// JobManager: gerencia jobs de geraÃ§Ã£o de relatÃ³rio (assÃ­ncrono).
// - Cria jobs e guarda em memÃ³ria (Map)
// - Executa etapas sequenciais (sync Sienge + scripts Python)
// - Atualiza progresso/tempo/status
// - Salva histÃ³rico ao concluir
// - Remove jobs antigos (TTL) periodicamente
//
// IMPORTANTE: como os jobs ficam em memÃ³ria, se o servidor reiniciar os jobs sÃ£o perdidos.

const { v4: uuidv4 } = require('uuid');
const EventEmitter = require('events');
const pythonRunner = require('./pythonRunner');          // Executa scripts Python (inserÃ§Ã£o/query/geraÃ§Ã£o do arquivo)
const historyManager = require('./historyManager');      // Persiste histÃ³rico de jobs concluÃ­dos
const logger = require('../utils/logger');               // Logger central
const siengeSyncService = require('./siengeSyncService'); // Sincroniza dados do Sienge (opcional antes do job)

class JobManager extends EventEmitter {
  constructor() {
    super();
    this.jobs = new Map(); // jobId -> job
    this.TTL_HOURS = 1;    // Jobs expiram apÃ³s 1 hora

    // Limpa jobs antigos a cada 10 minutos (evita memÃ³ria crescer indefinidamente)
    setInterval(() => this.cleanupOldJobs(), 10 * 60 * 1000);
  }

  /**
   * Cria um novo job de geraÃ§Ã£o de relatÃ³rio.
   * Retorna o objeto do job imediatamente e dispara o processamento em background.
   */
  createJob(formato, options = {}) {
    const jobId = uuidv4();

    // Estrutura do job (estado completo que o frontend pode consultar via status)
    const job = {
      jobId,
      formato,

      // Flag que indica se deve sincronizar o Sienge antes de rodar o restante
      // OBS: hÃ¡ duplicidade aqui (mesma chave declarada duas vezes). A Ãºltima linha vence.
      // Mantido como estÃ¡ para nÃ£o alterar comportamento, mas isso deveria ser corrigido.
      syncBeforeRun: Boolean(options.syncBeforeRun),
      syncBeforeRun: options.syncBeforeRun || false,

      status: 'processing', // processing | completed | failed
      currentStep: { number: 1, total: 5, description: 'Inicializando...' },

      // Progresso Ã© â€œestimadoâ€ e atualizado manualmente em cada etapa
      progress: { percentage: 0, recordsProcessed: 0, totalRecords: 19000 },

      // Controle de tempo (usado para mostrar duraÃ§Ã£o ao usuÃ¡rio e histÃ³rico)
      timing: {
        startTime: new Date().toISOString(),
        endTime: null,
        elapsedSeconds: 0
      },

      // Metadados do arquivo final gerado (preenchido na etapa de geraÃ§Ã£o)
      result: {
        downloadUrl: null,
        fileName: null,
        fileSize: null,
        recordCount: null
      },

      error: null,          // Mensagem de erro quando status = failed
      createdAt: new Date() // Usado para expiraÃ§Ã£o (TTL)
    };

    // Armazena em memÃ³ria para consulta posterior
    this.jobs.set(jobId, job);
    logger.info(`Job criado: ${jobId} - Formato: ${formato}`);

    // Inicia processamento assÃ­ncrono (nÃ£o bloqueia a resposta HTTP)
    this.processJob(jobId);

    return job;
  }

  /**
   * Executa o job em etapas sequenciais.
   * Etapas:
   * 0) (opcional) Sync Sienge
   * 1) InserÃ§Ã£o no banco via Python (lÃª JSON e popula tabela)
   * 2) Query consolidada via Python
   * 3) GeraÃ§Ã£o do arquivo de relatÃ³rio (csv/xls/txt) via Python
   * 4) FinalizaÃ§Ã£o (100%)
   */
  async processJob(jobId) {
    const job = this.jobs.get(jobId);
    if (!job) return;

    try {
      // Etapa 0 (opcional): sincroniza dados externos antes do processamento local
      if (job.syncBeforeRun) {
        await this.runStep(jobId, 0, 'Sincronizando dados do Sienge...', async () => {
          await siengeSyncService.syncAll();
          job.progress.percentage = 10;
        });
      }

      // Etapa 1: popular banco com dados base
      await this.runStep(jobId, 1, 'Lendo JSON e inserindo no banco...', async () => {
        await pythonRunner.runBackendInsert();
        job.progress.percentage = 25;
      });

      // Etapa 2: executar query consolidada (normalmente gera tabela/visÃ£o final para exportaÃ§Ã£o)
      await this.runStep(jobId, 2, 'Processando query consolidada...', async () => {
        await pythonRunner.runQuery();
        job.progress.percentage = 50;
      });

      // Etapa 3: gerar o arquivo final para download
      await this.runStep(jobId, 3, 'Gerando arquivo de relatório...', async () => {
        const result = await pythonRunner.runReportGeneration(job.formato);

        // Copia metadados retornados pelo Python para o job (usado na UI e histórico)
        job.result.fileName = result.fileName;
        job.result.fileSize = result.fileSize;
        job.result.recordCount = result.recordCount;

        // URL esperada pelo endpoint /downloads/:filename
        job.result.downloadUrl = `/downloads/${result.fileName}`;
        job.progress.percentage = 75;
      });

      // Etapa 4: finalizaÃ§Ã£o
      await this.runStep(jobId, 4, 'Finalizando...', async () => {
        job.progress.percentage = 100;
      });

      // Marca como concluÃ­do e calcula tempo total
      job.status = 'completed';
      job.timing.endTime = new Date().toISOString();
      job.timing.elapsedSeconds = Math.floor(
        (new Date(job.timing.endTime) - new Date(job.timing.startTime)) / 1000
      );

      // Salva no histÃ³rico (persistÃªncia fora da memÃ³ria)
      await historyManager.addToHistory(job);
      logger.info(`Job concluÃ­do: ${jobId} em ${job.timing.elapsedSeconds}s`);
    } catch (error) {
      // Qualquer falha em qualquer etapa derruba o job inteiro
      job.status = 'failed';
      job.error = error.message;
      job.timing.endTime = new Date().toISOString();
      logger.error(`Job falhou: ${jobId} - ${error.message}`);
    }
  }

  /**
   * Executa uma etapa do job (wrapper padrÃ£o).
   * Atualiza "currentStep" para o frontend e gera log da etapa.
   */
  async runStep(jobId, stepNumber, description, asyncFn) {
    const job = this.jobs.get(jobId);
    if (!job) return;

    // Total de etapas muda se syncBeforeRun estiver ligado
    job.currentStep = {
      number: stepNumber,
      total: job.syncBeforeRun ? 5 : 4,
      description
    };

    const totalSteps = job.syncBeforeRun ? 5 : 4;
    logger.info(`[${jobId}] Etapa ${stepNumber}/${totalSteps}: ${description}`);

    // Executa a funÃ§Ã£o da etapa (pode lanÃ§ar erro)
    await asyncFn();
  }

  /**
   * Retorna o job pelo ID (usado pelo controller para status).
   */
  getJob(jobId) {
    return this.jobs.get(jobId) || null;
  }

  /**
   * Remove jobs antigos da memÃ³ria.
   * Evita vazamento de memÃ³ria se muitos jobs forem criados.
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

// Exporta singleton (um Ãºnico gerenciador para a aplicaÃ§Ã£o toda)
module.exports = new JobManager();
