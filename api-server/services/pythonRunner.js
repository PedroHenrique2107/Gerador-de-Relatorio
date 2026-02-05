const { spawn } = require('child_process');
const path = require('path');
const logger = require('../utils/logger');

const PYTHON_PATH = process.env.PYTHON_PATH || 'python3';
const TIMEOUT_MS = (parseInt(process.env.JOB_TIMEOUT_MINUTES) || 30) * 60 * 1000;

class PythonRunner {
  /**
   * Executa inserção de dados (backend/scripts/main.py)
   */
  async runBackendInsert() {
    const scriptPath = path.resolve(process.env.BACKEND_INSERT_SCRIPT);
    const dataFolder = path.resolve(process.env.DATA_FOLDER);
    
    const args = [
      scriptPath,
      '--dir', dataFolder,
      '--pattern', '*.json',
      '--mode', 'quick',
      '--chunk-size', '5000',
      '--if-exists', 'replace'
    ];
    
    logger.info(`Executando backend insert: ${PYTHON_PATH} ${args.join(' ')}`);
    
    return this.runPythonScript(args, 'Backend Insert');
  }
  
  /**
   * Executa query consolidada (query/execute_query.py)
   */
  async runQuery() {
    const scriptPath = path.resolve(process.env.QUERY_SCRIPT);
    
    const args = [scriptPath];
    
    logger.info(`Executando query: ${PYTHON_PATH} ${args.join(' ')}`);
    
    return this.runPythonScript(args, 'Query Execution');
  }
  
  /**
   * Executa geração de relatório (relatorio/generate_report.py)
   */
  async runReportGeneration(formato) {
    const scriptPath = path.resolve(process.env.REPORT_SCRIPT);
    const downloadFolder = path.resolve(process.env.DOWNLOADS_FOLDER);
    
    const args = [
      scriptPath,
      '--formato', formato,
      '--output-dir', downloadFolder
    ];
    
    logger.info(`Executando geração de relatório: ${PYTHON_PATH} ${args.join(' ')}`);
    
    const output = await this.runPythonScript(args, 'Report Generation');
    
    // Parsear resultado (formato JSON esperado do script Python)
    try {
      const result = JSON.parse(output);
      return result;
    } catch (e) {
      throw new Error(`Falha ao parsear resultado do relatório: ${e.message}`);
    }
  }
  
  /**
   * Executa script Python genérico
   */
  async runPythonScript(args, stepName) {
    return new Promise((resolve, reject) => {
      const process = spawn(PYTHON_PATH, args);
      
      let stdout = '';
      let stderr = '';
      
      // Timeout
      const timeoutId = setTimeout(() => {
        process.kill();
        reject(new Error(`${stepName} timeout após ${TIMEOUT_MS / 1000}s`));
      }, TIMEOUT_MS);
      
      // Capturar stdout
      process.stdout.on('data', (data) => {
        const text = data.toString();
        stdout += text;
        logger.debug(`[${stepName}] stdout: ${text.trim()}`);
      });
      
      // Capturar stderr
      process.stderr.on('data', (data) => {
        const text = data.toString();
        stderr += text;
        logger.debug(`[${stepName}] stderr: ${text.trim()}`);
      });
      
      // Processo finalizado
      process.on('close', (code) => {
        clearTimeout(timeoutId);
        
        if (code === 0) {
          resolve(stdout);
        } else {
          reject(new Error(`${stepName} falhou com código ${code}: ${stderr}`));
        }
      });
      
      // Erro ao iniciar processo
      process.on('error', (err) => {
        clearTimeout(timeoutId);
        reject(new Error(`Falha ao executar ${stepName}: ${err.message}`));
      });
    });
  }
}

module.exports = new PythonRunner();
