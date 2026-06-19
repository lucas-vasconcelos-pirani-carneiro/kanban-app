import sqlite3
from typing import List
from src.models.quadro import Quadro
from src.repositories.quadro_repository import QuadroRepository

class QuadroService:
    def __init__(self, repository: QuadroRepository):
        self.repository = repository

    def criar_quadro(self, id_proj: int, nome: str) -> Quadro:
        if not id_proj:
            raise ValueError("O ID do projeto é obrigatório.")
            
        if not nome or not nome.strip():
            raise ValueError("O nome do quadro não pode estar vazio.")
            
        if len(nome) > 50:
            raise ValueError("O nome do quadro deve ter no máximo 50 caracteres.")

        novo_quadro = Quadro(id_proj=id_proj, nome=nome.strip())
        
        try:
            novo_id = self.repository.criar(novo_quadro)
            novo_quadro.id_quadro = novo_id
            return novo_quadro
        except sqlite3.IntegrityError:
            raise ValueError("O projeto associado não existe na base de dados.")

    def obter_quadro(self, id_quadro: int) -> Quadro:
        quadro = self.repository.buscar_por_id(id_quadro)
        if not quadro:
            raise ValueError("Quadro não encontrado.")
        return quadro

    def listar_quadros_do_projeto(self, id_proj: int) -> List[Quadro]:
        if not id_proj:
            raise ValueError("O ID do projeto é obrigatório.")
        return self.repository.listar_por_projeto(id_proj)

    def atualizar_nome_quadro(self, id_quadro: int, novo_nome: str):
        if not novo_nome or not novo_nome.strip():
            raise ValueError("O novo nome não pode estar vazio.")
            
        if len(novo_nome) > 50:
            raise ValueError("O nome do quadro deve ter no máximo 50 caracteres.")

        quadro_existente = self.repository.buscar_por_id(id_quadro)
        if not quadro_existente:
            raise ValueError("Quadro não encontrado.")

        quadro_existente.nome = novo_nome.strip()
        self.repository.atualizar(quadro_existente)

    def excluir_quadro(self, id_quadro: int):
        self.repository.deletar(id_quadro)