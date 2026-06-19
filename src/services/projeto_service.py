from datetime import date
from typing import List
from src.models.projeto import Projeto
from src.repositories.projeto_repository import ProjetoRepository
import sqlite3

class ProjetoService:
    def __init__(self, repository: ProjetoRepository):
        self.repository = repository

    def criar_projeto(self, nome: str, id_user_criador: int, descricao: str = "") -> Projeto:
        if not id_user_criador:
            raise ValueError("O ID do usuário criador é obrigatório.")
            
        if not nome or not nome.strip():
            raise ValueError("O nome do projeto é obrigatório.")
            
        if len(nome) > 100:
            raise ValueError("O nome do projeto deve ter no máximo 100 caracteres.")

        data_atual = date.today().isoformat()
        novo_projeto = Projeto(nome=nome.strip(), descricao=descricao.strip(), data_criacao=data_atual)
        
        try:
            # O repositório agora faz o insert nas duas tabelas
            novo_id = self.repository.criar(novo_projeto, id_user_criador)
            novo_projeto.id_proj = novo_id
            return novo_projeto
        except sqlite3.IntegrityError:
            #  Captura erro do PRAGMA foreign_keys = ON caso o id_user_criador não exista no banco
            raise ValueError("O usuário criador especificado não existe ou é inválido.")

    def obter_projeto(self, id_proj: int) -> Projeto:
        projeto = self.repository.buscar_por_id(id_proj)
        if not projeto:
            raise ValueError("Projeto não encontrado.")
        return projeto

    def listar_projetos(self) -> List[Projeto]:
        return self.repository.listar_todos()

    def atualizar_projeto(self, id_proj: int, novo_nome: str, nova_descricao: str = ""):
        if not novo_nome or not novo_nome.strip():
            raise ValueError("O nome do projeto não pode estar vazio.")
            
        if len(novo_nome) > 100:
            raise ValueError("O nome do projeto deve ter no máximo 100 caracteres.")

        projeto_existente = self.repository.buscar_por_id(id_proj)
        if not projeto_existente:
            raise ValueError("Projeto não encontrado.")

        projeto_existente.nome = novo_nome.strip()
        projeto_existente.descricao = nova_descricao.strip()
        
        self.repository.atualizar(projeto_existente)

    def excluir_projeto(self, id_proj: int):
        self.repository.deletar(id_proj)
