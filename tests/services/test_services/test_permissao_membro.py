import pytest
import sqlite3
from src.repositories.membro_projeto_repository import MembroProjetoRepository
from src.services.membro_projeto_service import MembroProjetoService

@pytest.fixture
def banco_de_teste_permissoes(tmp_path):
    """Cria o banco e insere os dados base para testar promoções e bloqueios."""
    db_path = tmp_path / "test_kanban_permissoes.db"
    
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
        
        -- Populando dados iniciais
        INSERT INTO USUARIO (id_user, nome, email, senha) VALUES (1, 'Marcelo', 'marcelo@unb.br', 'senha');
        INSERT INTO USUARIO (id_user, nome, email, senha) VALUES (2, 'Colega', 'colega@unb.br', 'senha');
        INSERT INTO USUARIO (id_user, nome, email, senha) VALUES (3, 'Invasor', 'invasor@unb.br', 'senha');
        
        INSERT INTO PROJETO (id_proj, nome, descricao, data_criacao) VALUES (1, 'Projeto Alpha', 'Testes', '2026-01-01');
        
        -- Marcelo é o gerente (1), Colega é membro normal (0)
        INSERT INTO MEMBRO_PROJETO (id_user, id_proj, gerente) VALUES (1, 1, 1);
        INSERT INTO MEMBRO_PROJETO (id_user, id_proj, gerente) VALUES (2, 1, 0);
    """)
    conexao.commit()
    conexao.close()
    
    return str(db_path)

def test_alteracao_de_permissoes(banco_de_teste_permissoes):
    repositorio = MembroProjetoRepository(db_path=banco_de_teste_permissoes)
    servico = MembroProjetoService(repository=repositorio)

    id_marcelo = 1 # Gerente
    id_colega = 2  # Membro Normal
    id_invasor = 3 # Fora do projeto
    id_projeto = 1


    with pytest.raises(PermissionError, match="Ação negada: Apenas gerentes podem gerenciar membros"):
        servico.alterar_permissao_membro(
            id_user_solicitante=id_colega, 
            id_user_alvo=id_colega, 
            id_proj=id_projeto, 
            novo_status_gerente=True
        )

    with pytest.raises(ValueError, match="Ação negada: Não pode remover a sua própria permissão de gerente"):
        servico.alterar_permissao_membro(
            id_user_solicitante=id_marcelo, 
            id_user_alvo=id_marcelo, 
            id_proj=id_projeto, 
            novo_status_gerente=False
        )


    servico.alterar_permissao_membro(
        id_user_solicitante=id_marcelo, 
        id_user_alvo=id_colega, 
        id_proj=id_projeto, 
        novo_status_gerente=True
    )
    
    # Verifica no banco se a promoção funcionou
    colega_promovido = servico.obter_membro(id_colega, id_projeto)
    assert colega_promovido.gerente is True