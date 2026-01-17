import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'blockchain_servir', 'servir.db')

def migrate():
    print(f"Migrando banco em: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Verificar se ID 1 existe
        cursor.execute("SELECT id, name FROM ministry WHERE id = 1")
        ministry = cursor.fetchone()
        
        if ministry:
            print(f"Ministério ID 1 encontrado: {ministry[1]}")
            cursor.execute("UPDATE ministry SET name = 'Comunidade SER' WHERE id = 1")
            print("Renomeado para 'Comunidade SER'.")
        else:
            print("Ministério ID 1 não encontrado. Criando...")
            cursor.execute("INSERT INTO ministry (id, name) VALUES (1, 'Comunidade SER')")
            
        # 2. Vincular todos os usuários existentes ao ID 1 (se ainda não estiverem)
        print("Vinculando usuários existentes à Comunidade SER...")
        cursor.execute("SELECT id FROM user")
        users = cursor.fetchall()
        
        count = 0
        for u in users:
            user_id = u[0]
            # Check association
            cursor.execute("SELECT * FROM user_ministries WHERE user_id = ? AND ministry_id = 1", (user_id,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO user_ministries (user_id, ministry_id) VALUES (?, 1)", (user_id,))
                count += 1
        
        print(f"{count} usuários vinculados.")
            
    except Exception as e:
        print(f"Erro na migração: {e}")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
