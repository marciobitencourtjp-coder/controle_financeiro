# ============================================
# FILE: cadastros.py
# CRUD para:
# - Fornecedores
# - Formas de Pagamento
# - Tipos de Documento
# - Bandeiras
# - Meios de Pagamento do Usuário (cartões / PIX)
# - Status
# - Tipos de Crédito
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
# 💳 FORMAS DE PAGAMENTO (À Vista / A Prazo)  — NÃO MEXER
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
# 📄 TIPOS DE DOCUMENTO (Boleto, Cartão, PIX...)
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
# 🏦 BANDEIRAS DE CARTÃO (Tabela antiga, mantida)
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
# 🏧 MEIOS DE PAGAMENTO DO USUÁRIO (cartões / PIX)
# Tabela: meios_pagamento_usuario
# Campos:
#   - tipo_pagamento: 'CARTAO_CREDITO', 'CARTAO_DEBITO', 'PIX', 'OUTRO'
#   - apelido: ex. "Santander – Master – 9999" ou "Caixa – Principal"
#   - banco, bandeira_cartao, ultimos_digitos, chave_pix
# ============================================================
def listar_meios_pagamento_usuario(usuario_id, tipo_pagamento=None, incluir_inativos=False):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT 
            id,
            usuario_id,
            tipo_pagamento,
            apelido,
            banco,
            bandeira_cartao,
            ultimos_digitos,
            chave_pix,
            ativo,
            data_criacao
        FROM meios_pagamento_usuario
        WHERE usuario_id = %s
    """
    params = [usuario_id]

    if not incluir_inativos:
        sql += " AND ativo = TRUE"

    if tipo_pagamento:
        sql += " AND tipo_pagamento = %s"
        params.append(tipo_pagamento)

    sql += """
        ORDER BY 
            banco NULLS LAST,
            apelido,
            bandeira_cartao NULLS LAST,
            ultimos_digitos NULLS LAST
    """

    cursor.execute(sql, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def criar_meio_pagamento(
    usuario_id,
    tipo_pagamento,
    apelido,
    banco=None,
    bandeira_cartao=None,
    ultimos_digitos=None,
    chave_pix=None
):
    """
    Exemplo cartão:
        criar_meio_pagamento(
            1, 'CARTAO_CREDITO',
            'Santander – Master – 9999',
            banco='Santander',
            bandeira_cartao='Master',
            ultimos_digitos='9999'
        )

    Exemplo PIX:
        criar_meio_pagamento(
            1, 'PIX',
            'Caixa – Principal',
            banco='Caixa',
            chave_pix='meuemail@x.com'
        )
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO meios_pagamento_usuario (
                usuario_id,
                tipo_pagamento,
                apelido,
                banco,
                bandeira_cartao,
                ultimos_digitos,
                chave_pix
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            usuario_id,
            tipo_pagamento,
            apelido,
            banco,
            bandeira_cartao,
            ultimos_digitos,
            chave_pix
        ))

        novo_id = cursor.fetchone()["id"]
        conn.commit()
        conn.close()
        return True, novo_id, "Meio de pagamento cadastrado com sucesso!"

    except Exception as e:
        conn.rollback()
        conn.close()
        return False, None, f"Erro ao cadastrar meio de pagamento: {str(e)}"


def desativar_meio_pagamento(meio_id, usuario_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE meios_pagamento_usuario
            SET ativo = FALSE
            WHERE id = %s AND usuario_id = %s
        """, (meio_id, usuario_id))
        conn.commit()
        conn.close()
        return True, "Meio de pagamento desativado com sucesso."
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Erro ao desativar meio de pagamento: {str(e)}"


# ============================================================
# 🏷️ STATUS (Aberto / Pago / Vencido...)
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
