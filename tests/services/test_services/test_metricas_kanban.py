import pytest
import sqlite3
import time
from datetime import datetime, timedelta
from src.repositories.coluna_repository import ColunaRepository
from src.repositories.cartao_repository import CartaoRepository
from src.services.cartao_service import CartaoService
from src.services.metricas_service import KanbanMetricasService

@pytest.fixture
def banco_metricas(tmp_path):
    db_path = tmp_path / "test_kanban_metricas.db"
    conexao = sqlite3.connect(str(db_path))
    conexao.executescript("""
        CREATE TABLE USUARIO (id_user INTEGER PRIMARY KEY, nome TEXT, email TEXT, senha TEXT);
        CREATE TABLE PROJETO (id_proj INTEGER PRIMARY KEY, nome TEXT, descricao TEXT, data_criacao DATE);
        CREATE TABLE QUADRO (id_quadro INTEGER PRIMARY KEY, id_proj INTEGER, nome TEXT);
        CREATE TABLE COLUNA (id_coluna INTEGER PRIMARY KEY, id_quadro INTEGER, nome TEXT, limite_col INTEGER);
        CREATE TABLE CARTAO (
            id_cartao INTEGER PRIMARY KEY AUTOINCREMENT, id_coluna INTEGER, id_raia INTEGER,
            id_user_responsavel INTEGER, nome TEXT, descricao TEXT, prioridade TEXT,
            data_limite TIMESTAMP, data_criacao TIMESTAMP, data_entrada_wip TIMESTAMP, data_conclusao TIMESTAMP
        );
        INSERT INTO USUARIO VALUES (1, 'Mar', 'm@unb.br', '123');
        INSERT INTO PROJETO VALUES (1, 'Sistema', 'Resíduos', '2026-01-01');
        INSERT INTO QUADRO VALUES (1, 1, 'Quadro Operacional');
        INSERT INTO COLUNA VALUES (1, 1, 'Backlog', NULL);
        INSERT INTO COLUNA VALUES (2, 1, 'Em Andamento', 5);
        INSERT INTO COLUNA VALUES (3, 1, 'Concluido', NULL);
    """)
    conexao.commit()
    conexao.close()
    return str(db_path)

def test_fluxo_de_movimentacao_e_calculo_de_metricas(banco_metricas):
    # SETUP
    coluna_repo = ColunaRepository(db_path=banco_metricas)
    cartao_repo = CartaoRepository(db_path=banco_metricas)
    
    cartao_service = CartaoService(cartao_repo=cartao_repo, coluna_repo=coluna_repo)
    metricas_service = KanbanMetricasService(cartao_repo=cartao_repo)

    id_marcelo = 1
    id_backlog = 1
    id_doing = 2
    id_concluido = 3

    # 1. Criação da tarefa no Backlog
    cartao = cartao_service.criar_cartao(id_backlog, id_marcelo, "Análise de Requisitos", "2026-12-31")
    id_cartao = cartao.id_cartao
    
    # Forçamos retroativamente a criação para 5 dias atrás para simular tempo real passando
    cartao_banco = cartao_repo.buscar_por_id(id_cartao)
    data_passada_criacao = (datetime.now() - timedelta(days=5)).isoformat()
    cartao_banco.data_criacao = data_passada_criacao
    cartao_repo.atualizar(cartao_banco)

    # 2. Movimentação: Backlog -> Em Andamento (Ativa data_entrada_wip)
    cartao_service.mover_cartao(id_cartao, id_doing)
    
    # Forçamos retroativamente a entrada no WIP para 2 dias atrás
    cartao_banco = cartao_repo.buscar_por_id(id_cartao)
    assert cartao_banco.data_entrada_wip is not None
    data_passada_wip = (datetime.now() - timedelta(days=2)).isoformat()
    cartao_banco.data_entrada_wip = data_passada_wip
    cartao_repo.atualizar(cartao_banco)

    # 3. Movimentação: Em Andamento -> Concluído (Ativa data_conclusao)
    cartao_service.mover_cartao(id_cartao, id_concluido)

    # 4. Cálculo e Validação das Métricas
    metricas = metricas_service.obter_metricas_individuais_cartao(id_cartao)
    
 # Lead Time total deve ser próximo de 5 dias
    assert metricas["lead_time_dias"] == pytest.approx(5.0, abs=0.1)
    
    # Cycle Time deve ser próximo de 2 dias
    assert metricas["cycle_time_dias"] == pytest.approx(2.0, abs=0.1)

    # 5. Validação das médias do Projeto
    medias = metricas_service.calcular_medias_projeto(id_proj=1)
    assert medias["total_cartoes_entregues"] == 1
    assert medias["lead_time_medio_dias"] == metricas["lead_time_dias"]