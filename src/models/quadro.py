class Quadro:
    def __init__(self, id_quadro: int = None, id_proj: int = None, nome: str = ""):
        self.id_quadro = id_quadro
        self.id_proj = id_proj
        self.nome = nome

    def __repr__(self) -> str:
        return f'Quadro(id_quadro={self.id_quadro}, id_proj={self.id_proj}, nome="{self.nome}")'