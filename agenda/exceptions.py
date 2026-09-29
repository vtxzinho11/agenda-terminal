"""Exceções do domínio: permitem à interface tratar erros sem conhecer detalhes internos."""


class ErroDeAgenda(Exception):
    """Classe base de todos os erros esperados da aplicação."""


class ErroDeValidacao(ErroDeAgenda):
    """Dados informados pelo usuário são inválidos."""


class ErroNaoEncontrado(ErroDeAgenda):
    """O registro solicitado não existe."""


class ErroDeArmazenamento(ErroDeAgenda):
    """Falha ao ler ou gravar os dados em disco."""
