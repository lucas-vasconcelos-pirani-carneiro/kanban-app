import pytest
import sqlite3
from src.repositories.projeto_repository import ProjetoRepository
from src.services.projeto_service import ProjetoService
from src.repositories.membro_projeto_repository import MembroProjetoRepository
from src.services.membro_projeto_service import MembroProjetoService

@pytest.fixture
def banco_de_teste_integracao(tmp_path):
    """
    Cria o banco temporário com as tabelas relacionadas e popula apenas os 
    usuários para podermos simular a criação do projeto sem quebrar as Foreign Keys.
    """
    db_path = tmp_path / "test_kanban_integracao.db"
    
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
        
        -- Cadastramos dois usuários base para o teste
        INSERT INTO USUARIO (id_user, nome, email, senha) VALUES (1, 'Marcelo', 'marcelo@unb.br', 'hash_senha');
        INSERT INTO USUARIO (id_user, nome, email, senha) VALUES (2, 'Colega', 'colega@unb.br', 'hash_senha');
    """)
    conexao.commit()
    conexao.close()
    
    return str(db_path)

def test_fluxo_criacao_projeto_e_adicao_membro(banco_de_teste_integracao):
    # 0. SETUP: Instanciando os repositórios e serviços de ambos os domínios
    repo_proj = ProjetoRepository(db_path=banco_de_teste_integracao)
    srv_proj = ProjetoService(repository=repo_proj)
    
    repo_membro = MembroProjetoRepository(db_path=banco_de_teste_integracao)
    srv_membro = MembroProjetoService(repository=repo_membro)

    id_marcelo = 1
    id_colega = 2


    novo_projeto = srv_proj.criar_projeto(
        nome="Projeto DF", 
        id_user_criador=id_marcelo, 
        descricao="Plano de Gerenciamento"
    )
    
    id_proj_criado = novo_projeto.id_proj
    assert id_proj_criado is not None


    # projeto inseriu a permissão corretamente durante a transação.
    membro_criador = srv_membro.obter_membro(id_user=id_marcelo, id_proj=id_proj_criado)
    
    assert membro_criador.id_user == id_marcelo
    assert membro_criador.gerente is True


    # Simulando o Marcelo (gerente) adicionando um colega de grupo ao quadro
    srv_membro.adicionar_membro(id_user=id_colega, id_proj=id_proj_criado, gerente=False)


    # Verifica se o colega entrou com a permissão correta (não-gerente)
    membro_novo = srv_membro.obter_membro(id_user=id_colega, id_proj=id_proj_criado)
    assert membro_novo.gerente is False
    
    # Verifica a listagem total de membros (deve conter exatamente 2)
    todos_membros = srv_membro.listar_membros_do_projeto(id_proj_criado)
    assert len(todos_membros) == 2