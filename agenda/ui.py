"""Funções de entrada e saída do terminal, reutilizadas pelos menus."""
from __future__ import annotations

try:
    import readline  # noqa: F401  (ativa setas, histórico e edição de linha no input())
except ImportError:  # ex.: Windows, onde o módulo não existe
    pass

from collections.abc import Callable
from datetime import date

from .exceptions import ErroDeAgenda
from .models import Prioridade
from .validators import FORMATO_DATA

Opcoes = dict[str, tuple[str, Callable[[], None]]]


def executar_menu(titulo: str, opcoes: Opcoes, rotulo_saida: str = "Voltar") -> None:
    """Exibe o menu em loop e trata os erros esperados sem derrubar o programa."""
    while True:
        print(f"\n=== {titulo} ===")
        for chave, (rotulo, _) in opcoes.items():
            print(f"  {chave}) {rotulo}")
        print(f"  0) {rotulo_saida}")
        escolha = input("Escolha: ").strip()
        if escolha == "0":
            return
        if escolha not in opcoes:
            print("Opção inválida.")
            continue
        try:
            opcoes[escolha][1]()
        except ErroDeAgenda as erro:
            print(f"Erro: {erro}")


def ler_texto(mensagem: str, *, obrigatorio: bool = False) -> str:
    while True:
        valor = input(f"{mensagem}: ").strip()
        if valor or not obrigatorio:
            return valor
        print("Campo obrigatório.")


def ler_edicao(mensagem: str, atual: str) -> str:
    """Enter mantém o valor atual; '-' limpa o campo."""
    valor = input(f"{mensagem} [{atual or 'vazio'}] (Enter mantém, '-' limpa): ").strip()
    if valor == "-":
        return ""
    return valor or atual


def ler_inteiro(mensagem: str) -> int:
    while True:
        valor = input(f"{mensagem}: ").strip()
        if valor.isdigit():
            return int(valor)
        print("Digite um número inteiro.")


def confirmar(mensagem: str) -> bool:
    return input(f"{mensagem} (s/N): ").strip().lower() in {"s", "sim"}


def escolher_prioridade(atual: Prioridade = Prioridade.MEDIA) -> Prioridade:
    opcoes = list(Prioridade)
    print("Prioridade: " + "  ".join(f"{i}) {p.value}" for i, p in enumerate(opcoes, 1)))
    while True:
        valor = input(f"Escolha [{atual.value}]: ").strip()
        if not valor:
            return atual
        if valor.isdigit() and 1 <= int(valor) <= len(opcoes):
            return opcoes[int(valor) - 1]
        print("Opção inválida.")


def formatar_data(data: date | None) -> str:
    return data.strftime(FORMATO_DATA) if data else ""


def formatar_telefone(digitos: str) -> str:
    if len(digitos) == 11:
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
    if len(digitos) == 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    return digitos
