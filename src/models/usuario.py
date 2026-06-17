class Usuario:
    def __init__(self, id_user: int = None, nome: str = '', email: str = '', senha: str = ''):
        self.id_user = id_user
        self.nome = nome
        self.email = email
        self.senha = senha

    def __str__(self) -> str:
        return f'Usuario(id_user={self.id_user}, nome="{self.nome}", email="{self.email}")'  # Sem senha
    def __repr__(self) -> str:
        return self.__str__()