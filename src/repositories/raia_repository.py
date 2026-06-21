import sqlite3
from contextlib import closing
from typing import List, Optional
from src.models.raia import Raia
import os
import sys

class RaiaRepository:
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

    def criar(self, raia: Raia) -> int:
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute(
                    "INSERT INTO RAIA (id_quadro, nome) VALUES (?, ?)",
                    (raia.id_quadro, raia.nome)
                )
                return cursor.lastrowid

    def buscar_por_id(self, id_raia: int) -> Optional[Raia]:
        with closing(self._conectar()) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id_raia, id_quadro, nome FROM RAIA WHERE id_raia = ?", (id_raia,))
            linha = cursor.fetchone()
            if linha:
                return Raia(id_raia=linha[0], id_quadro=linha[1], nome=linha[2])
            return None

    def listar_por_quadro(self, id_quadro: int) -> List[Raia]:
        raias = []
        with closing(self._conectar()) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id_raia, id_quadro, nome FROM RAIA WHERE id_quadro = ?", (id_quadro,))
            for linha in cursor.fetchall():
                raias.append(Raia(id_raia=linha[0], id_quadro=linha[1], nome=linha[2]))
        return raias

    def atualizar(self, raia: Raia):
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute(
                    "UPDATE RAIA SET nome = ? WHERE id_raia = ?",
                    (raia.nome, raia.id_raia)
                )

    def deletar(self, id_raia: int):
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute("DELETE FROM RAIA WHERE id_raia = ?", (id_raia,))
