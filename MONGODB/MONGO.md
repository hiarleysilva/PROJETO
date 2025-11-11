// CRIAÇÃO E CONFIGURAÇÃO DA COLLECTION (MongoDB Shell)

use biblioteca_db;

db.createCollection("atividade_logs", {
  capped: true,
  size: 5242880, // 5 Megabytes
  max: 5000      // Máximo de 5000 documentos
});

// 2.2: CRIAÇÃO DE ÍNDICES NO MONGODB

// Justificativa: Para buscar os logs mais recentes rapidamente
db.atividade_logs.createIndex({ timestamp: -1 });

// Justificativa: Para auditar a atividade de um usuário específico
db.atividade_logs.createIndex({ usuario_id: 1 });

// Justificativa: Para filtrar por tipos de ação (ex: 'LOGIN', 'ERRO')
db.atividade_logs.createIndex({ aco: 1 });

// 2.3: EXEMPLOS DE DOCUMENTOS (BSON/JSON)
// Demonstração da aplicação e da flexibilidade do schema-less

// Exemplo 1: Usuário fez login (Auditoria de Segurança)
db.atividade_logs.insertOne({
    timestamp: new Date(),
    usuario_id: "JOA25U000001", // ID do MySQL
    acao: "LOGIN_SUCESSO",
    ip_origem: "189.45.12.1"
});

// Exemplo 2: Usuário fez uma busca (Histórico de Buscas / Analytics)
// Justificativa: Dados semi-estruturados que não cabem no MySQL
db.atividade_logs.insertOne({
    timestamp: new Date(),
    usuario_id: "ANA25U000002",
    acao: "BUSCA_LIVRO",
    detalhes: {
        termo_busca: "Inteligência Artificial",
        resultados_encontrados: 5,
        filtro_categoria: "Tecnologia"
    }
});

// Exemplo 3: Procedure do MySQL falhou (Log de Erro para Analytics)
// Justificativa: Captura de erros de lógica de negócio para análise
db.atividade_logs.insertOne({
    timestamp: new Date(),
    usuario_id: "ANA25U000002",
    acao: "ERRO_PROCEDURE",
    severidade: "media",
    detalhes: {
        procedure: "sp_realizar_emprestimo",
        erro_mysql: "45000",
        mensagem_retornada: "Limite de empréstimos atingido",
        livro_tentativa: "IAE24L000001"
    }
});

// Exemplo 4: Empréstimo realizado (Log de Ação Crítica)
db.atividade_logs.insertOne({
    timestamp: new Date(),
    usuario_id: "MAR25U000003",
    acao: "EMPRESTIMO_REALIZADO",
    detalhes: {
        emprestimo_id: "EMP20251106123456",
        livro_id: "FIC23L000004",
        atendente_id: "bib_funcionario" // Usuário do MySQL que executou a ação
    }
});