import sqlite3
from contextlib import closing
from typing import List, Optional
from src.models.cartao import Cartao
import os
import sys # Importe sys

class CartaoRepository:
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

    def criar(self, cartao: Cartao) -> int:
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute(
                    """INSERT INTO CARTAO (id_coluna, id_raia, id_user_responsavel, nome, 
                       descricao, prioridade, data_limite, data_criacao) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (cartao.id_coluna, cartao.id_raia, cartao.id_user_responsavel, cartao.nome,
                     cartao.descricao, cartao.prioridade, cartao.data_limite, cartao.data_criacao)
                )
                return cursor.lastrowid

    def contar_por_coluna(self, id_coluna: int) -> int:
        """Conta quantos cartões ativos existem numa coluna específica para validar o WIP."""
        with closing(self._conectar()) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT COUNT(*) FROM CARTAO WHERE id_coluna = ?", (id_coluna,))
            return cursor.fetchone()[0]

    def buscar_por_id(self, id_cartao: int) -> Optional[Cartao]:
        with closing(self._conectar()) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM CARTAO WHERE id_cartao = ?", (id_cartao,))
            linha = cursor.fetchone()
            if linha:
                return Cartao(*linha)
            return None

    def listar_por_coluna(self, id_coluna: int) -> List[Cartao]:
        cartoes = []
        with closing(self._conectar()) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM CARTAO WHERE id_coluna = ?", (id_coluna,))
            for linha in cursor.fetchall():
                cartoes.append(Cartao(*linha))
        return cartoes

    def atualizar(self, cartao: Cartao):
            with closing(self._conectar()) as conexao:
                with conexao:
                    cursor = conexao.cursor()
                    cursor.execute(
                        """UPDATE CARTAO SET id_coluna = ?, id_raia = ?, id_user_responsavel = ?, 
                        nome = ?, descricao = ?, prioridade = ?, data_limite = ?, 
                        data_criacao = ?, data_entrada_wip = ?, data_conclusao = ? WHERE id_cartao = ?""",
                        (cartao.id_coluna, cartao.id_raia, cartao.id_user_responsavel, cartao.nome,
                        cartao.descricao, cartao.prioridade, cartao.data_limite, 
                        cartao.data_criacao, cartao.data_entrada_wip, cartao.data_conclusao, cartao.id_cartao)
                    )

    def deletar(self, id_cartao: int):
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute("DELETE FROM CARTAO WHERE id_cartao = ?", (id_cartao,))
    
    def listar_por_coluna_e_raia(self, id_coluna: int, id_raia: Optional[int]) -> List[Cartao]:
        cartoes = []
        with closing(self._conectar()) as conexao:
            cursor = conexao.cursor()
            if id_raia is None:
                cursor.execute(
                    "SELECT * FROM CARTAO WHERE id_coluna = ? AND id_raia IS NULL",
                    (id_coluna,)
                )
            else:
                cursor.execute(
                    "SELECT * FROM CARTAO WHERE id_coluna = ? AND id_raia = ?",
                    (id_coluna, id_raia)
                )
            for linha in cursor.fetchall():
                cartoes.append(Cartao(*linha))
        return cartoes
    

    def listar_concluidos_por_projeto(self, id_proj: int) -> List[Cartao]:
        """Busca todos os cartões concluídos pertencentes a um projeto (via colunas e quadros)."""
        cartoes = []
        with closing(self._conectar()) as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT C.* FROM CARTAO C
                JOIN COLUNA COL ON C.id_coluna = COL.id_coluna
                JOIN QUADRO Q ON COL.id_quadro = Q.id_quadro
                WHERE Q.id_proj = ? AND C.data_conclusao IS NOT NULL
            """, (id_proj,))
            for linha in cursor.fetchall():
                cartoes.append(Cartao(*linha))
        return cartoes
