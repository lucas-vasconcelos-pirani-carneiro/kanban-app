# main.py (na raiz do projeto)
from src.views.interface_manager import create_app
from database.init_db import inicializar_banco

if __name__ == "__main__":
    inicializar_banco() # Inicializa o banco (com a lógica de caminhos que fizemos antes)
    app = create_app()
    app.mainloop()