import pytest
import sqlite3
from src.repositories.cartao_repository import CartaoRepository
from src.repositories.coluna_repository import ColunaRepository
from src.services.cartao_service import CartaoService

@pytest.fixture
def banco_de_teste_cartoes(tmp_path):
    db_path = tmp_path / "test_kanban_cartoes.db"
    
    conexao = sqlite3.connect(str(db_path))
    conexao.executescript("""
        CREATE TABLE USUARIO (
            id_user INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL
        );
        CREATE TABLE PROJETO (
            id_proj INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100) NOT NULL,
            descricao TEXT,
            data_criacao DATE NOT NULL
        );
        CREATE TABLE QUADRO (
            id_quadro INTEGER PRIMARY KEY AUTOINCREMENT,
            id_proj INTEGER NOT NULL,
            nome VARCHAR(50) NOT NULL,
            FOREIGN KEY (id_proj) REFERENCES PROJETO(id_proj) ON DELETE CASCADE
        );
        CREATE TABLE COLUNA (
            id_coluna INTEGER PRIMARY KEY AUTOINCREMENT,
            id_quadro INTEGER NOT NULL,
            nome VARCHAR(30) NOT NULL,
            limite_col INTEGER CHECK (limite_col > 0 OR limite_col IS NULL),
            FOREIGN KEY (id_quadro) REFERENCES QUADRO(id_quadro) ON DELETE CASCADE
        );
        CREATE TABLE CARTAO (
            id_cartao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_coluna INTEGER NOT NULL,
            id_raia INTEGER,
            id_user_responsavel INTEGER NOT NULL,
            nome VARCHAR(100) NOT NULL,
            descricao TEXT,
            prioridade VARCHAR(20) CHECK (prioridade IN ('baixa', 'media', 'alta', 'urgente')),
            data_limite TIMESTAMP NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_entrada_wip TIMESTAMP,
            data_conclusao TIMESTAMP,
            FOREIGN KEY (id_coluna) REFERENCES COLUNA(id_coluna) ON DELETE RESTRICT,
            FOREIGN KEY (id_user_responsavel) REFERENCES USUARIO(id_user) ON DELETE RESTRICT
        );
        
        -- DADOS BASE PARA O TESTE
        INSERT INTO USUARIO (id_user, nome, email, senha) VALUES (1, 'Marcelo', 'marcelo@unb.br', 'senha');
        INSERT INTO PROJETO (id_proj, nome, data_criacao) VALUES (1, 'Projeto Alpha', '2026-01-01');
        INSERT INTO QUADRO (id_quadro, id_proj, nome) VALUES (1, 1, 'Quadro Principal');
        
        -- Coluna 1: Backlog (Infinito)
        INSERT INTO COLUNA (id_coluna, id_quadro, nome, limite_col) VALUES (1, 1, 'Backlog', NULL);
        -- Coluna 2: Em Andamento (Limite de WIP = 2)
        INSERT INTO COLUNA (id_coluna, id_quadro, nome, limite_col) VALUES (2, 1, 'Em Andamento', 2);
    """)
    conexao.commit()
    conexao.close()
    
    return str(db_path)

def test_crud_cartao_e_wip_limit(banco_de_teste_cartoes):
    coluna_repo = ColunaRepository(db_path=banco_de_teste_cartoes)
    cartao_repo = CartaoRepository(db_path=banco_de_teste_cartoes)
    servico = CartaoService(cartao_repo=cartao_repo, coluna_repo=coluna_repo)

    id_marcelo = 1
    id_coluna_backlog = 1
    id_coluna_doing = 2

    # ---------------------------------------------------------
    # 1. CRIAR CARTÃO (Sucesso)
    # ---------------------------------------------------------
    cartao1 = servico.criar_cartao(
        id_coluna=id_coluna_backlog, 
        id_user_responsavel=id_marcelo, 
        nome="Tarefa 1", 
        data_limite="2026-10-15",
        prioridade="alta"
    )
    assert cartao1.id_cartao is not None
    assert cartao1.prioridade == "alta"

    # ---------------------------------------------------------
    # 2. VALIDAÇÃO DE PRIORIDADE DA BASE DE DADOS
    # ---------------------------------------------------------
    with pytest.raises(ValueError, match="Prioridade inválida"):
        servico.criar_cartao(
            id_coluna=id_coluna_backlog, id_user_responsavel=id_marcelo, 
            nome="Tarefa Inválida", data_limite="2026-10-15", prioridade="super_urgente" # Não existe
        )

    # ---------------------------------------------------------
    # 3. TESTE DO LIMITE DE WIP (Work In Progress)
    # ---------------------------------------------------------
    # A coluna "Em Andamento" tem limite = 2. Vamos preenchê-la.
    cartao2 = servico.criar_cartao(id_coluna_doing, id_marcelo, "Tarefa 2", "2026-12-01")
    cartao3 = servico.criar_cartao(id_coluna_doing, id_marcelo, "Tarefa 3", "2026-12-01")
    
    # Ao tentar inserir ou mover a 3ª tarefa para o Doing, o Serviço DEVE bloquear!
    with pytest.raises(ValueError, match="WIP Limit atingido!"):
        servico.mover_cartao(id_cartao=cartao1.id_cartao, novo_id_coluna=id_coluna_doing)

    # ---------------------------------------------------------
    # 4. DELETAR
    # ---------------------------------------------------------
    servico.excluir_cartao(cartao1.id_cartao)
    with pytest.raises(ValueError, match="Cartão não encontrado."):
        servico.obter_cartao(cartao1.id_cartao)