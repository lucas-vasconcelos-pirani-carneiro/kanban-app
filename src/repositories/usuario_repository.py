import sqlite3
from contextlib import closing
from typing import Optional
from src.models.usuario import Usuario
import os
import sys

class UsuarioRepository:
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

    def criar(self, usuario: Usuario) -> int:
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute(
                    "INSERT INTO USUARIO (nome, email, senha) VALUES (?, ?, ?)",
                    (usuario.nome, usuario.email, usuario.senha)
                )
                return cursor.lastrowid

    def buscar_por_id(self, id_user: int) -> Optional[Usuario]:
        with closing(self._conectar()) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id_user, nome, email, senha FROM USUARIO WHERE id_user = ?", (id_user,))
            linha = cursor.fetchone()
            if linha:
                return Usuario(id_user=linha[0], nome=linha[1], email=linha[2], senha=linha[3])
            return None

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        with closing(self._conectar()) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id_user, nome, email, senha FROM USUARIO WHERE email = ?", (email,))
            linha = cursor.fetchone()
            if linha:
                return Usuario(id_user=linha[0], nome=linha[1], email=linha[2], senha=linha[3])
            return None

    def atualizar(self, usuario: Usuario):
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute(
                    "UPDATE USUARIO SET nome = ?, email = ? WHERE id_user = ?",
                    (usuario.nome, usuario.email, usuario.id_user)
                )

    def deletar(self, id_user: int):
        with closing(self._conectar()) as conexao:
            with conexao:
                cursor = conexao.cursor()
                cursor.execute("DELETE FROM USUARIO WHERE id_user = ?", (id_user,))
