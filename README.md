# Agenda & To-Do no terminal (Python + SQLite)

CRUD completo de **tarefas** e **contatos**, mais uma visão de **agenda** (tarefas pendentes com prazo,
agrupadas em atrasadas / hoje / próximas).

**Só precisa de Python 3.10+.** O SQLite já vem com o Python: não há nada para instalar nem servidor para subir.

## Usar
```bash
python main.py
```
Os dados ficam em `~/.agenda_terminal/agenda.db` (um único arquivo). O arquivo e as tabelas são criados
na primeira execução. Para guardar em outra pasta: `AGENDA_DATA_DIR=/caminho python main.py`.
Para fazer backup, basta copiar o `agenda.db`.

## Testes
```bash
python -m unittest discover -s tests -v
```
A mesma suíte de regras de negócio roda sobre JSON e SQLite. Os testes de MySQL são ignorados a menos que
`AGENDA_TEST_MYSQL=1` esteja definido.

## Outros armazenamentos (opcional)
O padrão é `AGENDA_STORAGE=sqlite`. Também existem:
- `AGENDA_STORAGE=json`: arquivos JSON na mesma pasta de dados.
- `AGENDA_STORAGE=mysql`: exige `pip install -r requirements-mysql.txt` e as variáveis `MYSQL_HOST`,
  `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` (veja `.env.example`; `docker-compose.yml`
  sobe um MySQL local). Os testes de MySQL usam o banco `agenda_test` e apagam as tabelas dele.

## Estrutura
```
main.py                  ponto de entrada
agenda/
  models.py              entidades (Contato, Tarefa, Prioridade)
  validators.py          validação/normalização de entrada
  services.py            regras de negócio (CRUD, filtros, agenda)
  repository.py          contrato Repositorio + implementação JSON
  sqlite_database.py     conexão SQLite, transações, criação do esquema
  sqlite_repository.py   implementação SQLite (SQL parametrizado)
  schema_sqlite.sql      tabelas, índices e chave estrangeira
  mysql_*.py, schema_mysql.sql   alternativa MySQL (opcional)
  ui.py / cli.py         telas do terminal e composição das dependências
  config.py              variáveis de ambiente
  exceptions.py          erros do domínio
tests/                   mesma suíte de serviços em JSON, SQLite e (opcional) MySQL
```
Fluxo de dependências: `cli → services → Repositorio (SQLite | MySQL | JSON) → models`.
