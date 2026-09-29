"""Roda a mesma suíte de serviços contra um MySQL real.

Só executa se AGENDA_TEST_MYSQL=1. Usa um banco separado (padrão: agenda_test)
e APAGA as tabelas dele a cada teste. Conexão via MYSQL_HOST/PORT/USER/PASSWORD.
"""
import os
import unittest
from dataclasses import replace

from tests import test_services as base

HABILITADO = os.environ.get("AGENDA_TEST_MYSQL") == "1"


@unittest.skipUnless(HABILITADO, "defina AGENDA_TEST_MYSQL=1 para testar com MySQL")
class MySQLMixin:
    def criar_repos(self):
        from agenda.config import obter_config_mysql
        from agenda.mysql_database import BancoMySQL
        from agenda.mysql_repository import ContatoMySQLRepository, TarefaMySQLRepository

        config = replace(obter_config_mysql(), database=os.environ.get("MYSQL_TEST_DATABASE", "agenda_test"))
        banco = BancoMySQL(config)
        banco.criar_esquema()
        banco.apagar_tabelas()
        banco.criar_esquema()
        return ContatoMySQLRepository(banco), TarefaMySQLRepository(banco)


class TestContatosMySQL(MySQLMixin, base.TestContatos):
    pass


class TestTarefasMySQL(MySQLMixin, base.TestTarefas):
    pass


if __name__ == "__main__":
    unittest.main()
