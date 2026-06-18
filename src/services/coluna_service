import sqlite3
from typing import List
from src.models.coluna import Coluna
from src.repositories.coluna_repository import ColunaRepository

class ColunaService:
    def __init__(self, repository: ColunaRepository):
        self.repository = repository

    def _validar_dados_coluna(self, nome: str, limite_col: int):
        if not nome or not nome.strip():
            raise ValueError("O nome da coluna é obrigatório.")
            
        if len(nome) > 30:
            raise ValueError("O nome da coluna deve ter no máximo 30 caracteres.")
            
        if limite_col is not None and limite_col <= 0:
            raise ValueError("O limite de WIP da coluna deve ser superior a zero.")

    def criar_coluna(self, id_quadro: int, nome: str, limite_col: int = None) -> Coluna:
        if not id_quadro:
            raise ValueError("O ID do quadro é obrigatório.")
            
        self._validar_dados_coluna(nome, limite_col)

        nova_coluna = Coluna(id_quadro=id_quadro, nome=nome.strip(), limite_col=limite_col)
        
        try:
            novo_id = self.repository.criar(nova_coluna)
            nova_coluna.id_coluna = novo_id
            return nova_coluna
        except sqlite3.IntegrityError:
            raise ValueError("O quadro associado não existe na base de dados.")

    def obter_coluna(self, id_coluna: int) -> Coluna:
        coluna = self.repository.buscar_por_id(id_coluna)
        if not coluna:
            raise ValueError("Coluna não encontrada.")
        return coluna

    def listar_colunas_do_quadro(self, id_quadro: int) -> List[Coluna]:
        if not id_quadro:
            raise ValueError("O ID do quadro é obrigatório.")
        return self.repository.listar_por_quadro(id_quadro)

    def atualizar_coluna(self, id_coluna: int, novo_nome: str, novo_limite: int = None):
        self._validar_dados_coluna(novo_nome, novo_limite)

        coluna_existente = self.repository.buscar_por_id(id_coluna)
        if not coluna_existente:
            raise ValueError("Coluna não encontrada.")

        coluna_existente.nome = novo_nome.strip()
        coluna_existente.limite_col = novo_limite
        
        self.repository.atualizar(coluna_existente)

    def excluir_coluna(self, id_coluna: int):
        # A restrição ON DELETE RESTRICT dos cartões pode impedir a exclusão 
        # se houver tarefas ainda pendentes nesta coluna. 
        try:
            self.repository.deletar(id_coluna)
        except sqlite3.IntegrityError:
            raise ValueError("Não é possível apagar a coluna: existem cartões associados a ela. Mova-os primeiro.")