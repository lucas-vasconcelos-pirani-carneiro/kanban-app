import sqlite3
from contextlib import closing
from typing import List, Optional
from src.models.projeto import Projeto
import os
import sys

class ProjetoRepository:
    def __init__(self, db_path: str = None):
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            base_path = os.path.abspath(os.path.join(base_path, '..', '..'))

        if db_path is None:
            self.db_path = os.path.join(base_path, "database", "kanban.db")
        else:
            self.db_path = db_path

    def _conectar(self) -> sqlite3.Connection:
        conexao = sqlite3.connect(self.db_path)
        conexao.execute("PRAGMA foreign_keys = ON;")
        return conexao

    def criar(self, projeto: Projeto, id_user_criador: int) -> int:
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                
                
                cursor.execute(
                    "INSERT INTO PROJETO (nome, descricao, data_criacao) VALUES (?, ?, ?)",
                    (projeto.nome, projeto.descricao, projeto.data_criacao)
                )
                novo_id_proj = cursor.lastrowid
                
                cursor.execute(
                    "INSERT INTO MEMBRO_PROJETO (id_user, id_proj, gerente) VALUES (?, ?, 1)",
                    (id_user_criador, novo_id_proj)
                )
                
                return novo_id_proj

    def buscar_por_id(self, id_proj: int) -> Optional[Projeto]:
        with closing(self._conectar()) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id_proj, nome, descricao, data_criacao FROM PROJETO WHERE id_proj = ?", (id_proj,))
            linha = cursor.fetchone()
            if linha:
                return Projeto(id_proj=linha[0], nome=linha[1], descricao=linha[2], data_criacao=linha[3])
            return None

    def listar_todos(self) -> List[Projeto]:
        """Devolve todos os projetos registados no sistema."""
        projetos = []
        with closing(self._conectar()) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id_proj, nome, descricao, data_criacao FROM PROJETO ORDER BY id_proj DESC")
            for linha in cursor.fetchall():
                projetos.append(Projeto(id_proj=linha[0], nome=linha[1], descricao=linha[2], data_criacao=linha[3]))
        return projetos

    def atualizar(self, projeto: Projeto):
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute(
                    "UPDATE PROJETO SET nome = ?, descricao = ? WHERE id_proj = ?",
                    (projeto.nome, projeto.descricao, projeto.id_proj)
                )

    def deletar(self, id_proj: int):
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                # Deleta cartões dentro das colunas dos quadros do projeto
                cursor.execute("""
                    DELETE FROM CARTAO WHERE id_coluna IN (
                        SELECT id_coluna FROM COLUNA WHERE id_quadro IN (
                            SELECT id_quadro FROM QUADRO WHERE id_proj = ?
                        )
                    )
                """, (id_proj,))
                # Deleta colunas dos quadros do projeto
                cursor.execute("""
                    DELETE FROM COLUNA WHERE id_quadro IN (
                        SELECT id_quadro FROM QUADRO WHERE id_proj = ?
                    )
                """, (id_proj,))
                # Deleta quadros do projeto
                cursor.execute("DELETE FROM QUADRO WHERE id_proj = ?", (id_proj,))
                # Deleta membros do projeto
                cursor.execute("DELETE FROM MEMBRO_PROJETO WHERE id_proj = ?", (id_proj,))
                # Deleta o projeto
                cursor.execute("DELETE FROM PROJETO WHERE id_proj = ?", (id_proj,))
