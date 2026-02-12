// Rota responsÃ¡vel por servir arquivos gerados (relatÃ³rios).
// Permite download apenas de arquivos dentro da pasta configurada de downloads.
// Possui validaÃ§Ãµes bÃ¡sicas de existÃªncia e seguranÃ§a contra path traversal.

const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs');
const logger = require('../utils/logger');

// DiretÃ³rio raiz do servidor da API
const API_SERVER_DIR = path.resolve(__dirname, '..');

// Pasta de downloads pode vir de variÃ¡vel de ambiente.
// Se nÃ£o vier, usa ./downloads (relativo Ã  raiz da API).
const configuredDownloads = process.env.DOWNLOADS_FOLDER || './downloads';

// Garante caminho absoluto final da pasta de downloads
// Evita ambiguidades de path relativo.
const DOWNLOADS_FOLDER = path.isAbsolute(configuredDownloads)
  ? configuredDownloads
  : path.resolve(API_SERVER_DIR, configuredDownloads);


/**
 * GET /downloads/:filename
 *
 * ResponsÃ¡vel por entregar o arquivo solicitado ao cliente.
 * Exemplo: /downloads/relatorio_20260211.xlsx
 *
 * Fluxo:
 * 1. Monta caminho completo do arquivo
 * 2. Verifica se existe
 * 3. Garante que estÃ¡ dentro da pasta permitida (seguranÃ§a)
 * 4. Inicia download
 */
router.get('/:filename', (req, res) => {
  const filename = req.params.filename;

  // Monta caminho completo do arquivo solicitado
  const filepath = path.join(DOWNLOADS_FOLDER, filename);
  
  // 1ï¸âƒ£ Verifica se o arquivo realmente existe
  if (!fs.existsSync(filepath)) {
    logger.warn(`Arquivo nÃ£o encontrado: ${filename}`);
    return res.status(404).json({ error: 'Arquivo nÃ£o encontrado' });
  }
  
  // 2ï¸âƒ£ SeguranÃ§a: impede acesso fora da pasta downloads (ex: ../../etc/passwd)
  const resolvedPath = path.resolve(filepath);

  // Garante que o caminho final comeÃ§a com a pasta permitida
  if (!resolvedPath.startsWith(DOWNLOADS_FOLDER)) {
    logger.warn(`Tentativa de acesso fora da pasta downloads: ${filename}`);
    return res.status(403).json({ error: 'Acesso negado' });
  }
  
  // Log de auditoria de download
  logger.info(`Download iniciado: ${filename}`);

  // Envia arquivo para o cliente com headers corretos
  res.download(filepath);
});

// Exporta router para ser usado no app principal (ex: app.use('/downloads', router))
module.exports = router;
