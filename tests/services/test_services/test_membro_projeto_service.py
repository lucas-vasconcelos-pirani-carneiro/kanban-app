import pytest
import sqlite3
from src.repositories.membro_projeto_repository import MembroProjetoRepository
from src.services.membro_projeto_service import MembroProjetoService

@pytest.fixture
def banco_de_teste(tmp_path):
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
        
        -- INSERE DADOS BASE
        INSERT INTO USUARIO (id_user, nome, email, senha) VALUES (1, 'Marcelo', 'marcelo@unb.br', 'senha');
        INSERT INTO USUARIO (id_user, nome, email, senha) VALUES (2, 'João', 'joao@unb.br', 'senha');
        INSERT INTO PROJETO (id_proj, nome, descricao, data_criacao) VALUES (1, 'Projeto Alpha', 'Testes', '2026-01-01');
        
        -- NOVA REGRA: Marcelo já nasce como gerente no banco para poder testar as inserções!
        INSERT INTO MEMBRO_PROJETO (id_user, id_proj, gerente) VALUES (1, 1, 1);
    """)
    conexao.commit()
    conexao.close()
    
    return str(db_path)

def test_crud_membro_projeto(banco_de_teste):
    repositorio = MembroProjetoRepository(db_path=banco_de_teste)
    servico = MembroProjetoService(repository=repositorio)

    id_marcelo = 1 # O Marcelo é o Gerente
    id_joao = 2    # O João será adicionado
    id_projeto_alpha = 1

    # 1. ADICIONAR (CREATE)
    # Marcelo adiciona o João
    servico.adicionar_membro(
        id_user_solicitante=id_marcelo, 
        id_user_novo=id_joao, 
        id_proj=id_projeto_alpha, 
        gerente=False
    )
    
    # Tentativa de adicionar o João novamente deve falhar
    with pytest.raises(ValueError, match="O utilizador já é membro deste projeto."):
        servico.adicionar_membro(
            id_user_solicitante=id_marcelo, 
            id_user_novo=id_joao, 
            id_proj=id_projeto_alpha, 
            gerente=False
        )

    # 2. LISTAR E BUSCAR (READ)
    membros = servico.listar_membros_do_projeto(id_projeto_alpha)
    assert len(membros) == 2 # Deve achar o Marcelo e o João

    # 3. ATUALIZAR (UPDATE)
    # Marcelo promove o João a gerente
    servico.alterar_permissao_membro(
        id_user_solicitante=id_marcelo, 
        id_user_alvo=id_joao, 
        id_proj=id_projeto_alpha, 
        novo_status_gerente=True
    )
    
    joao_atualizado = servico.obter_membro(id_joao, id_projeto_alpha)
    assert joao_atualizado.gerente is True

    # 4. DELETAR (DELETE)
    # Marcelo remove o João
    servico.remover_membro(
        id_user_solicitante=id_marcelo, 
        id_user_alvo=id_joao, 
        id_proj=id_projeto_alpha
    )
    
    # Tentar procurar o João no projeto agora tem de devolver um erro controlado
    with pytest.raises(ValueError, match="Membro não encontrado neste projeto."):
        servico.obter_membro(id_joao, id_projeto_alpha)