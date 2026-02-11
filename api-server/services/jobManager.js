<<<<<<< HEAD
const { v4: uuidv4 } = require('uuid');
const EventEmitter = require('events');
const pythonRunner = require('./pythonRunner');
const historyManager = require('./historyManager');
const logger = require('../utils/logger');
=======
// JobManager: gerencia jobs de geração de relatório (assíncrono).
// - Cria jobs e guarda em memória (Map)
// - Executa etapas sequenciais (sync Sienge + scripts Python)
// - Atualiza progresso/tempo/status
// - Salva histórico ao concluir
// - Remove jobs antigos (TTL) periodicamente
//
// IMPORTANTE: como os jobs ficam em memória, se o servidor reiniciar os jobs são perdidos.

const { v4: uuidv4 } = require('uuid');
const EventEmitter = require('events');
const pythonRunner = require('./pythonRunner');          // Executa scripts Python (inserção/query/geração do arquivo)
const historyManager = require('./historyManager');      // Persiste histórico de jobs concluídos
const logger = require('../utils/logger');               // Logger central
const siengeSyncService = require('./siengeSyncService'); // Sincroniza dados do Sienge (opcional antes do job)
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)

class JobManager extends EventEmitter {
  constructor() {
    super();
<<<<<<< HEAD
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
=======
    this.jobs = new Map(); // jobId -> job
    this.TTL_HOURS = 1;    // Jobs expiram após 1 hora

    // Limpa jobs antigos a cada 10 minutos (evita memória crescer indefinidamente)
    setInterval(() => this.cleanupOldJobs(), 10 * 60 * 1000);
  }

  /**
   * Cria um novo job de geração de relatório.
   * Retorna o objeto do job imediatamente e dispara o processamento em background.
   */
  createJob(formato, options = {}) {
    const jobId = uuidv4();

    // Estrutura do job (estado completo que o frontend pode consultar via status)
    const job = {
      jobId,
      formato,

      // Flag que indica se deve sincronizar o Sienge antes de rodar o restante
      // OBS: há duplicidade aqui (mesma chave declarada duas vezes). A última linha vence.
      // Mantido como está para não alterar comportamento, mas isso deveria ser corrigido.
      syncBeforeRun: Boolean(options.syncBeforeRun),
      syncBeforeRun: options.syncBeforeRun || false,

      status: 'processing', // processing | completed | failed
      currentStep: { number: 1, total: 5, description: 'Inicializando...' },

      // Progresso é “estimado” e atualizado manualmente em cada etapa
      progress: { percentage: 0, recordsProcessed: 0, totalRecords: 19000 },

      // Controle de tempo (usado para mostrar duração ao usuário e histórico)
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
      timing: {
        startTime: new Date().toISOString(),
        endTime: null,
        elapsedSeconds: 0
      },
<<<<<<< HEAD
=======

      // Metadados do arquivo final gerado (preenchido na etapa de geração)
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
      result: {
        downloadUrl: null,
        fileName: null,
        fileSize: null,
        recordCount: null
      },
<<<<<<< HEAD
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
=======

      error: null,          // Mensagem de erro quando status = failed
      createdAt: new Date() // Usado para expiração (TTL)
    };

    // Armazena em memória para consulta posterior
    this.jobs.set(jobId, job);
    logger.info(`Job criado: ${jobId} - Formato: ${formato}`);

    // Inicia processamento assíncrono (não bloqueia a resposta HTTP)
    this.processJob(jobId);

    return job;
  }

