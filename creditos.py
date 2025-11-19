# ============================================
# FILE: creditos.py
# Gestão de Créditos (Entradas Financeiras)
# ============================================

from database import get_connection
from datetime import datetime


# =====================================================
# ➕ CRIAR LANÇAMENTO DE CRÉDITO
# =====================================================

def criar_credito(usuario_id, tipo_credito_id, valor, descricao=None,
                  data_recebimento=None, observacoes=None):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        if data_recebimento is None:
            data_recebimento = datetime.now().date()

        cursor.execute("""
            INSERT INTO lancamentos_credito
                (usuario_id, tipo_credito_id, valor, descricao,
                 data_recebimento, observacoes)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (usuario_id, tipo_credito_id, valor, descricao,
              data_recebimento, observacoes))

        novo_id = cursor.fetchone()["id"]
        conn.commit()
        conn.close()

        return True, novo_id, "Crédito lançado com sucesso!"

    except Exception as e:
        conn.rollback()
        conn.close()
        return False, None, f"Erro ao criar crédito: {str(e)}"


# =====================================================
# 📋 LISTAR CRÉDITOS
# =====================================================

def listar_creditos(usuario_id, data_inicio=None, data_fim=None, tipo_credito_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            lc.id,
            lc.usuario_id,
            lc.tipo_credito_id,
            tc.descricao AS tipo_credito,
            lc.valor,
            lc.descricao,
            lc.data_recebimento,
            lc.observacoes,
            lc.data_lancamento
        FROM lancamentos_credito lc
        INNER JOIN tipos_credito tc ON lc.tipo_credito_id = tc.id
        WHERE lc.usuario_id = %s
    """

    params = [usuario_id]

    if tipo_credito_id:
        query += " AND lc.tipo_credito_id = %s"
        params.append(tipo_credito_id)

    if data_inicio:
        query += " AND lc.data_recebimento >= %s"
        params.append(data_inicio)

    if data_fim:
        query += " AND lc.data_recebimento <= %s"
        params.append(data_fim)

    query += " ORDER BY lc.data_recebimento DESC, lc.id DESC"

    cursor.execute(query, params)
    creditos = cursor.fetchall()
    conn.close()

    return creditos


# =====================================================
# 🔍 OBTER CRÉDITO POR ID
# =====================================================

def get_credito(credito_id, usuario_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            lc.*,
            tc.descricao AS tipo_credito
        FROM lancamentos_credito lc
        INNER JOIN tipos_credito tc ON lc.tipo_credito_id = tc.id
        WHERE lc.id = %s AND lc.usuario_id = %s
    """, (credito_id, usuario_id))

    row = cursor.fetchone()
    conn.close()

    return row if row else None


# =====================================================
# ✏️ EDITAR CRÉDITO
# =====================================================

def editar_credito(credito_id, usuario_id, tipo_credito_id=None, valor=None,
                   descricao=None, data_recebimento=None, observacoes=None):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        updates = []
        params = []

        if tipo_credito_id is not None:
            updates.append("tipo_credito_id = %s")
            params.append(tipo_credito_id)

        if valor is not None:
            updates.append("valor = %s")
            params.append(valor)

        if descricao is not None:
            updates.append("descricao = %s")
            params.append(descricao)

        if data_recebimento is not None:
            updates.append("data_recebimento = %s")
            params.append(data_recebimento)

        if observacoes is not None:
            updates.append("observacoes = %s")
            params.append(observacoes)

        if not updates:
            return False, "Nenhum campo informado para atualização"

        params.extend([credito_id, usuario_id])

        cursor.execute(f"""
            UPDATE lancamentos_credito
            SET {', '.join(updates)}
            WHERE id = %s AND usuario_id = %s
        """, params)

        conn.commit()
        conn.close()
        return True, "Crédito atualizado com sucesso!"

    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Erro ao atualizar crédito: {str(e)}"


# =====================================================
# 🗑️ EXCLUIR CRÉDITO
# =====================================================

def excluir_credito(credito_id, usuario_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM lancamentos_credito
            WHERE id = %s AND usuario_id = %s
        """, (credito_id, usuario_id))

        conn.commit()
        conn.close()
        return True, "Crédito excluído com sucesso!"

    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Erro ao excluir crédito: {str(e)}"
