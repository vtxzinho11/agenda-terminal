"""Validação e normalização de dados de entrada."""
from __future__ import annotations

import re
from datetime import date, datetime

from .exceptions import ErroDeValidacao

FORMATO_DATA = "%d/%m/%Y"
_REGEX_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar_nome(nome: str) -> str:
    nome = nome.strip()
    if len(nome) < 2:
        raise ErroDeValidacao("O nome deve ter pelo menos 2 caracteres.")
    if len(nome) > 120:
        raise ErroDeValidacao("O nome deve ter no máximo 120 caracteres.")
    return nome


def validar_titulo(titulo: str) -> str:
    titulo = titulo.strip()
    if not titulo:
        raise ErroDeValidacao("O título da tarefa é obrigatório.")
    if len(titulo) > 200:
        raise ErroDeValidacao("O título deve ter no máximo 200 caracteres.")
    return titulo


def validar_telefone(telefone: str) -> str:
    """Retorna apenas os dígitos (vazio é permitido)."""
    if not telefone.strip():
        return ""
    digitos = re.sub(r"\D", "", telefone)
    if not 8 <= len(digitos) <= 13:
        raise ErroDeValidacao("Telefone inválido: informe de 8 a 13 dígitos.")
    return digitos


def validar_email(email: str) -> str:
    email = email.strip().lower()
    if email and (len(email) > 255 or not _REGEX_EMAIL.match(email)):
        raise ErroDeValidacao("E-mail inválido.")
    return email


def parse_data(texto: str) -> date | None:
    """Converte 'dd/mm/aaaa' em date. Texto vazio significa 'sem prazo'."""
    texto = texto.strip()
    if not texto:
        return None
    try:
        return datetime.strptime(texto, FORMATO_DATA).date()
    except ValueError:
        raise ErroDeValidacao("Data inválida. Use o formato dd/mm/aaaa.") from None


def parse_inteiro_opcional(texto: str) -> int | None:
    texto = texto.strip()
    if not texto:
        return None
    if not texto.isdigit():
        raise ErroDeValidacao("O ID deve ser um número inteiro.")
    return int(texto)
