from datetime import datetime
from src.repositories.cartao_repository import CartaoRepository

class KanbanMetricasService:
    def __init__(self, cartao_repo: CartaoRepository):
        self.cartao_repo = cartao_repo

    def _calcular_diferenca_em_dias(self, data_inicio_iso: str, data_fim_iso: str) -> float:
        """Calcula a diferença em dias (com precisão decimal) entre dois timestamps ISO."""
        if not data_inicio_iso or not data_fim_iso:
            return 0.0
        inicio = datetime.fromisoformat(data_inicio_iso)
        fim = datetime.fromisoformat(data_fim_iso)
        diferenca = fim - inicio
        # Retorna em dias.
        return round(diferenca.total_seconds() / 86400, 2)

    def obter_metricas_individuais_cartao(self, id_cartao: int) -> dict:
        """Calcula Lead Time e Cycle Time de um cartão específico concluído."""
        cartao = self.cartao_repo.buscar_por_id(id_cartao)
        if not cartao:
            raise ValueError("Cartão não encontrado.")
        if not cartao.data_conclusao:
            raise ValueError("O cartão ainda não foi concluído. Não há métricas consolidadas.")

        lead_time = self._calcular_diferenca_em_dias(cartao.data_criacao, cartao.data_conclusao)
        cycle_time = self._calcular_diferenca_em_dias(cartao.data_entrada_wip, cartao.data_conclusao)

        return {
            "id_cartao": cartao.id_cartao,
            "nome": cartao.nome,
            "lead_time_dias": lead_time,
            "cycle_time_dias": cycle_time
        }

    def calcular_medias_projeto(self, id_proj: int) -> dict:
        """Calcula o tempo médio de Lead Time e Cycle Time das tarefas entregues no projeto."""
        cartoes_concluidos = self.cartao_repo.listar_concluidos_por_projeto(id_proj)
        
        if not cartoes_concluidos:
            return {
                "id_proj": id_proj,
                "total_cartoes_entregues": 0,
                "lead_time_medio_dias": 0.0,
                "cycle_time_medio_dias": 0.0
            }

        soma_lead = 0.0
        soma_cycle = 0.0

        for cartao in cartoes_concluidos:
            soma_lead += self._calcular_diferenca_em_dias(cartao.data_criacao, cartao.data_conclusao)
            soma_cycle += self._calcular_diferenca_em_dias(cartao.data_entrada_wip, cartao.data_conclusao)

        total = len(cartoes_concluidos)
        return {
            "id_proj": id_proj,
            "total_cartoes_entregues": total,
            "lead_time_medio_dias": round(soma_lead / total, 2),
            "cycle_time_medio_dias": round(soma_cycle / total, 2)
        }