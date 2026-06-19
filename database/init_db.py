import sqlite3
import os

def inicializar_banco():
    os.makedirs("database", exist_ok=True)
    conexao = sqlite3.connect("database/kanban.db")
    cursor = conexao.cursor()

    with open("database/SQLite-2.sql", "r") as f:
        schema = f.read()

    cursor.executescript(schema)
    conexao.commit()
    conexao.close()
    print("Banco de dados inicializado com sucesso.")

if __name__ == "__main__":
    inicializar_banco()
