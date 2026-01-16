import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'blockchain_servir', 'servir.db')

def migrate():
    print(f"Migrando banco em: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Criar tabela de associação user_ministries
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_ministries (
                user_id INTEGER NOT NULL,
                ministry_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, ministry_id),
                FOREIGN KEY(user_id) REFERENCES user(id),
                FOREIGN KEY(ministry_id) REFERENCES ministry(id)
            )
        ''')
        print("Tabela user_ministries criada.")
    except Exception as e:
        print(f"Erro ao criar user_ministries: {e}")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
