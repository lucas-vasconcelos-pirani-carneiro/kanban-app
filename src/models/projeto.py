class Projeto:
    def __init__(self, id_proj: int = None, nome: str = "", descricao: str = "", data_criacao: str = ""):
        self.id_proj = id_proj
        self.nome = nome
        self.descricao = descricao
        self.data_criacao = data_criacao

    def __repr__(self) -> str:
        return f'Projeto(id_proj={self.id_proj}, nome="{self.nome}", data_criacao="{self.data_criacao}")'