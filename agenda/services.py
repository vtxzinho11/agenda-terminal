"""Regras de negócio. Não sabem nada sobre terminal nem sobre JSON."""
from __future__ import annotations

import re
from datetime import date
from enum import Enum

from .exceptions import ErroNaoEncontrado
from .models import Contato, Prioridade, Tarefa
from .repository import Repositorio
from .validators import validar_email, validar_nome, validar_telefone, validar_titulo


class FiltroTarefas(str, Enum):
    TODAS = "todas"
    PENDENTES = "pendentes"
    CONCLUIDAS = "concluídas"


class ContatoService:
    def __init__(
        self, contatos: Repositorio[Contato], tarefas: Repositorio[Tarefa]
    ) -> None:
        self._contatos = contatos
        self._tarefas = tarefas

    def criar(self, nome: str, telefone: str = "", email: str = "") -> Contato:
        contato = Contato(
            nome=validar_nome(nome),
            telefone=validar_telefone(telefone),
            email=validar_email(email),
        )
        return self._contatos.adicionar(contato)

    def obter(self, contato_id: int) -> Contato:
        contato = self._contatos.obter(contato_id)
        if contato is None:
            raise ErroNaoEncontrado(f"Contato #{contato_id} não encontrado.")
        return contato

    def listar(self, busca: str = "") -> list[Contato]:
        contatos = sorted(self._contatos.listar(), key=lambda c: c.nome.lower())
        termo = busca.strip().lower()
        if not termo:
            return contatos
        digitos = re.sub(r"\D", "", termo)
        return [
            c
            for c in contatos
            if termo in c.nome.lower()
            or termo in c.email
            or (digitos and digitos in c.telefone)
        ]

    def atualizar(self, contato_id: int, nome: str, telefone: str, email: str) -> Contato:
        contato = self.obter(contato_id)
        contato.nome = validar_nome(nome)
        contato.telefone = validar_telefone(telefone)
        contato.email = validar_email(email)
        return self._contatos.atualizar(contato)

    def remover(self, contato_id: int) -> int:
        """Remove o contato e desvincula suas tarefas. Retorna quantas foram desvinculadas."""
        self.obter(contato_id)
        vinculadas = [t for t in self._tarefas.listar() if t.contato_id == contato_id]
        for tarefa in vinculadas:
            tarefa.contato_id = None
            self._tarefas.atualizar(tarefa)
        self._contatos.remover(contato_id)
        return len(vinculadas)


class TarefaService:
    def __init__(
        self, tarefas: Repositorio[Tarefa], contatos: Repositorio[Contato]
    ) -> None:
        self._tarefas = tarefas
        self._contatos = contatos

    def _verificar_contato(self, contato_id: int | None) -> None:
        if contato_id is not None and self._contatos.obter(contato_id) is None:
            raise ErroNaoEncontrado(f"Contato #{contato_id} não existe.")

    def criar(
        self,
        titulo: str,
        descricao: str = "",
        prazo: date | None = None,
        prioridade: Prioridade = Prioridade.MEDIA,
        contato_id: int | None = None,
    ) -> Tarefa:
        self._verificar_contato(contato_id)
        tarefa = Tarefa(
            titulo=validar_titulo(titulo),
            descricao=descricao.strip(),
            prazo=prazo,
            prioridade=prioridade,
            contato_id=contato_id,
        )
        return self._tarefas.adicionar(tarefa)

    def obter(self, tarefa_id: int) -> Tarefa:
        tarefa = self._tarefas.obter(tarefa_id)
        if tarefa is None:
            raise ErroNaoEncontrado(f"Tarefa #{tarefa_id} não encontrada.")
        return tarefa

    def listar(self, filtro: FiltroTarefas = FiltroTarefas.TODAS) -> list[Tarefa]:
        tarefas = self._tarefas.listar()
        if filtro is FiltroTarefas.PENDENTES:
            tarefas = [t for t in tarefas if not t.concluida]
        elif filtro is FiltroTarefas.CONCLUIDAS:
            tarefas = [t for t in tarefas if t.concluida]
        return sorted(
            tarefas,
            key=lambda t: (t.concluida, t.prazo or date.max, -t.prioridade.peso, t.id),
        )

    def agenda(self) -> list[Tarefa]:
        """Tarefas pendentes que têm prazo, em ordem cronológica."""
        return sorted(
            (t for t in self._tarefas.listar() if not t.concluida and t.prazo),
            key=lambda t: (t.prazo, -t.prioridade.peso),
        )

    def atualizar(
        self,
        tarefa_id: int,
        titulo: str,
        descricao: str,
        prazo: date | None,
        prioridade: Prioridade,
        contato_id: int | None,
    ) -> Tarefa:
        tarefa = self.obter(tarefa_id)
        self._verificar_contato(contato_id)
        tarefa.titulo = validar_titulo(titulo)
        tarefa.descricao = descricao.strip()
        tarefa.prazo = prazo
        tarefa.prioridade = prioridade
        tarefa.contato_id = contato_id
        return self._tarefas.atualizar(tarefa)

    def alternar_conclusao(self, tarefa_id: int) -> Tarefa:
        tarefa = self.obter(tarefa_id)
        tarefa.concluida = not tarefa.concluida
        return self._tarefas.atualizar(tarefa)

    def remover(self, tarefa_id: int) -> None:
        self.obter(tarefa_id)
        self._tarefas.remover(tarefa_id)
