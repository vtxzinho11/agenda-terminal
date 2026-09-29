"""Persistência em JSON, isolada do resto da aplicação.

Trocar por SQLite no futuro exige só uma nova classe com os mesmos métodos.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Generic, Protocol, TypeVar

from .exceptions import ErroDeArmazenamento, ErroNaoEncontrado


class Entidade(Protocol):
    id: int

    def to_dict(self) -> dict[str, Any]: ...

    @classmethod
    def from_dict(cls, dados: dict[str, Any]) -> Any: ...


T = TypeVar("T", bound=Entidade)


class Repositorio(Protocol[T]):
    """Contrato que os serviços esperam. JSON, MySQL ou qualquer outro backend o implementa."""

    def listar(self) -> list[T]: ...

    def obter(self, item_id: int) -> T | None: ...

    def adicionar(self, item: T) -> T: ...

    def atualizar(self, item: T) -> T: ...

    def remover(self, item_id: int) -> bool: ...


class JsonRepository(Generic[T]):
    """CRUD genérico sobre um arquivo JSON contendo uma lista de entidades."""

    def __init__(self, caminho: Path, modelo: type[T]) -> None:
        self._caminho = Path(caminho)
        self._modelo = modelo

    # ---------- leitura / escrita em disco ----------
    def _carregar(self) -> list[T]:
        if not self._caminho.exists():
            return []
        try:
            with self._caminho.open(encoding="utf-8") as arquivo:
                return [self._modelo.from_dict(item) for item in json.load(arquivo)]
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as erro:
            raise ErroDeArmazenamento(f"Arquivo corrompido: {self._caminho}") from erro
        except OSError as erro:
            raise ErroDeArmazenamento(f"Não foi possível ler {self._caminho}: {erro}") from erro

    def _salvar(self, itens: list[T]) -> None:
        temporario = self._caminho.with_suffix(".tmp")
        try:
            self._caminho.parent.mkdir(parents=True, exist_ok=True)
            with temporario.open("w", encoding="utf-8") as arquivo:
                json.dump([i.to_dict() for i in itens], arquivo, ensure_ascii=False, indent=2)
            os.replace(temporario, self._caminho)  # gravação atômica
        except OSError as erro:
            raise ErroDeArmazenamento(f"Não foi possível gravar {self._caminho}: {erro}") from erro

    # ---------- CRUD ----------
    def listar(self) -> list[T]:
        return self._carregar()

    def obter(self, item_id: int) -> T | None:
        return next((i for i in self._carregar() if i.id == item_id), None)

    def adicionar(self, item: T) -> T:
        itens = self._carregar()
        item.id = max((i.id for i in itens), default=0) + 1
        itens.append(item)
        self._salvar(itens)
        return item

    def atualizar(self, item: T) -> T:
        itens = self._carregar()
        for posicao, atual in enumerate(itens):
            if atual.id == item.id:
                itens[posicao] = item
                self._salvar(itens)
                return item
        raise ErroNaoEncontrado(f"Registro #{item.id} não encontrado.")

    def remover(self, item_id: int) -> bool:
        itens = self._carregar()
        restantes = [i for i in itens if i.id != item_id]
        if len(restantes) == len(itens):
            return False
        self._salvar(restantes)
        return True
