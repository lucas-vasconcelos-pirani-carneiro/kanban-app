class MembroProjeto:
    def __init__(self, id_user: int, id_proj: int, gerente: bool = False):
        self.id_user = id_user
        self.id_proj = id_proj
        self.gerente = gerente

    def __repr__(self) -> str:
        return f'MembroProjeto(id_user={self.id_user}, id_proj={self.id_proj}, gerente={self.gerente})'
    def __str__(self) -> str:
        return self.__repr__()