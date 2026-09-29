"""(Opcional) Conexão com o MySQL e criação do esquema."""
from __future__ import annotations

import re
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from .exceptions import ErroDeArmazenamento

try:
    import mysql.connector
    from mysql.connector import Error as ErroMySQL
except ImportError as erro:  # driver não instalado
    raise ErroDeArmazenamento(
        "Driver do MySQL não encontrado. Instale com: pip install -r requirements.txt"
    ) from erro

_ARQUIVO_SCHEMA = Path(__file__).with_name("schema_mysql.sql")
_NOME_BANCO_VALIDO = re.compile(r"^[A-Za-z0-9_]{1,64}$")


@dataclass(frozen=True)
class ConfigMySQL:
    host: str = "127.0.0.1"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = "agenda"


class BancoMySQL:
    """Abre uma conexão por operação: simples e sem risco de conexão expirada."""

    def __init__(self, config: ConfigMySQL) -> None:
        if not _NOME_BANCO_VALIDO.match(config.database):
            raise ErroDeArmazenamento(
                "Nome de banco inválido: use apenas letras, números e '_' (máx. 64)."
            )
        self._config = config

    def _conectar(self, com_banco: bool = True):
        parametros = {
            "host": self._config.host,
            "port": self._config.port,
            "user": self._config.user,
            "password": self._config.password,
            "charset": "utf8mb4",
            "connection_timeout": 5,
        }
        if com_banco:
            parametros["database"] = self._config.database
        try:
            return mysql.connector.connect(**parametros)
        except ErroMySQL as erro:
            raise ErroDeArmazenamento(
                f"Não foi possível conectar ao MySQL em "
                f"{self._config.host}:{self._config.port} ({erro}). "
                "Confira as variáveis MYSQL_HOST, MYSQL_PORT, MYSQL_USER, "
                "MYSQL_PASSWORD e MYSQL_DATABASE."
            ) from erro

    @contextmanager
    def cursor(self) -> Iterator:
        """Cursor que devolve dicionários; faz commit/rollback e fecha a conexão."""
        conexao = self._conectar()
        try:
            cursor = conexao.cursor(dictionary=True)
            yield cursor
            conexao.commit()
        except ErroMySQL as erro:
            conexao.rollback()
            raise ErroDeArmazenamento(f"Erro no banco de dados: {erro}") from erro
        except Exception:
            conexao.rollback()
            raise
        finally:
            conexao.close()

    def criar_esquema(self) -> None:
        """Cria o banco (se o usuário tiver permissão) e as tabelas, se ainda não existirem."""
        conexao = self._conectar(com_banco=False)
        try:
            conexao.cursor().execute(
                f"CREATE DATABASE IF NOT EXISTS `{self._config.database}` "
                "CHARACTER SET utf8mb4"
            )
            conexao.commit()
        except ErroMySQL as erro:
            raise ErroDeArmazenamento(f"Não foi possível criar o banco: {erro}") from erro
        finally:
            conexao.close()

        linhas = [
            linha
            for linha in _ARQUIVO_SCHEMA.read_text(encoding="utf-8").splitlines()
            if not linha.strip().startswith("--")
        ]
        comandos = [c.strip() for c in "\n".join(linhas).split(";") if c.strip()]
        with self.cursor() as cursor:
            for comando in comandos:
                cursor.execute(comando)

    def apagar_tabelas(self) -> None:
        """Uso em testes: remove as tabelas."""
        with self.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS tarefas")
            cursor.execute("DROP TABLE IF EXISTS contatos")
