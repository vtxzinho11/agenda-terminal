"""Repositórios MySQL: mesma interface do JsonRepository (listar/obter/adicionar/atualizar/remover)."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from .mysql_database import BancoMySQL
from .exceptions import ErroNaoEncontrado
from .models import Contato, Prioridade, Tarefa


def _iso(valor: datetime | str) -> str:
    return valor.isoformat(timespec="seconds") if isinstance(valor, datetime) else str(valor)


class _BaseMySQL:
    _tabela = ""

    def __init__(self, banco: BancoMySQL) -> None:
        self._banco = banco

    def _existe(self, cursor, item_id: int) -> bool:
        cursor.execute(f"SELECT 1 FROM {self._tabela} WHERE id = %s", (item_id,))
        return cursor.fetchone() is not None

    def remover(self, item_id: int) -> bool:
        with self._banco.cursor() as cursor:
            cursor.execute(f"DELETE FROM {self._tabela} WHERE id = %s", (item_id,))
            return cursor.rowcount > 0


class ContatoMySQLRepository(_BaseMySQL):
    _tabela = "contatos"

    @staticmethod
    def _para_modelo(linha: dict[str, Any]) -> Contato:
        return Contato(
            id=linha["id"],
            nome=linha["nome"],
            telefone=linha["telefone"],
            email=linha["email"],
            criado_em=_iso(linha["criado_em"]),
        )

    def listar(self) -> list[Contato]:
        with self._banco.cursor() as cursor:
            cursor.execute("SELECT * FROM contatos ORDER BY id")
            return [self._para_modelo(l) for l in cursor.fetchall()]

    def obter(self, item_id: int) -> Contato | None:
        with self._banco.cursor() as cursor:
            cursor.execute("SELECT * FROM contatos WHERE id = %s", (item_id,))
            linha = cursor.fetchone()
            return self._para_modelo(linha) if linha else None

    def adicionar(self, contato: Contato) -> Contato:
        with self._banco.cursor() as cursor:
            cursor.execute(
                "INSERT INTO contatos (nome, telefone, email, criado_em) VALUES (%s, %s, %s, %s)",
                (contato.nome, contato.telefone, contato.email,
                 datetime.fromisoformat(contato.criado_em)),
            )
            contato.id = cursor.lastrowid
        return contato

    def atualizar(self, contato: Contato) -> Contato:
        with self._banco.cursor() as cursor:
            cursor.execute(
                "UPDATE contatos SET nome = %s, telefone = %s, email = %s WHERE id = %s",
                (contato.nome, contato.telefone, contato.email, contato.id),
            )
            if cursor.rowcount == 0 and not self._existe(cursor, contato.id):
                raise ErroNaoEncontrado(f"Registro #{contato.id} não encontrado.")
        return contato


class TarefaMySQLRepository(_BaseMySQL):
    _tabela = "tarefas"

    @staticmethod
    def _para_modelo(linha: dict[str, Any]) -> Tarefa:
        return Tarefa(
            id=linha["id"],
            titulo=linha["titulo"],
            descricao=linha["descricao"],
            prazo=linha["prazo"],
            prioridade=Prioridade(linha["prioridade"]),
            concluida=bool(linha["concluida"]),
            contato_id=linha["contato_id"],
            criado_em=_iso(linha["criado_em"]),
        )

    def listar(self) -> list[Tarefa]:
        with self._banco.cursor() as cursor:
            cursor.execute("SELECT * FROM tarefas ORDER BY id")
            return [self._para_modelo(l) for l in cursor.fetchall()]

    def obter(self, item_id: int) -> Tarefa | None:
        with self._banco.cursor() as cursor:
            cursor.execute("SELECT * FROM tarefas WHERE id = %s", (item_id,))
            linha = cursor.fetchone()
            return self._para_modelo(linha) if linha else None

    def adicionar(self, tarefa: Tarefa) -> Tarefa:
        with self._banco.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tarefas (titulo, descricao, prazo, prioridade, concluida, "
                "contato_id, criado_em) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (tarefa.titulo, tarefa.descricao, tarefa.prazo, tarefa.prioridade.value,
                 int(tarefa.concluida), tarefa.contato_id,
                 datetime.fromisoformat(tarefa.criado_em)),
            )
            tarefa.id = cursor.lastrowid
        return tarefa

    def atualizar(self, tarefa: Tarefa) -> Tarefa:
        with self._banco.cursor() as cursor:
            cursor.execute(
                "UPDATE tarefas SET titulo = %s, descricao = %s, prazo = %s, prioridade = %s, "
                "concluida = %s, contato_id = %s WHERE id = %s",
                (tarefa.titulo, tarefa.descricao, tarefa.prazo, tarefa.prioridade.value,
                 int(tarefa.concluida), tarefa.contato_id, tarefa.id),
            )
            if cursor.rowcount == 0 and not self._existe(cursor, tarefa.id):
                raise ErroNaoEncontrado(f"Registro #{tarefa.id} não encontrado.")
        return tarefa
