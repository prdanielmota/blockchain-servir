import sqlite3
import os

# Caminho absoluto do banco (mesmo do config.py)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'blockchain_servir', 'servir.db')

def migrate():
    print(f"Migrando banco em: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Tentar adicionar menu_state
        cursor.execute("ALTER TABLE user ADD COLUMN menu_state TEXT DEFAULT 'MAIN'")
        print("Coluna menu_state adicionada.")
    except sqlite3.OperationalError:
        print("Coluna menu_state já existe.")
        
    try:
        # Tentar adicionar menu_context
        cursor.execute("ALTER TABLE user ADD COLUMN menu_context TEXT")
        print("Coluna menu_context adicionada.")
    except sqlite3.OperationalError:
        print("Coluna menu_context já existe.")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
