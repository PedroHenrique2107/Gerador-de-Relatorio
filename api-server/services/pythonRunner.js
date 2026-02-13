// PythonRunner: executa scripts Python usados no pipeline do relatÃ³rio.
// Responsabilidades:
// - Descobrir qual Python usar (venv do projeto, PYTHON_PATH, ou python do sistema)
// - Montar argumentos e validar variÃ¡veis de ambiente obrigatÃ³rias
// - Executar scripts via child_process.spawn com timeout
// - Capturar stdout/stderr e retornar resultado (string ou JSON)
//
// IMPORTANTE: os scripts e pastas sÃ£o configurados via variÃ¡veis de ambiente:
// - PYTHON_PATH (opcional)
// - BACKEND_INSERT_SCRIPT (obrigatÃ³rio)
// - QUERY_SCRIPT (obrigatÃ³rio)
// - REPORT_SCRIPT (obrigatÃ³rio)
// - DATA_FOLDER (obrigatÃ³rio)
// - DOWNLOADS_FOLDER (obrigatÃ³rio)
// - JOB_TIMEOUT_MINUTES (opcional, default 30)

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const logger = require('../utils/logger');

// DiretÃ³rio da API (ex: api-server/)
const API_SERVER_DIR = path.resolve(__dirname, '..');

// Raiz do projeto (um nÃ­vel acima da API)
const PROJECT_ROOT = path.resolve(API_SERVER_DIR, '..');

// Timeout padrÃ£o: 30 min (configurÃ¡vel via JOB_TIMEOUT_MINUTES)
const TIMEOUT_MS = (parseInt(process.env.JOB_TIMEOUT_MINUTES, 10) || 30) * 60 * 1000;

class PythonRunner {
  // Detecta se a string parece ser um caminho (tem / ou \)
  hasPathSegments(value) {
    return value.includes('/') || value.includes('\\');
  }

