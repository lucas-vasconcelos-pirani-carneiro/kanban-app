class Raia:
    def __init__(self, id_raia: int = None, id_quadro: int = None, nome: str = ""):
        self.id_raia = id_raia
        self.id_quadro = id_quadro
        self.nome = nome

    def __repr__(self) -> str:
        return f'Raia(id_raia={self.id_raia}, id_quadro={self.id_quadro}, nome="{self.nome}")'