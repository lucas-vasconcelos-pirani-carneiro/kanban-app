import pytest
import sqlite3
from src.repositories.membro_projeto_repository import MembroProjetoRepository
from src.services.membro_projeto_service import MembroProjetoService

@pytest.fixture
def banco_de_teste(tmp_path):
    """
    Cria a estrutura relacional necessária e injeta dados de teste 
    para satisfazer as chaves estrangeiras (IntegrityError).
    """
    db_path = tmp_path / "test_kanban.db"
    
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
        CREATE TABLE MEMBRO_PROJETO (
            id_user INTEGER,
            id_proj INTEGER,
            gerente BOOLEAN DEFAULT 0,
            PRIMARY KEY (id_user, id_proj),
            FOREIGN KEY (id_user) REFERENCES USUARIO(id_user) ON DELETE CASCADE,
            FOREIGN KEY (id_proj) REFERENCES PROJETO(id_proj) ON DELETE CASCADE
        );
        
        -- INSERE DADOS BASE PARA OS TESTES --
        INSERT INTO USUARIO (id_user, nome, email, senha) VALUES (1, 'Marcelo', 'marcelo@unb.br', 'senha');
        INSERT INTO USUARIO (id_user, nome, email, senha) VALUES (2, 'João', 'joao@unb.br', 'senha');
        INSERT INTO PROJETO (id_proj, nome, descricao, data_criacao) VALUES (1, 'Projeto Alpha', 'Testes', '2026-01-01');
    """)
    conexao.commit()
    conexao.close()
    
    return str(db_path)

def test_crud_membro_projeto(banco_de_teste):
    #  SETUP
    repositorio = MembroProjetoRepository(db_path=banco_de_teste)
    servico = MembroProjetoService(repository=repositorio)

    id_utilizador_marcelo = 1
    id_utilizador_joao = 2
    id_projeto_alpha = 1

    # 1. ADICIONAR (CREATE)
    servico.adicionar_membro(id_utilizador_marcelo, id_projeto_alpha, gerente=False)
    
    with pytest.raises(ValueError, match="O utilizador já é membro deste projeto."):
        servico.adicionar_membro(id_utilizador_marcelo, id_projeto_alpha, gerente=True)

    # 2. LISTAR E BUSCAR (READ)
    servico.adicionar_membro(id_utilizador_joao, id_projeto_alpha, gerente=False)
    
    membros = servico.listar_membros_do_projeto(id_projeto_alpha)
    assert len(membros) == 2

    # 3. ATUALIZAR (UPDATE)
    servico.alterar_permissao_membro(id_utilizador_marcelo, id_projeto_alpha, gerente=True)
    
    marcelo_atualizado = servico.obter_membro(id_utilizador_marcelo, id_projeto_alpha)
    assert marcelo_atualizado.gerente is True

    # 4. DELETAR (DELETE)
    servico.remover_membro(id_utilizador_joao, id_projeto_alpha)
    
    # Tentar procurar o João no projeto agora tem de devolver um erro controlado
    with pytest.raises(ValueError, match="Membro não encontrado neste projeto."):
        servico.obter_membro(id_utilizador_joao, id_projeto_alpha)