import sqlite3
from contextlib import closing
from typing import List, Optional
from src.models.coluna import Coluna

class ColunaRepository:
    def __init__(self, db_path: str = "database/kanban.db"):
        self.db_path = db_path

    def _conectar(self) -> sqlite3.Connection:
        conexao = sqlite3.connect(self.db_path)
        conexao.execute("PRAGMA foreign_keys = ON;") # Garante que ON DELETE CASCADE do Quadro funciona nas Colunas
        return conexao

    def criar(self, coluna: Coluna) -> int:
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute(
                    "INSERT INTO COLUNA (id_quadro, nome, limite_col) VALUES (?, ?, ?)",
                    (coluna.id_quadro, coluna.nome, coluna.limite_col)
                )
                return cursor.lastrowid

    def buscar_por_id(self, id_coluna: int) -> Optional[Coluna]:
        with closing(self._conectar()) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id_coluna, id_quadro, nome, limite_col FROM COLUNA WHERE id_coluna = ?", (id_coluna,))
            linha = cursor.fetchone()
            if linha:
                return Coluna(id_coluna=linha[0], id_quadro=linha[1], nome=linha[2], limite_col=linha[3])
            return None

    def listar_por_quadro(self, id_quadro: int) -> List[Coluna]:
        colunas = []
        with closing(self._conectar()) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id_coluna, id_quadro, nome, limite_col FROM COLUNA WHERE id_quadro = ?", (id_quadro,))
            for linha in cursor.fetchall():
                colunas.append(Coluna(id_coluna=linha[0], id_quadro=linha[1], nome=linha[2], limite_col=linha[3]))
        return colunas

    def atualizar(self, coluna: Coluna):
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute(
                    "UPDATE COLUNA SET nome = ?, limite_col = ? WHERE id_coluna = ?",
                    (coluna.nome, coluna.limite_col, coluna.id_coluna)
                )

    def deletar(self, id_coluna: int):
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute("DELETE FROM COLUNA WHERE id_coluna = ?", (id_coluna,))