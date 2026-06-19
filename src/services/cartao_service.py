import sqlite3
from datetime import datetime
from typing import List
from src.models.cartao import Cartao
from src.repositories.cartao_repository import CartaoRepository
from src.repositories.coluna_repository import ColunaRepository

class CartaoService:
    def __init__(self, cartao_repo: CartaoRepository, coluna_repo: ColunaRepository):
        self.cartao_repo = cartao_repo
        self.coluna_repo = coluna_repo
        
        # Restrição física do SQLite mapeada no código
        self.prioridades_validas = ['baixa', 'media', 'alta', 'urgente']

    def _verificar_wip_limite(self, id_coluna: int):
        """Verifica se a coluna de destino suporta mais um cartão."""
        coluna_destino = self.coluna_repo.buscar_por_id(id_coluna)
        if not coluna_destino:
            raise ValueError("A coluna de destino não existe.")

        if coluna_destino.limite_col is not None:
            total_atual = self.cartao_repo.contar_por_coluna(id_coluna)
            if total_atual >= coluna_destino.limite_col:
                raise ValueError(f"WIP Limit atingido! A coluna '{coluna_destino.nome}' só permite {coluna_destino.limite_col} tarefa(s).")

    def criar_cartao(self, id_coluna: int, id_user_responsavel: int, nome: str, 
                     data_limite: str, prioridade: str = "baixa", descricao: str = "", id_raia: int = None) -> Cartao:
                     
        if not nome or not nome.strip() or len(nome) > 100:
            raise ValueError("O nome é obrigatório e deve ter no máximo 100 caracteres.")
            
        if not data_limite:
            raise ValueError("A data limite é obrigatória.")
            
        if prioridade not in self.prioridades_validas:
            raise ValueError(f"Prioridade inválida. As opções são: {', '.join(self.prioridades_validas)}")

        # 1. Regra de Negócio: Bloqueia a inserção se a coluna estiver lotada
        self._verificar_wip_limite(id_coluna)

        data_criacao = datetime.now().isoformat()
        
        novo_cartao = Cartao(
            id_coluna=id_coluna, id_raia=id_raia, id_user_responsavel=id_user_responsavel,
            nome=nome.strip(), descricao=descricao.strip(), prioridade=prioridade,
            data_limite=data_limite, data_criacao=data_criacao
        )
        
        try:
            novo_id = self.cartao_repo.criar(novo_cartao)
            novo_cartao.id_cartao = novo_id
            return novo_cartao
        except sqlite3.IntegrityError:
            raise ValueError("Erro de associação: O usuário, coluna ou raia informados não existem.")

    def obter_cartao(self, id_cartao: int) -> Cartao:
        cartao = self.cartao_repo.buscar_por_id(id_cartao)
        if not cartao:
            raise ValueError("Cartão não encontrado.")
        return cartao

    def mover_cartao(self, id_cartao: int, novo_id_coluna: int):
        cartao = self.obter_cartao(id_cartao)
        
        if cartao.id_coluna == novo_id_coluna:
            return # Já está na coluna certa
            
        # 1. Valida WIP da nova coluna
        self._verificar_wip_limite(novo_id_coluna)
        
        # Opcional: Aqui poderíamos definir data_entrada_wip ou data_conclusao 
        # baseado no nome ou tipo da coluna nova
        
        cartao.id_coluna = novo_id_coluna
        self.cartao_repo.atualizar(cartao)

    def excluir_cartao(self, id_cartao: int):
        self.cartao_repo.deletar(id_cartao)