"""Interface de linha de comando: só conversa com o usuário e delega aos serviços."""
from __future__ import annotations

from datetime import date

from . import ui
from .config import (
    obter_caminho_sqlite,
    obter_config_mysql,
    obter_diretorio_dados,
    obter_tipo_armazenamento,
)
from .exceptions import ErroDeArmazenamento
from .models import Contato, Tarefa
from .repository import JsonRepository, Repositorio
from .services import ContatoService, FiltroTarefas, TarefaService
from .validators import parse_data, parse_inteiro_opcional


class App:
    def __init__(self, contatos: ContatoService, tarefas: TarefaService) -> None:
        self._contatos = contatos
        self._tarefas = tarefas

    def executar(self) -> None:
        ui.executar_menu(
            "AGENDA & TO-DO",
            {
                "1": ("Tarefas", self._menu_tarefas),
                "2": ("Contatos", self._menu_contatos),
                "3": ("Agenda (compromissos com prazo)", self._mostrar_agenda),
            },
            rotulo_saida="Sair",
        )
        print("Até logo!")

    # ------------------------------------------------------------------ tarefas
    def _menu_tarefas(self) -> None:
        ui.executar_menu(
            "TAREFAS",
            {
                "1": ("Listar todas", lambda: self._listar_tarefas(FiltroTarefas.TODAS)),
                "2": ("Listar pendentes", lambda: self._listar_tarefas(FiltroTarefas.PENDENTES)),
                "3": ("Listar concluídas", lambda: self._listar_tarefas(FiltroTarefas.CONCLUIDAS)),
                "4": ("Adicionar", self._adicionar_tarefa),
                "5": ("Editar", self._editar_tarefa),
                "6": ("Concluir / reabrir", self._alternar_tarefa),
                "7": ("Remover", self._remover_tarefa),
            },
        )

    def _nomes_contatos(self) -> dict[int, str]:
        return {c.id: c.nome for c in self._contatos.listar()}

    @staticmethod
    def _linha_tarefa(tarefa: Tarefa, nomes: dict[int, str]) -> str:
        marca = "[x]" if tarefa.concluida else "[ ]"
        partes = [f"{marca} #{tarefa.id} {tarefa.titulo}"]
        if tarefa.prazo:
            aviso = " (ATRASADA)" if tarefa.atrasada else ""
            partes.append(f"prazo {ui.formatar_data(tarefa.prazo)}{aviso}")
        partes.append(f"prioridade {tarefa.prioridade.value}")
        if tarefa.contato_id is not None:
            partes.append(f"contato: {nomes.get(tarefa.contato_id, '?')}")
        linha = " | ".join(partes)
        if tarefa.descricao:
            linha += f"\n      {tarefa.descricao}"
        return linha

    def _listar_tarefas(self, filtro: FiltroTarefas) -> None:
        tarefas = self._tarefas.listar(filtro)
        if not tarefas:
            print(f"Nenhuma tarefa ({filtro.value}).")
            return
        nomes = self._nomes_contatos()
        print()
        for tarefa in tarefas:
            print(self._linha_tarefa(tarefa, nomes))

    def _adicionar_tarefa(self) -> None:
        titulo = ui.ler_texto("Título", obrigatorio=True)
        descricao = ui.ler_texto("Descrição (opcional)")
        prazo = parse_data(ui.ler_texto("Prazo dd/mm/aaaa (opcional)"))
        prioridade = ui.escolher_prioridade()
        contato_id = parse_inteiro_opcional(ui.ler_texto("ID do contato (opcional)"))
        tarefa = self._tarefas.criar(titulo, descricao, prazo, prioridade, contato_id)
        print(f"Tarefa #{tarefa.id} criada.")

    def _editar_tarefa(self) -> None:
        tarefa = self._tarefas.obter(ui.ler_inteiro("ID da tarefa"))
        titulo = ui.ler_edicao("Título", tarefa.titulo)
        descricao = ui.ler_edicao("Descrição", tarefa.descricao)
        prazo = parse_data(ui.ler_edicao("Prazo dd/mm/aaaa", ui.formatar_data(tarefa.prazo)))
        prioridade = ui.escolher_prioridade(tarefa.prioridade)
        contato_id = parse_inteiro_opcional(
            ui.ler_edicao("ID do contato", str(tarefa.contato_id or ""))
        )
        self._tarefas.atualizar(tarefa.id, titulo, descricao, prazo, prioridade, contato_id)
        print("Tarefa atualizada.")

    def _alternar_tarefa(self) -> None:
        tarefa = self._tarefas.alternar_conclusao(ui.ler_inteiro("ID da tarefa"))
        print("Tarefa concluída." if tarefa.concluida else "Tarefa reaberta.")

    def _remover_tarefa(self) -> None:
        tarefa = self._tarefas.obter(ui.ler_inteiro("ID da tarefa"))
        if ui.confirmar(f"Remover '{tarefa.titulo}'?"):
            self._tarefas.remover(tarefa.id)
            print("Tarefa removida.")

    # ------------------------------------------------------------------ contatos
    def _menu_contatos(self) -> None:
        ui.executar_menu(
            "CONTATOS",
            {
                "1": ("Listar", self._listar_contatos),
                "2": ("Buscar", self._buscar_contatos),
                "3": ("Adicionar", self._adicionar_contato),
                "4": ("Editar", self._editar_contato),
                "5": ("Remover", self._remover_contato),
            },
        )

    @staticmethod
    def _linha_contato(contato: Contato) -> str:
        partes = [f"#{contato.id} {contato.nome}"]
        if contato.telefone:
            partes.append(ui.formatar_telefone(contato.telefone))
        if contato.email:
            partes.append(contato.email)
        return " | ".join(partes)

    def _exibir_contatos(self, contatos: list[Contato]) -> None:
        if not contatos:
            print("Nenhum contato encontrado.")
            return
        print()
        for contato in contatos:
            print(self._linha_contato(contato))

    def _listar_contatos(self) -> None:
        self._exibir_contatos(self._contatos.listar())

    def _buscar_contatos(self) -> None:
        termo = ui.ler_texto("Buscar por nome, telefone ou e-mail", obrigatorio=True)
        self._exibir_contatos(self._contatos.listar(termo))

    def _adicionar_contato(self) -> None:
        nome = ui.ler_texto("Nome", obrigatorio=True)
        telefone = ui.ler_texto("Telefone (opcional)")
        email = ui.ler_texto("E-mail (opcional)")
        contato = self._contatos.criar(nome, telefone, email)
        print(f"Contato #{contato.id} criado.")

    def _editar_contato(self) -> None:
        contato = self._contatos.obter(ui.ler_inteiro("ID do contato"))
        nome = ui.ler_edicao("Nome", contato.nome)
        telefone = ui.ler_edicao("Telefone", ui.formatar_telefone(contato.telefone))
        email = ui.ler_edicao("E-mail", contato.email)
        self._contatos.atualizar(contato.id, nome, telefone, email)
        print("Contato atualizado.")

    def _remover_contato(self) -> None:
        contato = self._contatos.obter(ui.ler_inteiro("ID do contato"))
        if ui.confirmar(f"Remover '{contato.nome}'?"):
            desvinculadas = self._contatos.remover(contato.id)
            print("Contato removido.")
            if desvinculadas:
                print(f"{desvinculadas} tarefa(s) ficaram sem contato vinculado.")

    # ------------------------------------------------------------------ agenda
    def _mostrar_agenda(self) -> None:
        tarefas = self._tarefas.agenda()
        if not tarefas:
            print("Nenhum compromisso pendente com prazo.")
            return
        hoje = date.today()
        nomes = self._nomes_contatos()
        grupos = (
            ("Atrasadas", [t for t in tarefas if t.prazo < hoje]),
            ("Hoje", [t for t in tarefas if t.prazo == hoje]),
            ("Próximas", [t for t in tarefas if t.prazo > hoje]),
        )
        for nome_grupo, itens in grupos:
            if itens:
                print(f"\n-- {nome_grupo} --")
                for tarefa in itens:
                    print(self._linha_tarefa(tarefa, nomes))


