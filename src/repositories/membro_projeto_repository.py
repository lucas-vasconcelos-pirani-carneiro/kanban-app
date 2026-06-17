import sqlite3
from contextlib import closing
from typing import List, Optional
from src.models.membro_projeto import MembroProjeto

class MembroProjetoRepository:
    def __init__(self, db_path: str = "database/kanban.db"):
        self.db_path = db_path

    def _conectar(self) -> sqlite3.Connection:
        conexao = sqlite3.connect(self.db_path)
        conexao.execute("PRAGMA foreign_keys = ON;")
        return conexao

    def adicionar(self, membro: MembroProjeto):
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute(
                    "INSERT INTO MEMBRO_PROJETO (id_user, id_proj, gerente) VALUES (?, ?, ?)",
                    (membro.id_user, membro.id_proj, 1 if membro.gerente else 0)
                )

    def buscar(self, id_user: int, id_proj: int) -> Optional[MembroProjeto]:
        with closing(self._conectar()) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id_user, id_proj, gerente FROM MEMBRO_PROJETO WHERE id_user = ? AND id_proj = ?",
                (id_user, id_proj)
            )
            linha = cursor.fetchone()
            if linha:
                return MembroProjeto(id_user=linha[0], id_proj=linha[1], gerente=bool(linha[2]))
            return None

    def listar_por_projeto(self, id_proj: int) -> List[MembroProjeto]:
        membros = []
        with closing(self._conectar()) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id_user, id_proj, gerente FROM MEMBRO_PROJETO WHERE id_proj = ?",
                (id_proj,)
            )
            for linha in cursor.fetchall():
                membros.append(MembroProjeto(id_user=linha[0], id_proj=linha[1], gerente=bool(linha[2])))
        return membros

    def atualizar_permissao(self, id_user: int, id_proj: int, gerente: bool):
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute(
                    "UPDATE MEMBRO_PROJETO SET gerente = ? WHERE id_user = ? AND id_proj = ?",
                    (1 if gerente else 0, id_user, id_proj)
                )

    def remover(self, id_user: int, id_proj: int):
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute(
                    "DELETE FROM MEMBRO_PROJETO WHERE id_user = ? AND id_proj = ?",
                    (id_user, id_proj)
                )