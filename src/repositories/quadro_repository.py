import sqlite3
from contextlib import closing
from typing import List, Optional
from src.models.quadro import Quadro

class QuadroRepository:
    def __init__(self, db_path: str = "database/kanban.db"):
        self.db_path = db_path

    def _conectar(self) -> sqlite3.Connection:
        conexao = sqlite3.connect(self.db_path)
        conexao.execute("PRAGMA foreign_keys = ON;") # Garante o Cascade
        return conexao

    def criar(self, quadro: Quadro) -> int:
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute(
                    "INSERT INTO QUADRO (id_proj, nome) VALUES (?, ?)",
                    (quadro.id_proj, quadro.nome)
                )
                return cursor.lastrowid

    def buscar_por_id(self, id_quadro: int) -> Optional[Quadro]:
        with closing(self._conectar()) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id_quadro, id_proj, nome FROM QUADRO WHERE id_quadro = ?", (id_quadro,))
            linha = cursor.fetchone()
            if linha:
                return Quadro(id_quadro=linha[0], id_proj=linha[1], nome=linha[2])
            return None

    def listar_por_projeto(self, id_proj: int) -> List[Quadro]:
        quadros = []
        with closing(self._conectar()) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id_quadro, id_proj, nome FROM QUADRO WHERE id_proj = ?", (id_proj,))
            for linha in cursor.fetchall():
                quadros.append(Quadro(id_quadro=linha[0], id_proj=linha[1], nome=linha[2]))
        return quadros

    def atualizar(self, quadro: Quadro):
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute(
                    "UPDATE QUADRO SET nome = ? WHERE id_quadro = ?",
                    (quadro.nome, quadro.id_quadro)
                )

    def deletar(self, id_quadro: int):
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute("DELETE FROM QUADRO WHERE id_quadro = ?", (id_quadro,))