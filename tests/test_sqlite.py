"""Roda a mesma suíte de serviços sobre o SQLite (sempre habilitado: usa só a biblioteca padrão)."""
import unittest
from datetime import date

from agenda.exceptions import ErroDeArmazenamento
from agenda.models import Tarefa
from agenda.sqlite_database import BancoSQLite
from agenda.sqlite_repository import ContatoSQLiteRepository, TarefaSQLiteRepository
from tests import test_services as base


class SQLiteMixin:
    def criar_repos(self):
        self.banco = BancoSQLite(self.pasta / "agenda.db")
        self.banco.criar_esquema()
        return ContatoSQLiteRepository(self.banco), TarefaSQLiteRepository(self.banco)


class TestContatosSQLite(SQLiteMixin, base.TestContatos):
    pass


class TestTarefasSQLite(SQLiteMixin, base.TestTarefas):
    pass


class TestEspecificosSQLite(SQLiteMixin, base.BaseTeste):
    def test_dados_persistem_em_nova_conexao(self):
        self.contatos.criar("Ana")
        self.tarefas.criar("Estudar", prazo=date(2030, 5, 1))
        outro = BancoSQLite(self.pasta / "agenda.db")
        self.assertEqual(ContatoSQLiteRepository(outro).listar()[0].nome, "Ana")
        self.assertEqual(TarefaSQLiteRepository(outro).listar()[0].prazo, date(2030, 5, 1))

    def test_esquema_pode_ser_criado_duas_vezes(self):
        self.contatos.criar("Ana")
        self.banco.criar_esquema()
        self.assertEqual(len(self.contatos.listar()), 1)

    def test_chave_estrangeira_e_respeitada(self):
        with self.assertRaises(ErroDeArmazenamento):
            self.repo_tarefas.adicionar(Tarefa(titulo="órfã", contato_id=999))

    def test_acentos_sao_preservados(self):
        self.contatos.criar("José Conceição")
        self.assertEqual(self.contatos.listar()[0].nome, "José Conceição")


if __name__ == "__main__":
    unittest.main()
