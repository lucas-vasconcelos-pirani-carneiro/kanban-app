import pytest
import sqlite3
from src.repositories.coluna_repository import ColunaRepository
from src.services.coluna_service import ColunaService

@pytest.fixture
def banco_de_teste_coluna(tmp_path):
    """
    Cria a estrutura relacional de base e injeta um quadro de teste
    para podermos vincular as novas colunas.
    """
    db_path = tmp_path / "test_kanban_colunas.db"
    
    conexao = sqlite3.connect(str(db_path))
    conexao.executescript("""
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
        
        -- DADOS BASE PARA O TESTE
        INSERT INTO PROJETO (id_proj, nome, data_criacao) VALUES (1, 'Projeto Alpha', '2026-01-01');
        INSERT INTO QUADRO (id_quadro, id_proj, nome) VALUES (1, 1, 'Quadro Principal');
    """)
    conexao.commit()
    conexao.close()
    
    return str(db_path)

def test_crud_coluna_e_regras_wip(banco_de_teste_coluna):
    repositorio = ColunaRepository(db_path=banco_de_teste_coluna)
    servico = ColunaService(repository=repositorio)

    id_quadro_principal = 1

    # ---------------------------------------------------------
    # 1. CRIAR BACKLOG (Sem limite de WIP - Valor NULL/None)
    # ---------------------------------------------------------
    coluna_backlog = servico.criar_coluna(
        id_quadro=id_quadro_principal, 
        nome="Backlog"
        # Não passamos o limite_col, o que simula a coluna infinita
    )
    assert coluna_backlog.id_coluna is not None
    assert coluna_backlog.limite_col is None

    # ---------------------------------------------------------
    # 2. CRIAR "EM ANDAMENTO" (Com limite de WIP)
    # ---------------------------------------------------------
    coluna_doing = servico.criar_coluna(
        id_quadro=id_quadro_principal, 
        nome="Em Andamento", 
        limite_col=3
    )
    assert coluna_doing.limite_col == 3

    # ---------------------------------------------------------
    # 3. VALIDAÇÃO: Tentar violar a regra física da base de dados
    # ---------------------------------------------------------
    # O limite_col não pode ser zero ou negativo. O serviço tem de bloquear isto.
    with pytest.raises(ValueError, match="O limite de WIP da coluna deve ser superior a zero."):
        servico.criar_coluna(id_quadro=id_quadro_principal, nome="Testes WIP", limite_col=0)

    # ---------------------------------------------------------
    # 4. LISTAR
    # ---------------------------------------------------------
    colunas_do_quadro = servico.listar_colunas_do_quadro(id_quadro_principal)
    assert len(colunas_do_quadro) == 2

    # ---------------------------------------------------------
    # 5. ATUALIZAR
    # ---------------------------------------------------------
    # Vamos atualizar a coluna "Em Andamento" para "Doing" e aumentar o limite
    servico.atualizar_coluna(
        id_coluna=coluna_doing.id_coluna, 
        novo_nome="Doing", 
        novo_limite=5
    )
    
    doing_atualizada = servico.obter_coluna(coluna_doing.id_coluna)
    assert doing_atualizada.nome == "Doing"
    assert doing_atualizada.limite_col == 5

    # ---------------------------------------------------------
    # 6. DELETAR
    # ---------------------------------------------------------
    servico.excluir_coluna(coluna_backlog.id_coluna)
    
    with pytest.raises(ValueError, match="Coluna não encontrada."):
        servico.obter_coluna(coluna_backlog.id_coluna)