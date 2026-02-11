/**
 * SIENGE Sync Service
 * -----------------------------------------------------------------------------
 * Faz a sincronização dos JSONs do Sienge para a pasta backend/data.
 *
 * Endpoints sincronizados:
 * 1) Extrato Cliente Histórico
 * 2) Income (selectionType=B) -> Competência
 * 3) Income (selectionType=P) -> Pagamento
 * 4) Income (selectionType=I) -> Emissão
 *
 * Arquivos de saída:
 * - SI_EXTRATO_CLIENTE_HISTORICO.json
 * - SI_DATACOMPETPARCELAS.json
 * - SI_DATAPAGTO.json
 * - SI_DATAEMISSAO.json
 */

const fs = require("fs/promises");
const path = require("path");
const https = require("https");
const { URL } = require("url");
const logger = require("../utils/logger");

const API_SERVER_DIR = path.resolve(__dirname, "..");
const PROJECT_ROOT = path.resolve(API_SERVER_DIR, "..");
const DATA_DIR = path.resolve(PROJECT_ROOT, "backend", "data");

class SiengeSyncService {
  constructor() {
    this.defaultStartDate = process.env.SIENGE_START_DATE || "2000-01-01";
    this.defaultEndDate = process.env.SIENGE_END_DATE || "2100-12-31";
    this.timeoutMs = Number(process.env.SIENGE_TIMEOUT_MS || 120000);
  }

  /**
   * Base URL do tenant
   * Ex: https://api.sienge.com.br/smartcompass/public/api/bulk-data/v1
   */
  getBaseUrl() {
    const subdomain = process.env.SIENGE_SUBDOMAIN;
    const baseDomain = process.env.SIENGE_BASE_DOMAIN || "api.sienge.com.br";

    if (!subdomain) {
      throw new Error("Variável obrigatória ausente: SIENGE_SUBDOMAIN");
    }

    return `https://${baseDomain}/${subdomain}/public/api/bulk-data/v1`;
  }

  /**
   * Cabeçalhos de autenticação
   * Prioridade:
   * 1) Basic Auth (SIENGE_BASIC_USER + SIENGE_BASIC_PASS)
   * 2) Bearer Token (SIENGE_TOKEN)
   */
  getHeaders() {
    const basicUser = process.env.SIENGE_BASIC_USER;
    const basicPass = process.env.SIENGE_BASIC_PASS;
    const token = process.env.SIENGE_TOKEN;

    let authorization = null;

    if (basicUser && basicPass) {
      const basic = Buffer.from(`${basicUser}:${basicPass}`).toString("base64");
      authorization = `Basic ${basic}`;
    } else if (token) {
      authorization = token.startsWith("Bearer ") ? token : `Bearer ${token}`;
    } else {
      throw new Error(
        "Autenticação não configurada. Use SIENGE_BASIC_USER/SIENGE_BASIC_PASS ou SIENGE_TOKEN."
      );
    }

    return {
      Accept: "application/json",
      "Content-Type": "application/json",
      Authorization: authorization,
    };
  }

  /**
   * Monta URL com query params
   */
  buildUrl(endpointPath, queryParams = {}) {
    const url = new URL(`${this.getBaseUrl()}${endpointPath}`);

    for (const [key, value] of Object.entries(queryParams)) {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }

    return url;
  }

  /**
   * Requisição GET e parse de JSON
   */
  requestJson(url, headers) {
    return new Promise((resolve, reject) => {
      const req = https.request(
        url,
        {
          method: "GET",
          headers,
          timeout: this.timeoutMs,
        },
        (res) => {
          let raw = "";

          res.on("data", (chunk) => {
            raw += chunk.toString("utf8");
          });

          res.on("end", () => {
            const statusCode = res.statusCode || 0;

            if (statusCode < 200 || statusCode >= 300) {
              return reject(
                new Error(
                  `Sienge retornou ${statusCode} para ${url.pathname}: ${raw.slice(0, 700)}`
                )
              );
            }

            try {
              resolve(JSON.parse(raw));
            } catch (err) {
              reject(
                new Error(`Resposta inválida (não JSON) em ${url.pathname}: ${err.message}`)
              );
            }
          });
        }
      );

      req.on("timeout", () => {
        req.destroy(new Error(`Timeout após ${this.timeoutMs}ms em ${url.pathname}`));
      });

      req.on("error", (err) => reject(err));

      req.end();
    });
  }

  /**
   * Garante pasta de dados e grava arquivo JSON
   */
  async writeJson(fileName, payload) {
    await fs.mkdir(DATA_DIR, { recursive: true });
    const filePath = path.join(DATA_DIR, fileName);
    await fs.writeFile(filePath, JSON.stringify(payload, null, 2), "utf8");
    return filePath;
  }

  /**
   * Sincroniza todos os datasets
   */
  async syncAll() {
    const headers = this.getHeaders();

    const tasks = [
      {
        id: "extrato",
        fileName: "SI_EXTRATO_CLIENTE_HISTORICO.json",
        endpoint: "/customer-extract-history",
        query: {
          startDueDate: this.defaultStartDate,
          endDueDate: this.defaultEndDate,
        },
      },
      {
        id: "income_competencia",
        fileName: "SI_DATACOMPETPARCELAS.json",
        endpoint: "/income",
        query: {
          startDate: this.defaultStartDate,
          endDate: this.defaultEndDate,
          selectionType: "B",
        },
      },
      {
        id: "income_pagto",
        fileName: "SI_DATAPAGTO.json",
        endpoint: "/income",
        query: {
          startDate: this.defaultStartDate,
          endDate: this.defaultEndDate,
          selectionType: "P",
        },
      },
      {
        id: "income_emissao",
        fileName: "SI_DATAEMISSAO.json",
        endpoint: "/income",
        query: {
          startDate: this.defaultStartDate,
          endDate: this.defaultEndDate,
          selectionType: "I",
        },
      },
    ];

    const result = {
      startedAt: new Date().toISOString(),
      dataDir: DATA_DIR,
      files: [],
    };

    for (const task of tasks) {
      const url = this.buildUrl(task.endpoint, task.query);

      logger.info(`[SIENGE_SYNC] Requisição ${task.id}: ${url.toString()}`);
      const payload = await this.requestJson(url, headers);
      const savedPath = await this.writeJson(task.fileName, payload);

      result.files.push({
        id: task.id,
        fileName: task.fileName,
        savedPath,
        endpoint: `${task.endpoint}?${url.searchParams.toString()}`,
      });

      logger.info(`[SIENGE_SYNC] Arquivo atualizado: ${task.fileName}`);
    }

    result.finishedAt = new Date().toISOString();
    return result;
  }
}

module.exports = new SiengeSyncService();
