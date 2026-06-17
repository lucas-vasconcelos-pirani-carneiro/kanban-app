import re
import bcrypt
from src.models.usuario import Usuario
from src.repositories.usuario_repository import UsuarioRepository

class UsuarioService:
    def __init__(self, repository: UsuarioRepository):
        self.repository = repository

    def _gerar_hash_senha(self, senha_texto_puro: str) -> str:
        """Gera um hash seguro para a senha usando bcrypt."""
        salt = bcrypt.gensalt()
        senha_hash = bcrypt.hashpw(senha_texto_puro.encode('utf-8'), salt)
        return senha_hash.decode('utf-8')

    def criar_usuario(self, nome: str, email: str, senha_texto_puro: str) -> Usuario:
        if not nome or not email or not senha_texto_puro:
            raise ValueError("Nome, e-mail e senha são campos obrigatórios.")
            
        #  Validação de formato de e-mail usando Regex
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Formato de e-mail inválido.")
            
        #  Validação de comprimento de senha
        if len(senha_texto_puro) < 6:
            raise ValueError("A senha deve ter no mínimo 6 caracteres.")
        
        #  O SQLite possui a restrição UNIQUE no e-mail
        #  captura isso para dar uma mensagem pra View.
        if self.repository.buscar_por_email(email):
            raise ValueError("Este e-mail já está cadastrado no sistema.")
        
        # HASH
        senha_hash = self._gerar_hash_senha(senha_texto_puro)
        
        novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash)
        novo_id = self.repository.criar(novo_usuario)
        novo_usuario.id_user = novo_id
        
        return novo_usuario

    def autenticar_usuario(self, email: str, senha_texto_puro: str) -> Usuario:
        """Verifica se as credenciais de login estão corretas."""
        usuario = self.repository.buscar_por_email(email)
        
        if not usuario:
            raise ValueError("Usuário não encontrado.")
            
        # Compara a senha em texto puro com o hash
        if bcrypt.checkpw(senha_texto_puro.encode('utf-8'), usuario.senha.encode('utf-8')):
            return usuario
            
        raise ValueError("Senha incorreta.")

    def obter_usuario(self, id_user: int) -> Usuario:
        usuario = self.repository.buscar_por_id(id_user)
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        return usuario

    def atualizar_dados_cadastrais(self, id_user: int, novo_nome: str, novo_email: str):
        if not novo_nome or not novo_email:
            raise ValueError("Nome e e-mail não podem estar vazios.")
            
        if not re.match(r"[^@]+@[^@]+\.[^@]+", novo_email):
            raise ValueError("Formato de e-mail inválido.")
            
        usuario_existente = self.repository.buscar_por_id(id_user)
        if not usuario_existente:
            raise ValueError("Usuário não encontrado.")

        #  Verifica se está tentando mudar para um email que já pertencido
        usuario_com_email = self.repository.buscar_por_email(novo_email)
        if usuario_com_email and usuario_com_email.id_user != id_user:
            raise ValueError("Este e-mail já está em uso por outra conta.")

        usuario_existente.nome = novo_nome
        usuario_existente.email = novo_email
        self.repository.atualizar(usuario_existente)

    def excluir_conta(self, id_user: int):
        self.repository.deletar(id_user)