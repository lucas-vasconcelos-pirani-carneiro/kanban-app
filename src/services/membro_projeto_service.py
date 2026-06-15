import sqlite3
from typing import List
from src.models.membro_projeto import MembroProjeto
from src.repositories.membro_projeto_repository import MembroProjetoRepository

class MembroProjetoService:
    def __init__(self, repository: MembroProjetoRepository):
        self.repository = repository

    def _verificar_permissao_gerente(self, id_user_solicitante: int, id_proj: int):
        """Método auxiliar interno para validar se quem está pedindo a ação é gerente."""
        solicitante = self.repository.buscar(id_user_solicitante, id_proj)
        
        if not solicitante:
            raise ValueError("O usuário solicitante não faz parte deste projeto.")
            
        if not solicitante.gerente:
            # Usamos PermissionError para diferenciar de um erro comum de digitação
            raise PermissionError("Ação negada: Apenas gerentes podem gerenciar membros do projeto.")
        
    def adicionar_membro(self, id_user_solicitante: int, id_user_novo: int, id_proj: int, gerente: bool = False) -> MembroProjeto:
        # 1. BLINDAGEM: Verifica se quem está pedindo tem autorização
        self._verificar_permissao_gerente(id_user_solicitante, id_proj)

        # 2. Regras de negócio normais
        if not id_user_novo or not id_proj:
            raise ValueError("Os IDs do novo utilizador e do projeto são obrigatórios.")

        if self.repository.buscar(id_user_novo, id_proj):
            raise ValueError("O utilizador já é membro deste projeto.")

        novo_membro = MembroProjeto(id_user=id_user_novo, id_proj=id_proj, gerente=gerente)

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

    def alterar_permissao_membro(self, id_user_solicitante: int, id_user_alvo: int, id_proj: int, novo_status_gerente: bool):
        # 1. BLINDAGEM: Apenas um gerente pode alterar as permissões de qualquer membro
        self._verificar_permissao_gerente(id_user_solicitante, id_proj)

        # 2. SEGURANÇA: Evita que o gerente remova a sua própria permissão e deixe o projeto sem liderança
        if id_user_solicitante == id_user_alvo and novo_status_gerente is False:
            raise ValueError("Ação negada: Não pode remover a sua própria permissão de gerente.")

        # 3. Valida se o alvo realmente faz parte do projeto
        membro_existente = self.repository.buscar(id_user_alvo, id_proj)
        if not membro_existente:
            raise ValueError("O membro alvo não foi encontrado neste projeto.")

        # 4. Executa a alteração no repositório
        self.repository.atualizar_permissao(id_user_alvo, id_proj, novo_status_gerente)

        self.repository.atualizar_permissao(id_user, id_proj, gerente)

    def remover_membro(self, id_user_solicitante: int, id_user_alvo: int, id_proj: int):
        # 1. BLINDAGEM: Apenas gerente pode remover alguém
        self._verificar_permissao_gerente(id_user_solicitante, id_proj)
        
        # Opcional de segurança: impedir que o gerente remova a si mesmo se for o único
        if id_user_solicitante == id_user_alvo:
            raise ValueError("Um gerente não pode remover a si mesmo por este menu.")

        membro_existente = self.repository.buscar(id_user_alvo, id_proj)
        if not membro_existente:
            raise ValueError("O membro alvo não foi encontrado neste projeto.")
            
        self.repository.remover(id_user_alvo, id_proj)