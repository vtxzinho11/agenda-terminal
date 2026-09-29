import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from agenda.exceptions import ErroDeArmazenamento, ErroDeValidacao, ErroNaoEncontrado
from agenda.models import Contato, Prioridade, Tarefa
from agenda.repository import JsonRepository
from agenda.services import ContatoService, FiltroTarefas, TarefaService


class BaseTeste(unittest.TestCase):
    """Cria os serviços sobre um backend. Subclasses trocam o backend sobrescrevendo criar_repos()."""

    def criar_repos(self):
        return (
            JsonRepository(self.pasta / "contatos.json", Contato),
            JsonRepository(self.pasta / "tarefas.json", Tarefa),
        )

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.pasta = Path(self._tmp.name)
        self.repo_contatos, self.repo_tarefas = self.criar_repos()
        self.contatos = ContatoService(self.repo_contatos, self.repo_tarefas)
        self.tarefas = TarefaService(self.repo_tarefas, self.repo_contatos)


class TestContatos(BaseTeste):
    def test_crud_completo(self):
        c = self.contatos.criar("Maria Silva", "(11) 91234-5678", "MARIA@x.com")
        self.assertEqual(c.id, 1)
        self.assertEqual(c.telefone, "11912345678")
        self.assertEqual(c.email, "maria@x.com")

        self.contatos.atualizar(c.id, "Maria S.", "", "")
        self.assertEqual(self.contatos.obter(c.id).nome, "Maria S.")

        self.contatos.remover(c.id)
        with self.assertRaises(ErroNaoEncontrado):
            self.contatos.obter(c.id)

    def test_validacoes(self):
        with self.assertRaises(ErroDeValidacao):
            self.contatos.criar("A")
        with self.assertRaises(ErroDeValidacao):
            self.contatos.criar("João", email="invalido")
        with self.assertRaises(ErroDeValidacao):
            self.contatos.criar("João", telefone="123")

    def test_busca_por_nome_e_telefone(self):
        self.contatos.criar("Ana", "11 99999-0000")
        self.contatos.criar("Bruno", "21 98888-1111")
        self.assertEqual([c.nome for c in self.contatos.listar("bru")], ["Bruno"])
        self.assertEqual([c.nome for c in self.contatos.listar("99999")], ["Ana"])

    def test_remover_contato_desvincula_tarefas(self):
        c = self.contatos.criar("Ana")
        t = self.tarefas.criar("Ligar", contato_id=c.id)
        self.assertEqual(self.contatos.remover(c.id), 1)
        self.assertIsNone(self.tarefas.obter(t.id).contato_id)


class TestTarefas(BaseTeste):
    def test_crud_completo(self):
        t = self.tarefas.criar("Estudar", prazo=date(2030, 1, 1), prioridade=Prioridade.ALTA)
        self.assertEqual(self.tarefas.obter(t.id).prazo, date(2030, 1, 1))

        self.tarefas.atualizar(t.id, "Estudar Python", "", None, Prioridade.BAIXA, None)
        atualizada = self.tarefas.obter(t.id)
        self.assertEqual(atualizada.titulo, "Estudar Python")
        self.assertIsNone(atualizada.prazo)

        self.assertTrue(self.tarefas.alternar_conclusao(t.id).concluida)
        self.assertFalse(self.tarefas.alternar_conclusao(t.id).concluida)

        self.tarefas.remover(t.id)
        with self.assertRaises(ErroNaoEncontrado):
            self.tarefas.obter(t.id)

    def test_titulo_obrigatorio(self):
        with self.assertRaises(ErroDeValidacao):
            self.tarefas.criar("   ")

    def test_contato_inexistente(self):
        with self.assertRaises(ErroNaoEncontrado):
            self.tarefas.criar("Ligar", contato_id=99)

    def test_filtros_e_ordenacao(self):
        a = self.tarefas.criar("A", prazo=date.today() + timedelta(days=5))
        b = self.tarefas.criar("B", prazo=date.today() + timedelta(days=1))
        c = self.tarefas.criar("C")
        self.tarefas.alternar_conclusao(c.id)
        self.assertEqual([t.titulo for t in self.tarefas.listar(FiltroTarefas.PENDENTES)], ["B", "A"])
        self.assertEqual([t.titulo for t in self.tarefas.listar(FiltroTarefas.CONCLUIDAS)], ["C"])
        self.assertEqual([t.id for t in self.tarefas.agenda()], [b.id, a.id])


class TestPersistencia(BaseTeste):
    def test_dados_sobrevivem_a_nova_instancia(self):
        self.contatos.criar("Ana")
        novo_repo = JsonRepository(self.pasta / "contatos.json", Contato)
        self.assertEqual(novo_repo.listar()[0].nome, "Ana")

    def test_arquivo_corrompido(self):
        (self.pasta / "contatos.json").write_text("{quebrado", encoding="utf-8")
        with self.assertRaises(ErroDeArmazenamento):
            self.contatos.listar()


if __name__ == "__main__":
    unittest.main()