def _criar_repositorios() -> tuple[Repositorio[Contato], Repositorio[Tarefa]]:
    tipo = obter_tipo_armazenamento()
    if tipo == "sqlite":
        from .sqlite_database import BancoSQLite
        from .sqlite_repository import ContatoSQLiteRepository, TarefaSQLiteRepository

        banco_sqlite = BancoSQLite(obter_caminho_sqlite())
        banco_sqlite.criar_esquema()
        return ContatoSQLiteRepository(banco_sqlite), TarefaSQLiteRepository(banco_sqlite)
    if tipo == "mysql":
        # Importação tardia: o driver só é exigido quando o MySQL é usado.
        from .mysql_database import BancoMySQL
        from .mysql_repository import ContatoMySQLRepository, TarefaMySQLRepository

        banco = BancoMySQL(obter_config_mysql())
        banco.criar_esquema()
        return ContatoMySQLRepository(banco), TarefaMySQLRepository(banco)
    if tipo == "json":
        pasta = obter_diretorio_dados()
        return (
            JsonRepository(pasta / "contatos.json", Contato),
            JsonRepository(pasta / "tarefas.json", Tarefa),
        )
    raise ErroDeArmazenamento(f"AGENDA_STORAGE inválido: '{tipo}' (use 'sqlite', 'mysql' ou 'json').")


def criar_app() -> App:
    """Composição das dependências (único lugar que conhece as classes concretas)."""
    repo_contatos, repo_tarefas = _criar_repositorios()
    return App(
        ContatoService(repo_contatos, repo_tarefas),
        TarefaService(repo_tarefas, repo_contatos),
    )


def main() -> int:
    try:
        criar_app().executar()
    except (KeyboardInterrupt, EOFError):
        print("\nAté logo!")
    except ErroDeArmazenamento as erro:
        print(f"Erro fatal: {erro}")
        return 1
    return 0
