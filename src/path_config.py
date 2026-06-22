# src/path_config.py
import os
import sys

def get_db_path() -> str:
    """Retorna o caminho para salvar o banco de dados (persistente)."""
    if getattr(sys, 'frozen', False):
        # Running as compiled .exe -> Save next to the executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # Running as script -> Save in the project root
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    db_dir = os.path.join(base_dir, "database")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "kanban.db")

def get_sql_path() -> str:
    """Retorna o caminho do arquivo SQL empacotado."""
    if getattr(sys, 'frozen', False):
        # Running as compiled .exe -> Read from PyInstaller's temp folder
        base_dir = sys._MEIPASS
    else:
        # Running as script
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
    return os.path.join(base_dir, "database", "SQLite-2.sql")