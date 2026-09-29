-- Estrutura das tabelas (executada automaticamente na inicialização).
CREATE TABLE IF NOT EXISTS contatos (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    nome      VARCHAR(120) NOT NULL,
    telefone  VARCHAR(20)  NOT NULL DEFAULT '',
    email     VARCHAR(255) NOT NULL DEFAULT '',
    criado_em DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_contatos_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS tarefas (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    titulo     VARCHAR(200) NOT NULL,
    descricao  TEXT         NOT NULL,
    prazo      DATE         NULL,
    prioridade VARCHAR(10)  NOT NULL DEFAULT 'média',
    concluida  TINYINT(1)   NOT NULL DEFAULT 0,
    contato_id INT          NULL,
    criado_em  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tarefas_prazo (prazo),
    CONSTRAINT fk_tarefas_contato FOREIGN KEY (contato_id)
        REFERENCES contatos (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
