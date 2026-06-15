import pytest
import sqlite3
from src.repositories.usuario_repository import UsuarioRepository
from src.services.usuario_service import UsuarioService

@pytest.fixture
def banco_de_teste(tmp_path):
    db_path = tmp_path / "test_kanban.db"
    
    conexao = sqlite3.connect(str(db_path))
    conexao.execute("""
        CREATE TABLE USUARIO (
            id_user INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL
        )
    """)
    conexao.commit()
    conexao.close()
    
    return str(db_path)

def test_crud_usuario_fluxo_completo(banco_de_teste):
    
    repositorio = UsuarioRepository(db_path=banco_de_teste)
    servico = UsuarioService(repository=repositorio)
    

    novo_usuario = servico.criar_usuario("Marcelo", "marcelo@unb.br", "senha_forte_123")
    
    assert novo_usuario.id_user is not None
    id_criado = novo_usuario.id_user
    
    usuario_buscado = servico.obter_usuario(id_criado)
    
    assert usuario_buscado.nome == "Marcelo"
    assert usuario_buscado.email == "marcelo@unb.br"
    

    servico.atualizar_dados_cadastrais(id_criado, "Marcelo Atualizado", "novo.marcelo@unb.br")
    

    usuario_atualizado = servico.obter_usuario(id_criado)
    
    assert usuario_atualizado.nome == "Marcelo Atualizado"
    assert usuario_atualizado.email == "novo.marcelo@unb.br"
    

    servico.excluir_conta(id_criado)
    
 
    with pytest.raises(ValueError, match="Usuário não encontrado."):
        servico.obter_usuario(id_criado)

        #  python -m pytest tests\services\test_services\test_usuario_service.py -v