<<<<<<< HEAD
const winston = require('winston');
const path = require('path');

const logDir = path.join(__dirname, '..', 'logs');

const logger = winston.createLogger({
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
    winston.format.errors({ stack: true }),
    winston.format.printf(({ timestamp, level, message, stack }) => {
      return `${timestamp} [${level.toUpperCase()}]: ${stack || message}`;
    })
  ),
  transports: [
=======
// Logger central da aplicação usando Winston.
// Responsável por:
// - Padronizar formato de logs
// - Definir nível de log por ambiente (dev vs produção)
// - Exibir logs no console com timestamp e stack trace
//
// OBS: Atualmente loga apenas no Console.
// A variável logDir está definida, mas não está sendo usada (pode ser usada futuramente para logs em arquivo).

const winston = require('winston');
const path = require('path');

// Diretório onde logs poderiam ser salvos em arquivo (não utilizado atualmente)
const logDir = path.join(__dirname, '..', 'logs');

const logger = winston.createLogger({
  // Em produção mostra apenas info+.
  // Em desenvolvimento mostra debug+.
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',

  // Formato padrão aplicado antes de enviar para os transports
  format: winston.format.combine(
    // Adiciona timestamp no formato legível
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),

    // Permite capturar stack trace quando for Error
    winston.format.errors({ stack: true }),

    // Define formato final da mensagem
    winston.format.printf(({ timestamp, level, message, stack }) => {
      // Se existir stack (erro), imprime stack.
      // Caso contrário, imprime apenas mensagem.
      return `${timestamp} [${level.toUpperCase()}]: ${stack || message}`;
    })
  ),

  transports: [
    // Transport Console (stdout)
    // Em desenvolvimento aplica cores para facilitar leitura.
>>>>>>> 539d0c7 (versão completa do gerador de relatórios)
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.printf(({ timestamp, level, message }) => {
          return `${timestamp} ${level}: ${message}`;
        })
      )
    })
  ]
});

module.exports = logger;
