<<<<<<< HEAD
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
    
=======
// PythonRunner: executa scripts Python usados no pipeline do relatório.
// Responsabilidades:
// - Descobrir qual Python usar (venv do projeto, PYTHON_PATH, ou python do sistema)
// - Montar argumentos e validar variáveis de ambiente obrigatórias
// - Executar scripts via child_process.spawn com timeout
// - Capturar stdout/stderr e retornar resultado (string ou JSON)
//
// IMPORTANTE: os scripts e pastas são configurados via variáveis de ambiente:
// - PYTHON_PATH (opcional)
// - BACKEND_INSERT_SCRIPT (obrigatório)
// - QUERY_SCRIPT (obrigatório)
// - REPORT_SCRIPT (obrigatório)
// - DATA_FOLDER (obrigatório)
// - DOWNLOADS_FOLDER (obrigatório)
// - JOB_TIMEOUT_MINUTES (opcional, default 30)

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const logger = require('../utils/logger');

// Diretório da API (ex: api-server/)
const API_SERVER_DIR = path.resolve(__dirname, '..');

// Raiz do projeto (um nível acima da API)
const PROJECT_ROOT = path.resolve(API_SERVER_DIR, '..');

// Timeout padrão: 30 min (configurável via JOB_TIMEOUT_MINUTES)
const TIMEOUT_MS = (parseInt(process.env.JOB_TIMEOUT_MINUTES, 10) || 30) * 60 * 1000;

class PythonRunner {
  // Detecta se a string parece ser um caminho (tem / ou \)
  hasPathSegments(value) {
    return value.includes('/') || value.includes('\\');
  }

  /**
   * Escolhe qual executável Python usar.
   * Prioridade:
   * 1) PYTHON_PATH (se existir e for válido)
   * 2) .venv do projeto (Windows e Linux)
   * 3) python3 / python do sistema
   */
  getPythonPath() {
    if (process.env.PYTHON_PATH) {
      const configured = process.env.PYTHON_PATH;

      // Se não tem / ou \, assume que é um comando (ex: "python" ou "python3")
      if (!this.hasPathSegments(configured)) {
        return configured;
      }

      // Se tem path, resolve relativo à API e valida existência
      const resolvedConfigured = path.resolve(API_SERVER_DIR, configured);
      if (fs.existsSync(resolvedConfigured)) {
        return resolvedConfigured;
      }
    }

    // Lista de candidatos (venv local do projeto + fallback para python do sistema)
    const candidates = [
      path.join(PROJECT_ROOT, 'backend', '.venv', 'Scripts', 'python.exe'), // Windows
      path.join(PROJECT_ROOT, 'backend', '.venv', 'Scripts', 'python'),     // Windows (varia)
      path.join(PROJECT_ROOT, 'backend', '.venv', 'bin', 'python3'),        // Linux/mac
      path.join(PROJECT_ROOT, 'backend', '.venv', 'bin', 'python'),         // Linux/mac
      'python3',
      'python'
    ];

    // Retorna o primeiro candidato que exista (se for path) ou que seja um comando
    for (const candidate of candidates) {
      if (!candidate.includes(path.sep) || fs.existsSync(candidate)) {
        return candidate;
      }
    }

    // Fallback final
    return 'python';
  }

  /**
   * Lê uma variável de ambiente que deve ser um caminho (arquivo/pasta).
   * - Se for relativo, resolve relativo à pasta da API.
   * - Se não existir a env, lança erro (fail-fast).
   */
  resolveEnvPath(name) {
    const value = process.env[name];
    if (!value) {
      throw new Error(`Variavel de ambiente obrigatoria ausente: ${name}`);
    }

    return path.isAbsolute(value) ? value : path.resolve(API_SERVER_DIR, value);
  }

