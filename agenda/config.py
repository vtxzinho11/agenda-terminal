"""Configuração da aplicação."""
import os
from pathlib import Path

VARIAVEL_DIRETORIO = "AGENDA_DATA_DIR"


def obter_diretorio_dados() -> Path:
    """Pasta de dados: banco SQLite ou JSONs (padrão: ~/.agenda_terminal)."""
    personalizado = os.environ.get(VARIAVEL_DIRETORIO)
    return Path(personalizado) if personalizado else Path.home() / ".agenda_terminal"


def obter_tipo_armazenamento() -> str:
    """'sqlite' (padrão), 'mysql' ou 'json' (variável AGENDA_STORAGE)."""
    return os.environ.get("AGENDA_STORAGE", "sqlite").strip().lower()


def obter_caminho_sqlite() -> Path:
    """Arquivo do banco SQLite (padrão: ~/.agenda_terminal/agenda.db)."""
    return obter_diretorio_dados() / "agenda.db"


def obter_config_mysql():
    """Lê a conexão das variáveis de ambiente (a senha nunca fica no código)."""
    from .mysql_database import ConfigMySQL
    from .exceptions import ErroDeArmazenamento

    try:
        porta = int(os.environ.get("MYSQL_PORT", "3306"))
    except ValueError:
        raise ErroDeArmazenamento("MYSQL_PORT deve ser um número inteiro.") from None
    return ConfigMySQL(
        host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
        port=porta,
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        database=os.environ.get("MYSQL_DATABASE", "agenda"),
    )
