/**
 * Arquivo de rotas responsável pelas requisições relacionadas ao Sienge.
 * 
 * Aqui definimos quais URLs (endpoints) o sistema terá
 * e qual controller será chamado em cada uma.
 */


// Importa o framework Express
const express = require("express");

/**
 * Cria uma instância de roteador do Express.
 * 
 * O Router serve para organizar as rotas em módulos separados,
 * evitando deixar tudo no app.js/server.js.
 */
const router = express.Router();


// Importa o controller responsável pelas ações do Sienge
const siengeController = require("../controllers/siengeController");


/**
 * Rota responsável por executar a sincronização do Sienge.
 * 
 * Método HTTP: POST
 * Endpoint: /api/sienge/sync
 * 
 * Quando essa rota for chamada, executa:
 * siengeController.sync
 */
router.post("/sync", siengeController.sync);


/**
 * Exporta o router para ser usado no arquivo principal da API
 * (geralmente app.js ou server.js).
 * 
 * Exemplo de uso:
 * app.use("/api/sienge", router);
 */
module.exports = router;
