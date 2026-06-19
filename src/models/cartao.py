class Cartao:
    def __init__(self, id_cartao: int = None, id_coluna: int = None, id_raia: int = None, 
                 id_user_responsavel: int = None, nome: str = "", descricao: str = "", 
                 prioridade: str = "baixa", data_limite: str = "", data_criacao: str = "", 
                 data_entrada_wip: str = None, data_conclusao: str = None):
        self.id_cartao = id_cartao
        self.id_coluna = id_coluna
        self.id_raia = id_raia
        self.id_user_responsavel = id_user_responsavel
        self.nome = nome
        self.descricao = descricao
        self.prioridade = prioridade
        self.data_limite = data_limite
        self.data_criacao = data_criacao
        self.data_entrada_wip = data_entrada_wip
        self.data_conclusao = data_conclusao

    def __repr__(self) -> str:
        return f'Cartao(id_cartao={self.id_cartao}, nome="{self.nome}", prioridade="{self.prioridade}")'