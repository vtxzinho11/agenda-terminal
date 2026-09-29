"""Conexão com o SQLite (biblioteca padrão do Python: não exige instalação)."""
from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from .exceptions import ErroDeArmazenamento

_ARQUIVO_SCHEMA = Path(__file__).with_name("schema_sqlite.sql")


class BancoSQLite:
    """Abre uma conexão por operação, com chaves estrangeiras ativadas."""

    def __init__(self, caminho: Path) -> None:
        self._caminho = Path(caminho)

    @contextmanager
    def cursor(self) -> Iterator[sqlite3.Cursor]:
        """Cursor com commit/rollback automáticos; a conexão é sempre fechada."""
        try:
            self._caminho.parent.mkdir(parents=True, exist_ok=True)
            conexao = sqlite3.connect(self._caminho, timeout=5)
        except (OSError, sqlite3.Error) as erro:
            raise ErroDeArmazenamento(
                f"Não foi possível abrir o banco {self._caminho}: {erro}"
            ) from erro
        conexao.row_factory = sqlite3.Row
        try:
            conexao.execute("PRAGMA foreign_keys = ON")  # é por conexão no SQLite
            yield conexao.cursor()
            conexao.commit()
        except sqlite3.Error as erro:
            conexao.rollback()
            raise ErroDeArmazenamento(f"Erro no banco de dados: {erro}") from erro
        except Exception:
            conexao.rollback()
            raise
        finally:
            conexao.close()

    def criar_esquema(self) -> None:
        """Cria o arquivo do banco e as tabelas, se ainda não existirem."""
        script = _ARQUIVO_SCHEMA.read_text(encoding="utf-8")
        with self.cursor() as cursor:
            cursor.executescript(script)