  /**
   * Escolhe qual executÃ¡vel Python usar.
   * Prioridade:
   * 1) PYTHON_PATH (se existir e for vÃ¡lido)
   * 2) .venv do projeto (Windows e Linux)
   * 3) python3 / python do sistema
   */
  getPythonPath() {
    if (process.env.PYTHON_PATH) {
      const configured = process.env.PYTHON_PATH;

      // Se nÃ£o tem / ou \, assume que Ã© um comando (ex: "python" ou "python3")
      if (!this.hasPathSegments(configured)) {
        return configured;
      }

      // Se tem path, resolve relativo Ã  API e valida existÃªncia
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
   * LÃª uma variÃ¡vel de ambiente que deve ser um caminho (arquivo/pasta).
   * - Se for relativo, resolve relativo Ã  pasta da API.
   * - Se nÃ£o existir a env, lanÃ§a erro (fail-fast).
   */
  resolveEnvPath(name) {
    const value = process.env[name];
    if (!value) {
      throw new Error(`Variavel de ambiente obrigatoria ausente: ${name}`);
    }

    return path.isAbsolute(value) ? value : path.resolve(API_SERVER_DIR, value);
  }

  /**
   * Executa o script Python que lÃª JSON e insere no banco.
   * ParÃ¢metros e comportamento sÃ£o controlados via args fixos aqui.
   */
  async runBackendInsert() {
    const scriptPath = this.resolveEnvPath('BACKEND_INSERT_SCRIPT');
    const dataFolder = this.resolveEnvPath('DATA_FOLDER');
    const pattern = process.env.BACKEND_INSERT_PATTERN || 'SI_*.json';
    const chunkSize = process.env.BACKEND_INSERT_CHUNK_SIZE || '15000';

    // Args do script (contrato esperado do Python)
    const args = [
      scriptPath,
      '--dir', dataFolder,
      '--pattern', pattern,
      '--mode', 'quick',
      '--chunk-size', chunkSize,
      '--if-exists', 'replace'
    ];

    const pythonPath = this.getPythonPath();
    logger.info(`Executando backend insert: ${pythonPath} ${args.join(' ')}`);

    return this.runPythonScript(pythonPath, args, 'Backend Insert');
  }

  /**
   * Executa o script Python da query consolidada.
   * Normalmente prepara dados finais para exportaÃ§Ã£o.
   */
  async runQuery() {
    const scriptPath = this.resolveEnvPath('QUERY_SCRIPT');
    const args = [scriptPath];

    const pythonPath = this.getPythonPath();
    logger.info(`Executando query: ${pythonPath} ${args.join(' ')}`);

    return this.runPythonScript(pythonPath, args, 'Query Execution');
  }

  /**
   * Executa o script Python que gera o arquivo do relatÃ³rio.
   * Espera que o Python retorne no stdout um JSON com metadados do arquivo.
   * Exemplo esperado:
   * { fileName, fileSize, recordCount }
   */
  async runReportGeneration(formato) {
    const scriptPath = this.resolveEnvPath('REPORT_SCRIPT');
    const downloadFolder = this.resolveEnvPath('DOWNLOADS_FOLDER');

    const args = [
      scriptPath,
      '--formato', formato,
      '--output-dir', downloadFolder
    ];

    const pythonPath = this.getPythonPath();
    logger.info(`Executando geracao de relatorio: ${pythonPath} ${args.join(' ')}`);

    // stdout deve conter JSON (contrato com o Python)
    const output = await this.runPythonScript(pythonPath, args, 'Report Generation');

    // Converte stdout em objeto; se stdout nÃ£o for JSON, falha explicitamente
    try {
      return JSON.parse(output);
    } catch (e) {
      throw new Error(`Falha ao parsear resultado do relatorio: ${e.message}`);
    }
  }

  /**
   * Executor genÃ©rico de scripts Python.
   * - spawn com cwd = PROJECT_ROOT (scripts podem depender de paths relativos)
   * - captura stdout/stderr
   * - timeout global por job/etapa
   * - resolve stdout quando exit code = 0
   */
  async runPythonScript(pythonPath, args, stepName) {
    return new Promise((resolve, reject) => {
      const BACKEND_DIR = path.join(PROJECT_ROOT, 'backend');

      const child = spawn(pythonPath, args, {
        cwd: BACKEND_DIR,   // 🔥 roda dentro do backend
        env: {
          ...process.env,   // 🔥 repassa variáveis de ambiente
          PYTHONUTF8: '1',  // 🔥 evita problema com "Área" -> "�rea"
          PYTHONIOENCODING: 'utf-8',
        },
        windowsHide: true,
      });

      let stdout = '';
      let stderr = '';

      // Timeout: evita jobs travados indefinidamente
      const timeoutId = setTimeout(() => {
        child.kill();
        reject(new Error(`${stepName} timeout apos ${TIMEOUT_MS / 1000}s`));
      }, TIMEOUT_MS);

      // stdout (informaÃ§Ãµes e/ou retorno do script)
      child.stdout.on('data', (data) => {
        const text = data.toString();
        stdout += text;
        logger.debug(`[${stepName}] stdout: ${text.trim()}`);
      });

      // stderr (erros e logs do script)
      child.stderr.on('data', (data) => {
        const text = data.toString();
        stderr += text;
        logger.debug(`[${stepName}] stderr: ${text.trim()}`);
      });

      // Processo terminou (exit code)
      child.on('close', (code) => {
        clearTimeout(timeoutId);

        // Sucesso: devolve stdout como string
        if (code === 0) {
          resolve(stdout);
          return;
        }

        // Falha: devolve stderr para facilitar diagnÃ³stico
        reject(new Error(`${stepName} falhou com codigo ${code}: ${stderr}`));
      });

      // Erro de spawn (ex: python nÃ£o encontrado)
      child.on('error', (err) => {
        clearTimeout(timeoutId);
        reject(new Error(`Falha ao executar ${stepName}: ${err.message}`));
      });
    });
  }
}

module.exports = new PythonRunner();
