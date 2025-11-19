# ============================================
# FILE: cadastros.py
# CRUD de Fornecedores, Formas de Pagamento,
# Tipos de Documento, Bandeiras, Status, etc.
# Totalmente compatível com PostgreSQL
# ============================================

from database import get_connection


# ============================================================
# 🏢 FORNECEDORES
# ============================================================
def listar_fornecedores(usuario_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            id,
            nome,
            cpf_cnpj,
            telefone,
            email,
            ativo,
            data_criacao
        FROM fornecedores
        WHERE usuario_id = %s
        ORDER BY nome
    """, (usuario_id,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def criar_fornecedor(usuario_id, nome, cpf_cnpj, telefone, email):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO fornecedores (usuario_id, nome, cpf_cnpj, telefone, email)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (usuario_id, nome, cpf_cnpj, telefone, email))

        novo_id = cursor.fetchone()["id"]
        conn.commit()
        conn.close()
        return True, novo_id, "Fornecedor cadastrado com sucesso!"

    except Exception as e:
        conn.rollback()
        conn.close()
        return False, None, f"Erro ao cadastrar fornecedor: {str(e)}"


# ============================================================
# 💳 FORMAS DE PAGAMENTO
# ============================================================
def listar_formas_pagamento():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, descricao, ativo
        FROM formas_pagamento
        ORDER BY descricao
    """)

    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# 📄 TIPOS DE DOCUMENTO
# ============================================================
def listar_tipos_documento():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            id,
            descricao,
            requer_bandeira,
            permite_parcelamento,
            ativo
        FROM tipos_documento
        ORDER BY descricao
    """)

    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# 🏦 BANDEIRAS DE CARTÃO
# ============================================================
def listar_bandeiras_cartao():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, descricao, ativo
        FROM bandeiras_cartao
        ORDER BY descricao
    """)

    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# 🏷️ STATUS DO DOCUMENTO (Aberto, Pago, Vencido...)
# ============================================================
def listar_status_documento():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, descricao, cor
        FROM status_documento
        ORDER BY id
    """)

    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# 💰 TIPOS DE CRÉDITO (Salário, 13º, Férias...)
# ============================================================
def listar_tipos_credito():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, descricao, ativo
        FROM tipos_credito
        ORDER BY descricao
    """)

    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
