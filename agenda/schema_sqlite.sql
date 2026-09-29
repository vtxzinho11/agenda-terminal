-- Estrutura das tabelas no SQLite (executada automaticamente na inicialização).
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS contatos (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nome      TEXT NOT NULL,
    telefone  TEXT NOT NULL DEFAULT '',
    email     TEXT NOT NULL DEFAULT '',
    criado_em TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_contatos_nome ON contatos (nome);

CREATE TABLE IF NOT EXISTS tarefas (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo     TEXT NOT NULL,
    descricao  TEXT NOT NULL DEFAULT '',
    prazo      TEXT,
    prioridade TEXT NOT NULL DEFAULT 'média',
    concluida  INTEGER NOT NULL DEFAULT 0 CHECK (concluida IN (0, 1)),
    contato_id INTEGER REFERENCES contatos (id) ON DELETE SET NULL,
    criado_em  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tarefas_prazo ON tarefas (prazo);