  /**
   * Executa o job em etapas sequenciais.
   * Etapas:
   * 0) (opcional) Sync Sienge
   * 1) Inserção no banco via Python (lê JSON e popula tabela)
   * 2) Query consolidada via Python
   * 3) Geração do arquivo de relatório (csv/xls/txt) via Python
   * 4) Finalização (100%)
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
   */
  async processJob(jobId) {
    const job = this.jobs.get(jobId);
    if (!job) return;
<<<<<<< HEAD
    
    try {
      // ETAPA 1: Inserir dados do JSON no banco (backend/scripts/main.py)
=======

    try {
      // Etapa 0 (opcional): sincroniza dados externos antes do processamento local
      if (job.syncBeforeRun) {
        await this.runStep(jobId, 0, 'Sincronizando dados do Sienge...', async () => {
          await siengeSyncService.syncAll();
          job.progress.percentage = 10;
        });
      }

      // Etapa 1: popular banco com dados base
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
      await this.runStep(jobId, 1, 'Lendo JSON e inserindo no banco...', async () => {
        await pythonRunner.runBackendInsert();
        job.progress.percentage = 25;
      });
<<<<<<< HEAD
      
      // ETAPA 2: Executar query consolidada (query/execute_query.py)
=======

      // Etapa 2: executar query consolidada (normalmente gera tabela/visão final para exportação)
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
      await this.runStep(jobId, 2, 'Processando query consolidada...', async () => {
        await pythonRunner.runQuery();
        job.progress.percentage = 50;
      });
<<<<<<< HEAD
      
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
=======

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

      // Etapa 4: finalização
      await this.runStep(jobId, 4, 'Finalizando...', async () => {
        job.progress.percentage = 100;
      });

      // Marca como concluído e calcula tempo total
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
      job.status = 'completed';
      job.timing.endTime = new Date().toISOString();
      job.timing.elapsedSeconds = Math.floor(
        (new Date(job.timing.endTime) - new Date(job.timing.startTime)) / 1000
      );
<<<<<<< HEAD
      
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
=======

      // Salva no histórico (persistência fora da memória)
      await historyManager.addToHistory(job);
      logger.info(`Job concluído: ${jobId} em ${job.timing.elapsedSeconds}s`);
    } catch (error) {
      // Qualquer falha em qualquer etapa derruba o job inteiro
      job.status = 'failed';
      job.error = error.message;
      job.timing.endTime = new Date().toISOString();
      logger.error(`Job falhou: ${jobId} - ${error.message}`);
    }
  }

  /**
   * Executa uma etapa do job (wrapper padrão).
   * Atualiza "currentStep" para o frontend e gera log da etapa.
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
   */
  async runStep(jobId, stepNumber, description, asyncFn) {
    const job = this.jobs.get(jobId);
    if (!job) return;
<<<<<<< HEAD
    
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
=======

    // Total de etapas muda se syncBeforeRun estiver ligado
    job.currentStep = {
      number: stepNumber,
      total: job.syncBeforeRun ? 5 : 4,
      description
    };

    const totalSteps = job.syncBeforeRun ? 5 : 4;
    logger.info(`[${jobId}] Etapa ${stepNumber}/${totalSteps}: ${description}`);

    // Executa a função da etapa (pode lançar erro)
    await asyncFn();
  }

  /**
   * Retorna o job pelo ID (usado pelo controller para status).
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
   */
  getJob(jobId) {
    return this.jobs.get(jobId) || null;
  }
<<<<<<< HEAD
  
  /**
   * Remove jobs mais antigos que TTL
=======

  /**
   * Remove jobs antigos da memória.
   * Evita vazamento de memória se muitos jobs forem criados.
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
   */
  cleanupOldJobs() {
    const now = new Date();
    const ttlMs = this.TTL_HOURS * 60 * 60 * 1000;
<<<<<<< HEAD
    
=======

>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
    for (const [jobId, job] of this.jobs.entries()) {
      if (now - job.createdAt > ttlMs) {
        this.jobs.delete(jobId);
        logger.info(`Job removido (TTL): ${jobId}`);
      }
    }
  }
}

<<<<<<< HEAD
module.exports = new JobManager();
=======
// Exporta singleton (um único gerenciador para a aplicação toda)
module.exports = new JobManager();
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
