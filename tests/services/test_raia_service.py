import pytest
import sqlite3
from src.repositories.raia_repository import RaiaRepository
from src.services.raia_service import RaiaService

@pytest.fixture
def banco_de_teste_raias(tmp_path):
    """
    Cria a estrutura relacional do projeto, quadro e raias.
    """
    db_path = tmp_path / "test_kanban_raias.db"
    
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
        CREATE TABLE RAIA (
            id_raia INTEGER PRIMARY KEY AUTOINCREMENT,
            id_quadro INTEGER NOT NULL,
            nome VARCHAR(50) NOT NULL,
            FOREIGN KEY (id_quadro) REFERENCES QUADRO(id_quadro) ON DELETE CASCADE
        );
        
        -- DADOS BASE PARA O TESTE
        INSERT INTO PROJETO (id_proj, nome, data_criacao) VALUES (1, 'Projeto Alpha', '2026-01-01');
        INSERT INTO QUADRO (id_quadro, id_proj, nome) VALUES (1, 1, 'Quadro Principal');
    """)
    conexao.commit()
    conexao.close()
    
    return str(db_path)

def test_crud_raia_completo(banco_de_teste_raias):
    repositorio = RaiaRepository(db_path=banco_de_teste_raias)
    servico = RaiaService(repository=repositorio)

    id_quadro_principal = 1

    # 1. CRIAR (E validação de nome grande)
    raia_urgente = servico.criar_raia(id_quadro=id_quadro_principal, nome="Urgentes")
    assert raia_urgente.id_raia is not None

    with pytest.raises(ValueError, match="O nome da raia deve ter no máximo 50 caracteres."):
        nome_gigante = "A" * 51
        servico.criar_raia(id_quadro=id_quadro_principal, nome=nome_gigante)

    # 2. LISTAR
    servico.criar_raia(id_quadro=id_quadro_principal, nome="Prioridade Baixa")
    raias = servico.listar_raias_do_quadro(id_quadro_principal)
    assert len(raias) == 2

    # 3. ATUALIZAR
    servico.atualizar_nome_raia(id_raia=raia_urgente.id_raia, novo_nome="Expedite (Urgente)")
    raia_atualizada = servico.obter_raia(raia_urgente.id_raia)
    assert raia_atualizada.nome == "Expedite (Urgente)"

    # 4. DELETAR
    servico.excluir_raia(raia_urgente.id_raia)
    with pytest.raises(ValueError, match="Raia não encontrada."):
        servico.obter_raia(raia_urgente.id_raia)