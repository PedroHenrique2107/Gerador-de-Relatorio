/**
 * Controller responsável por executar a sincronização de dados do Sienge.
 * 
 * Esse endpoint é chamado via requisição HTTP e dispara o serviço
 * que realiza a sincronização completa (syncAll).
 * 
 * Fluxo:
 * 1. Recebe a requisição
 * 2. Chama o serviço de sincronização
 * 3. Retorna sucesso ou erro para o cliente
 */

// Importa o serviço que contém a lógica de sincronização com o Sienge
const siengeSyncService = require("../services/siengeSyncService");

// Importa o logger para registrar erros e eventos no sistema
const logger = require("../utils/logger");


/**
 * Método responsável por executar a sincronização completa.
 * 
 * Rota esperada (exemplo):
 * POST /sienge/sync
 * ou
 * GET /sienge/sync
 * 
 * @param {Request} req  → Dados da requisição HTTP
 * @param {Response} res → Objeto de resposta HTTP
 */
exports.sync = async (req, res) => {
  try {

    /**
     * Executa a sincronização chamando o serviço principal.
     * 
     * syncAll() provavelmente:
     * - Consulta dados no Sienge
     * - Processa informações
     * - Insere/atualiza no banco local
     */
    const result = await siengeSyncService.syncAll();


    /**
     * Retorna resposta de sucesso para o cliente.
     * Status HTTP: 200 (OK)
     */
    res.status(200).json({
      ok: true, // Flag indicando sucesso
      message: "Sincronizacao Sienge concluida com sucesso", // Mensagem descritiva
      result, // Retorno detalhado do serviço (quantidades, logs, etc.)
    });

  } catch (error) {

    /**
     * Caso ocorra erro durante a sincronização:
     * - Registra no log do sistema
     * - Retorna erro para o cliente
     */
    logger.error(`Erro no sync Sienge: ${error.message}`);


    /**
     * Retorna resposta de erro.
     * Status HTTP: 500 (Erro interno do servidor)
     */
    res.status(500).json({
      ok: false, // Flag indicando falha
      error: error.message, // Mensagem do erro ocorrido
    });
  }
};