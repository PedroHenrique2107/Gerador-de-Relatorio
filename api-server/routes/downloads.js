<<<<<<< HEAD
=======
// Rota responsável por servir arquivos gerados (relatórios).
// Permite download apenas de arquivos dentro da pasta configurada de downloads.
// Possui validações básicas de existência e segurança contra path traversal.

>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs');
const logger = require('../utils/logger');

<<<<<<< HEAD
const DOWNLOADS_FOLDER = path.resolve(process.env.DOWNLOADS_FOLDER || './downloads');

// GET /downloads/:filename - Download de arquivo
router.get('/:filename', (req, res) => {
  const filename = req.params.filename;
  const filepath = path.join(DOWNLOADS_FOLDER, filename);
  
  // Validar que arquivo existe
=======
// Diretório raiz do servidor da API
const API_SERVER_DIR = path.resolve(__dirname, '..');

// Pasta de downloads pode vir de variável de ambiente.
// Se não vier, usa ./downloads (relativo à raiz da API).
const configuredDownloads = process.env.DOWNLOADS_FOLDER || './downloads';

// Garante caminho absoluto final da pasta de downloads
// Evita ambiguidades de path relativo.
const DOWNLOADS_FOLDER = path.isAbsolute(configuredDownloads)
  ? configuredDownloads
  : path.resolve(API_SERVER_DIR, configuredDownloads);


/**
 * GET /downloads/:filename
 *
 * Responsável por entregar o arquivo solicitado ao cliente.
 * Exemplo: /downloads/relatorio_20260211.xlsx
 *
 * Fluxo:
 * 1. Monta caminho completo do arquivo
 * 2. Verifica se existe
 * 3. Garante que está dentro da pasta permitida (segurança)
 * 4. Inicia download
 */
router.get('/:filename', (req, res) => {
  const filename = req.params.filename;

  // Monta caminho completo do arquivo solicitado
  const filepath = path.join(DOWNLOADS_FOLDER, filename);
  
  // 1️⃣ Verifica se o arquivo realmente existe
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
  if (!fs.existsSync(filepath)) {
    logger.warn(`Arquivo não encontrado: ${filename}`);
    return res.status(404).json({ error: 'Arquivo não encontrado' });
  }
  
<<<<<<< HEAD
  // Validar que está dentro da pasta downloads (segurança)
  const resolvedPath = path.resolve(filepath);
=======
  // 2️⃣ Segurança: impede acesso fora da pasta downloads (ex: ../../etc/passwd)
  const resolvedPath = path.resolve(filepath);

  // Garante que o caminho final começa com a pasta permitida
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
  if (!resolvedPath.startsWith(DOWNLOADS_FOLDER)) {
    logger.warn(`Tentativa de acesso fora da pasta downloads: ${filename}`);
    return res.status(403).json({ error: 'Acesso negado' });
  }
  
<<<<<<< HEAD
  logger.info(`Download iniciado: ${filename}`);
  res.download(filepath);
});

=======
  // Log de auditoria de download
  logger.info(`Download iniciado: ${filename}`);

  // Envia arquivo para o cliente com headers corretos
  res.download(filepath);
});

// Exporta router para ser usado no app principal (ex: app.use('/downloads', router))
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
module.exports = router;
