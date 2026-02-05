const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs');
const logger = require('../utils/logger');

const DOWNLOADS_FOLDER = path.resolve(process.env.DOWNLOADS_FOLDER || './downloads');

// GET /downloads/:filename - Download de arquivo
router.get('/:filename', (req, res) => {
  const filename = req.params.filename;
  const filepath = path.join(DOWNLOADS_FOLDER, filename);
  
  // Validar que arquivo existe
  if (!fs.existsSync(filepath)) {
    logger.warn(`Arquivo não encontrado: ${filename}`);
    return res.status(404).json({ error: 'Arquivo não encontrado' });
  }
  
  // Validar que está dentro da pasta downloads (segurança)
  const resolvedPath = path.resolve(filepath);
  if (!resolvedPath.startsWith(DOWNLOADS_FOLDER)) {
    logger.warn(`Tentativa de acesso fora da pasta downloads: ${filename}`);
    return res.status(403).json({ error: 'Acesso negado' });
  }
  
  logger.info(`Download iniciado: ${filename}`);
  res.download(filepath);
});

module.exports = router;