  /**
   * Executa o script Python que lê JSON e insere no banco.
   * Parâmetros e comportamento são controlados via args fixos aqui.
   */
  async runBackendInsert() {
    const scriptPath = this.resolveEnvPath('BACKEND_INSERT_SCRIPT');
    const dataFolder = this.resolveEnvPath('DATA_FOLDER');

    // Args do script (contrato esperado do Python)
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
    const args = [
      scriptPath,
      '--dir', dataFolder,
      '--pattern', '*.json',
      '--mode', 'quick',
      '--chunk-size', '5000',
      '--if-exists', 'replace'
    ];
<<<<<<< HEAD
    
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
    
=======

    const pythonPath = this.getPythonPath();
    logger.info(`Executando backend insert: ${pythonPath} ${args.join(' ')}`);

    return this.runPythonScript(pythonPath, args, 'Backend Insert');
  }

  /**
   * Executa o script Python da query consolidada.
   * Normalmente prepara dados finais para exportação.
   */
  async runQuery() {
    const scriptPath = this.resolveEnvPath('QUERY_SCRIPT');
    const args = [scriptPath];

    const pythonPath = this.getPythonPath();
    logger.info(`Executando query: ${pythonPath} ${args.join(' ')}`);

    return this.runPythonScript(pythonPath, args, 'Query Execution');
  }

  /**
   * Executa o script Python que gera o arquivo do relatório.
   * Espera que o Python retorne no stdout um JSON com metadados do arquivo.
   * Exemplo esperado:
   * { fileName, fileSize, recordCount }
   */
  async runReportGeneration(formato) {
    const scriptPath = this.resolveEnvPath('REPORT_SCRIPT');
    const downloadFolder = this.resolveEnvPath('DOWNLOADS_FOLDER');

>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
    const args = [
      scriptPath,
      '--formato', formato,
      '--output-dir', downloadFolder
    ];
<<<<<<< HEAD
    
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
=======

    const pythonPath = this.getPythonPath();
    logger.info(`Executando geracao de relatorio: ${pythonPath} ${args.join(' ')}`);

    // stdout deve conter JSON (contrato com o Python)
    const output = await this.runPythonScript(pythonPath, args, 'Report Generation');

    // Converte stdout em objeto; se stdout não for JSON, falha explicitamente
    try {
      return JSON.parse(output);
    } catch (e) {
      throw new Error(`Falha ao parsear resultado do relatorio: ${e.message}`);
    }
  }

  /**
   * Executor genérico de scripts Python.
   * - spawn com cwd = PROJECT_ROOT (scripts podem depender de paths relativos)
   * - captura stdout/stderr
   * - timeout global por job/etapa
   * - resolve stdout quando exit code = 0
   */
  async runPythonScript(pythonPath, args, stepName) {
    return new Promise((resolve, reject) => {
      const child = spawn(pythonPath, args, { cwd: PROJECT_ROOT });

      let stdout = '';
      let stderr = '';

      // Timeout: evita jobs travados indefinidamente
      const timeoutId = setTimeout(() => {
        child.kill();
        reject(new Error(`${stepName} timeout apos ${TIMEOUT_MS / 1000}s`));
      }, TIMEOUT_MS);

      // stdout (informações e/ou retorno do script)
      child.stdout.on('data', (data) => {
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
        const text = data.toString();
        stdout += text;
        logger.debug(`[${stepName}] stdout: ${text.trim()}`);
      });
<<<<<<< HEAD
      
      // Capturar stderr
      process.stderr.on('data', (data) => {
=======

      // stderr (erros e logs do script)
      child.stderr.on('data', (data) => {
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
        const text = data.toString();
        stderr += text;
        logger.debug(`[${stepName}] stderr: ${text.trim()}`);
      });
<<<<<<< HEAD
      
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
=======

      // Processo terminou (exit code)
      child.on('close', (code) => {
        clearTimeout(timeoutId);

        // Sucesso: devolve stdout como string
        if (code === 0) {
          resolve(stdout);
          return;
        }

        // Falha: devolve stderr para facilitar diagnóstico
        reject(new Error(`${stepName} falhou com codigo ${code}: ${stderr}`));
      });

      // Erro de spawn (ex: python não encontrado)
      child.on('error', (err) => {
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
        clearTimeout(timeoutId);
        reject(new Error(`Falha ao executar ${stepName}: ${err.message}`));
      });
    });
  }
}

module.exports = new PythonRunner();
