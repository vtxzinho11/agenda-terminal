"""Entidades do domínio (sem nenhuma lógica de tela ou de disco)."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any


class Prioridade(str, Enum):
    BAIXA = "baixa"
    MEDIA = "média"
    ALTA = "alta"

    @property
    def peso(self) -> int:
        return {"baixa": 1, "média": 2, "alta": 3}[self.value]


def _agora() -> str:
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class Contato:
    nome: str
    telefone: str = ""
    email: str = ""
    id: int = 0
    criado_em: str = field(default_factory=_agora)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, dados: dict[str, Any]) -> Contato:
        return cls(
            id=dados["id"],
            nome=dados["nome"],
            telefone=dados.get("telefone", ""),
            email=dados.get("email", ""),
            criado_em=dados.get("criado_em") or _agora(),
        )


@dataclass
class Tarefa:
    titulo: str
    descricao: str = ""
    prazo: date | None = None
    prioridade: Prioridade = Prioridade.MEDIA
    concluida: bool = False
    contato_id: int | None = None
    id: int = 0
    criado_em: str = field(default_factory=_agora)

    @property
    def atrasada(self) -> bool:
        return not self.concluida and self.prazo is not None and self.prazo < date.today()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "prazo": self.prazo.isoformat() if self.prazo else None,
            "prioridade": self.prioridade.value,
            "concluida": self.concluida,
            "contato_id": self.contato_id,
            "criado_em": self.criado_em,
        }

    @classmethod
    def from_dict(cls, dados: dict[str, Any]) -> Tarefa:
        prazo = dados.get("prazo")
        return cls(
            id=dados["id"],
            titulo=dados["titulo"],
            descricao=dados.get("descricao", ""),
            prazo=date.fromisoformat(prazo) if prazo else None,
            prioridade=Prioridade(dados.get("prioridade", Prioridade.MEDIA.value)),
            concluida=dados.get("concluida", False),
            contato_id=dados.get("contato_id"),
            criado_em=dados.get("criado_em") or _agora(),
        )
