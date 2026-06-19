class Coluna:
    def __init__(self, id_coluna: int = None, id_quadro: int = None, nome: str = "", limite_col: int = None):
        self.id_coluna = id_coluna
        self.id_quadro = id_quadro
        self.nome = nome
        self.limite_col = limite_col

    def __repr__(self) -> str:
        return f'Coluna(id_coluna={self.id_coluna}, id_quadro={self.id_quadro}, nome="{self.nome}", limite_col={self.limite_col})'