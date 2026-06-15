import sqlite3
from typing import List
from src.models.membro_projeto import MembroProjeto
from src.repositories.membro_projeto_repository import MembroProjetoRepository

class MembroProjetoService:
    def __init__(self, repository: MembroProjetoRepository):
        self.repository = repository

    def adicionar_membro(self, id_user: int, id_proj: int, gerente: bool = False) -> MembroProjeto:
        if not id_user or not id_proj:
            raise ValueError("Os IDs de utilizador e projeto são obrigatórios.")

        if self.repository.buscar(id_user, id_proj):
            raise ValueError("O utilizador já é membro deste projeto.")

        novo_membro = MembroProjeto(id_user=id_user, id_proj=id_proj, gerente=gerente)

        try:
            self.repository.adicionar(novo_membro)
            return novo_membro
        except sqlite3.IntegrityError:
            raise ValueError("O utilizador ou o projeto especificado não existe na base de dados.")

    def obter_membro(self, id_user: int, id_proj: int) -> MembroProjeto:
        membro = self.repository.buscar(id_user, id_proj)
        if not membro:
            raise ValueError("Membro não encontrado neste projeto.")
        return membro

    def listar_membros_do_projeto(self, id_proj: int) -> List[MembroProjeto]:
        if not id_proj:
            raise ValueError("O ID do projeto é obrigatório.")
        return self.repository.listar_por_projeto(id_proj)

    def alterar_permissao_membro(self, id_user: int, id_proj: int, gerente: bool):
        membro_existente = self.repository.buscar(id_user, id_proj)
        if not membro_existente:
            raise ValueError("Membro não encontrado neste projeto.")

        self.repository.atualizar_permissao(id_user, id_proj, gerente)

    def remover_membro(self, id_user: int, id_proj: int):
        membro_existente = self.repository.buscar(id_user, id_proj)
        if not membro_existente:
            raise ValueError("Membro não encontrado neste projeto.")
            
        self.repository.remover(id_user, id_proj)