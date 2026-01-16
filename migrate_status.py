import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'blockchain_servir', 'servir.db')

def migrate():
    print(f"Migrando banco em: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Tentar adicionar status
        cursor.execute("ALTER TABLE action_definition ADD COLUMN status TEXT DEFAULT 'approved'")
        print("Coluna status adicionada em action_definition.")
    except sqlite3.OperationalError:
        print("Coluna status já existe.")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
