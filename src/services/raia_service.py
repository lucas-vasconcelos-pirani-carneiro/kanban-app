import sqlite3
from typing import List
from src.models.raia import Raia
from src.repositories.raia_repository import RaiaRepository

class RaiaService:
    def __init__(self, repository: RaiaRepository):
        self.repository = repository

    def criar_raia(self, id_quadro: int, nome: str) -> Raia:
        if not id_quadro:
            raise ValueError("O ID do quadro é obrigatório para criar uma raia.")
            
        if not nome or not nome.strip():
            raise ValueError("O nome da raia não pode estar vazio.")
            
        if len(nome) > 50:
            raise ValueError("O nome da raia deve ter no máximo 50 caracteres.")

        nova_raia = Raia(id_quadro=id_quadro, nome=nome.strip())
        
        try:
            novo_id = self.repository.criar(nova_raia)
            nova_raia.id_raia = novo_id
            return nova_raia
        except sqlite3.IntegrityError:
            raise ValueError("O quadro associado não existe na base de dados.")

    def obter_raia(self, id_raia: int) -> Raia:
        raia = self.repository.buscar_por_id(id_raia)
        if not raia:
            raise ValueError("Raia não encontrada.")
        return raia

    def listar_raias_do_quadro(self, id_quadro: int) -> List[Raia]:
        if not id_quadro:
            raise ValueError("O ID do quadro é obrigatório para a listagem.")
        return self.repository.listar_por_quadro(id_quadro)

    def atualizar_nome_raia(self, id_raia: int, novo_nome: str):
        if not novo_nome or not novo_nome.strip():
            raise ValueError("O nome da raia não pode estar vazio.")
            
        if len(novo_nome) > 50:
            raise ValueError("O nome da raia deve ter no máximo 50 caracteres.")

        raia_existente = self.repository.buscar_por_id(id_raia)
        if not raia_existente:
            raise ValueError("Raia não encontrada.")

        raia_existente.nome = novo_nome.strip()
        self.repository.atualizar(raia_existente)

    def excluir_raia(self, id_raia: int):
        # A exclusão aqui é segura mesmo com cartões na raia devido ao ON DELETE SET NULL
        self.repository.deletar(id_raia)