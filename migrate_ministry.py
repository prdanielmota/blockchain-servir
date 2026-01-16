import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'blockchain_servir', 'servir.db')

def migrate():
    print(f"Migrando banco em: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Criar tabela Ministry
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ministry (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        print("Tabela Ministry criada.")
    except Exception as e:
        print(f"Erro ao criar Ministry: {e}")

    # 2. Inserir Ministério "Geral" (ID 1)
    try:
        cursor.execute("INSERT OR IGNORE INTO ministry (id, name) VALUES (1, 'Geral')")
        print("Ministério 'Geral' garantido.")
    except Exception as e:
        print(f"Erro ao inserir Geral: {e}")

    # 3. Adicionar coluna ministry_id em ActionDefinition
    try:
        cursor.execute("ALTER TABLE action_definition ADD COLUMN ministry_id INTEGER DEFAULT 1 REFERENCES ministry(id)")
        print("Coluna ministry_id adicionada.")
    except sqlite3.OperationalError:
        print("Coluna ministry_id já existe.")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
