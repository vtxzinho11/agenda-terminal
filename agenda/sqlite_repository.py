"""Repositórios SQLite: mesma interface do JsonRepository (listar/obter/adicionar/atualizar/remover)."""
from __future__ import annotations

import sqlite3
from datetime import date

from .exceptions import ErroNaoEncontrado
from .models import Contato, Prioridade, Tarefa
from .sqlite_database import BancoSQLite


class _BaseSQLite:
    _tabela = ""

    def __init__(self, banco: BancoSQLite) -> None:
        self._banco = banco

    def remover(self, item_id: int) -> bool:
        with self._banco.cursor() as cursor:
            cursor.execute(f"DELETE FROM {self._tabela} WHERE id = ?", (item_id,))
            return cursor.rowcount > 0


class ContatoSQLiteRepository(_BaseSQLite):
    _tabela = "contatos"

    @staticmethod
    def _para_modelo(linha: sqlite3.Row) -> Contato:
        return Contato(
            id=linha["id"],
            nome=linha["nome"],
            telefone=linha["telefone"],
            email=linha["email"],
            criado_em=linha["criado_em"],
        )

    def listar(self) -> list[Contato]:
        with self._banco.cursor() as cursor:
            cursor.execute("SELECT * FROM contatos ORDER BY id")
            return [self._para_modelo(l) for l in cursor.fetchall()]

    def obter(self, item_id: int) -> Contato | None:
        with self._banco.cursor() as cursor:
            cursor.execute("SELECT * FROM contatos WHERE id = ?", (item_id,))
            linha = cursor.fetchone()
            return self._para_modelo(linha) if linha else None

    def adicionar(self, contato: Contato) -> Contato:
        with self._banco.cursor() as cursor:
            cursor.execute(
                "INSERT INTO contatos (nome, telefone, email, criado_em) VALUES (?, ?, ?, ?)",
                (contato.nome, contato.telefone, contato.email, contato.criado_em),
            )
            contato.id = cursor.lastrowid
        return contato

    def atualizar(self, contato: Contato) -> Contato:
        with self._banco.cursor() as cursor:
            cursor.execute(
                "UPDATE contatos SET nome = ?, telefone = ?, email = ? WHERE id = ?",
                (contato.nome, contato.telefone, contato.email, contato.id),
            )
            if cursor.rowcount == 0:
                raise ErroNaoEncontrado(f"Registro #{contato.id} não encontrado.")
        return contato


class TarefaSQLiteRepository(_BaseSQLite):
    _tabela = "tarefas"

    @staticmethod
    def _para_modelo(linha: sqlite3.Row) -> Tarefa:
        return Tarefa(
            id=linha["id"],
            titulo=linha["titulo"],
            descricao=linha["descricao"],
            prazo=date.fromisoformat(linha["prazo"]) if linha["prazo"] else None,
            prioridade=Prioridade(linha["prioridade"]),
            concluida=bool(linha["concluida"]),
            contato_id=linha["contato_id"],
            criado_em=linha["criado_em"],
        )

    @staticmethod
    def _valores(tarefa: Tarefa) -> tuple:
        return (
            tarefa.titulo,
            tarefa.descricao,
            tarefa.prazo.isoformat() if tarefa.prazo else None,
            tarefa.prioridade.value,
            int(tarefa.concluida),
            tarefa.contato_id,
        )

    def listar(self) -> list[Tarefa]:
        with self._banco.cursor() as cursor:
            cursor.execute("SELECT * FROM tarefas ORDER BY id")
            return [self._para_modelo(l) for l in cursor.fetchall()]

    def obter(self, item_id: int) -> Tarefa | None:
        with self._banco.cursor() as cursor:
            cursor.execute("SELECT * FROM tarefas WHERE id = ?", (item_id,))
            linha = cursor.fetchone()
            return self._para_modelo(linha) if linha else None

    def adicionar(self, tarefa: Tarefa) -> Tarefa:
        with self._banco.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tarefas (titulo, descricao, prazo, prioridade, concluida, "
                "contato_id, criado_em) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (*self._valores(tarefa), tarefa.criado_em),
            )
            tarefa.id = cursor.lastrowid
        return tarefa

    def atualizar(self, tarefa: Tarefa) -> Tarefa:
        with self._banco.cursor() as cursor:
            cursor.execute(
                "UPDATE tarefas SET titulo = ?, descricao = ?, prazo = ?, prioridade = ?, "
                "concluida = ?, contato_id = ? WHERE id = ?",
                (*self._valores(tarefa), tarefa.id),
            )
            if cursor.rowcount == 0:
                raise ErroNaoEncontrado(f"Registro #{tarefa.id} não encontrado.")
        return tarefa
