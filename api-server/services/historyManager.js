const fs = require('fs').promises;
const path = require('path');
const logger = require('../utils/logger');
const { formatBytes, formatDuration } = require('../utils/formatters');

const DATA_DIR = path.join(__dirname, '..', 'data');
const HISTORY_FILE = path.join(DATA_DIR, 'history.json');
const MAX_RECORDS = parseInt(process.env.HISTORY_MAX_RECORDS) || 10;

class HistoryManager {
  constructor() {
    this.ensureDataDir();
  }
  
  /**
   * Garante que diretório data existe
   */
  async ensureDataDir() {
    try {
      await fs.mkdir(DATA_DIR, { recursive: true });
    } catch (error) {
      logger.error(`Erro ao criar diretório data: ${error.message}`);
    }
  }
  
  /**
   * Adiciona job ao histórico
   */
  async addToHistory(job) {
    try {
      let history = await this.loadHistory();
      
      const entry = {
        id: history.length + 1,
        jobId: job.jobId,
        formato: job.formato,
        syncBeforeRun: Boolean(job.syncBeforeRun),
        status: job.status,
        fileName: job.result.fileName,
        fileSize: job.result.fileSize,
        recordCount: job.result.recordCount,
        processingTime: formatDuration(job.timing.elapsedSeconds),
        createdAt: job.timing.startTime,
        downloadUrl: job.result.downloadUrl,
        error: job.error
      };
      
      history.unshift(entry);
      
      // Manter apenas MAX_RECORDS
      if (history.length > MAX_RECORDS) {
        history = history.slice(0, MAX_RECORDS);
      }
      
      await this.saveHistory(history);
      
      logger.info(`Histórico atualizado: ${job.jobId}`);
      
    } catch (error) {
      logger.error(`Erro ao adicionar ao histórico: ${error.message}`);
    }
  }
  
  /**
   * Retorna histórico
   */
  async getHistory() {
    return await this.loadHistory();
  }
  
  /**
   * Carrega histórico do arquivo
   */
  async loadHistory() {
    try {
      const data = await fs.readFile(HISTORY_FILE, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      if (error.code === 'ENOENT') {
        return [];
      }
      logger.error(`Erro ao carregar histórico: ${error.message}`);
      return [];
    }
  }
  
  /**
   * Salva histórico no arquivo
   */
  async saveHistory(history) {
    try {
      await fs.writeFile(HISTORY_FILE, JSON.stringify(history, null, 2));
    } catch (error) {
      logger.error(`Erro ao salvar histórico: ${error.message}`);
    }
  }
}

module.exports = new HistoryManager();
