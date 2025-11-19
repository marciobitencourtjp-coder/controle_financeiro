# ============================================
# FILE: auth.py
# Autenticação e Cadastro de Usuários
# ============================================

from database import get_connection
import bcrypt

# --------------------------------------------
# 🔑 Criar hash da senha
# --------------------------------------------
def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

# --------------------------------------------
# 🔑 Validar senha
# --------------------------------------------
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# --------------------------------------------
# 👤 Autenticar usuário
# --------------------------------------------
def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, username, password_hash, nome_completo, email
            FROM usuarios
            WHERE username = %s
        """, (username,))

        user = cursor.fetchone()
        conn.close()

        if user and verify_password(password, user["password_hash"]):
            return True, {
                "id": user["id"],
                "username": user["username"],
                "nome_completo": user["nome_completo"],
                "email": user["email"]
            }

        return False, None

    except Exception as e:
        conn.close()
        return False, f"Erro na autenticação: {str(e)}"

# --------------------------------------------
# 🆕 Criar novo usuário (RETORNO PADRONIZADO)
# Sempre retorna: (success, user_id, message)
# --------------------------------------------
def create_user(username, password, nome_completo, email):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Verifica se já existe
        cursor.execute("""
            SELECT id FROM usuarios WHERE username = %s
        """, (username,))

        existente = cursor.fetchone()
        if existente:
            conn.close()
            return False, None, "Usuário já existe."

        hashed = hash_password(password)

        cursor.execute("""
            INSERT INTO usuarios (username, password_hash, nome_completo, email)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (username, hashed, nome_completo, email))

        new_id = cursor.fetchone()["id"]

        conn.commit()
        conn.close()

        return True, new_id, "Usuário criado com sucesso!"

    except Exception as e:
        conn.rollback()
        conn.close()
        return False, None, f"Erro ao criar usuário: {str(e)}"
