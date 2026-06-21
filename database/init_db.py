# database/init_db.py
import sqlite3
import os
from src.path_config import get_db_path, get_sql_path

def inicializar_banco():
    db_path = get_db_path()
    sql_path = get_sql_path()

    # Só cria as tabelas se o arquivo não existir ou estiver vazio
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        conexao = sqlite3.connect(db_path)
        cursor = conexao.cursor()

        with open(sql_path, "r", encoding="utf-8") as f:
            schema = f.read()

        cursor.executescript(schema)
        conexao.commit()
        conexao.close()
        print(f"Banco de dados inicializado em: {db_path}")