# ============================================
# FILE: debitos.py
# Gestão de Débitos, Parcelas e Pagamentos
# Compatível com PostgreSQL (Supabase)
# ============================================

from database import get_connection
from datetime import datetime, timedelta


# =====================================================
# ➕ CRIAR LANÇAMENTO DE DÉBITO + PARCELAS
# =====================================================
def criar_lancamento_debito(
    usuario_id,
    fornecedor_id,
    forma_pagamento_id,
    tipo_documento_id,
    valor_total,
    descricao,
    quantidade_parcelas=1,
    bandeira_cartao_id=None,
    data_lancamento=None,
    data_primeira_parcela=None,
    observacoes=None
):
    """
    Cria um lançamento de débito e gera as parcelas automaticamente.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        if data_lancamento is None:
            data_lancamento = datetime.now().date()

        if data_primeira_parcela is None:
            data_primeira_parcela = data_lancamento + timedelta(days=30)

        # Inserir lançamento principal
        cursor.execute(
            """
            INSERT INTO lancamentos_debito (
                usuario_id,
                fornecedor_id,
                forma_pagamento_id,
                tipo_documento_id,
                bandeira_cartao_id,
                valor_total,
                descricao,
                quantidade_parcelas,
                data_lancamento,
                observacoes
            )
            VALUES (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s)
            RETURNING id
        """,
            (
                usuario_id,
                fornecedor_id,
                forma_pagamento_id,
                tipo_documento_id,
                bandeira_cartao_id,
                valor_total,
                descricao,
                quantidade_parcelas,
                data_lancamento,
                observacoes,
            ),
        )

        lancamento_id = cursor.fetchone()["id"]

        # Cálculo das parcelas (ajustando centavos na última)
        valor_parcela = round(valor_total / quantidade_parcelas, 2)
        soma_parcelas = valor_parcela * (quantidade_parcelas - 1)
        ultima_parcela = round(valor_total - soma_parcelas, 2)

        for i in range(quantidade_parcelas):
            numero_parcela = i + 1
            data_vencimento = data_primeira_parcela + timedelta(days=30 * i)
            valor = ultima_parcela if numero_parcela == quantidade_parcelas else valor_parcela

            cursor.execute(
                """
                INSERT INTO parcelas_debito (
                    lancamento_debito_id,
                    numero_parcela,
                    valor_parcela,
                    data_vencimento,
                    status_id
                )
                VALUES (%s, %s, %s, %s, 1)
            """,
                (lancamento_id, numero_parcela, valor, data_vencimento),
            )

        conn.commit()
        conn.close()
        return True, lancamento_id, "Lançamento criado com sucesso!"

    except Exception as e:
        conn.rollback()
        conn.close()
        return False, None, f"Erro ao criar lançamento: {str(e)}"


# =====================================================
# 📋 LISTAR PARCELAS
# =====================================================
def listar_parcelas_debito(
    usuario_id,
    fornecedor_id=None,
    status_id=None,
    data_inicio=None,
    data_fim=None,
):
    """
    Lista parcelas de débito com filtros opcionais.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            pd.id,
            pd.lancamento_debito_id,
            pd.numero_parcela,
            pd.valor_parcela,
            pd.data_vencimento,
            pd.status_id,
            pd.data_pagamento,
            pd.valor_pago,
            pd.observacoes,
            ld.descricao AS lancamento_descricao,
            ld.quantidade_parcelas,
            ld.valor_total AS lancamento_valor_total,
            f.nome AS fornecedor_nome,
            f.id AS fornecedor_id,
            s.descricao AS status_descricao,
            s.cor AS status_cor,
            td.descricao AS tipo_documento,
            fp.descricao AS forma_pagamento,
            bc.descricao AS bandeira_cartao
        FROM parcelas_debito pd
        INNER JOIN lancamentos_debito ld ON pd.lancamento_debito_id = ld.id
        INNER JOIN fornecedores f ON ld.fornecedor_id = f.id
        INNER JOIN status_documento s ON pd.status_id = s.id
        INNER JOIN tipos_documento td ON ld.tipo_documento_id = td.id
        INNER JOIN formas_pagamento fp ON ld.forma_pagamento_id = fp.id
        LEFT JOIN bandeiras_cartao bc ON ld.bandeira_cartao_id = bc.id
        WHERE ld.usuario_id = %s
    """

    params = [usuario_id]

    if fornecedor_id:
        query += " AND f.id = %s"
        params.append(fornecedor_id)

    if status_id:
        query += " AND pd.status_id = %s"
        params.append(status_id)

    if data_inicio:
        query += " AND pd.data_vencimento >= %s"
        params.append(data_inicio)

    if data_fim:
        query += " AND pd.data_vencimento <= %s"
        params.append(data_fim)

    query += " ORDER BY pd.data_vencimento, f.nome"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return rows


# =====================================================
# 🔄 ATUALIZAR STATUS AUTOMATICAMENTE (VENCIDAS)
# =====================================================
def atualizar_status_parcela_vencida():
    """
    Marca como 'Vencido' (status_id = 3) todas as parcelas
    com status 'Aberto' (1) e data_vencimento < hoje.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        hoje = datetime.now().date()

        cursor.execute(
            """
            UPDATE parcelas_debito
            SET status_id = 3
            WHERE status_id = 1
              AND data_vencimento < %s
        """,
            (hoje,),
        )

        linhas_afetadas = cursor.rowcount
        conn.commit()
        conn.close()

        return True, linhas_afetadas

    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)


# =====================================================
# 💰 BAIXAR PARCELA (PAGAMENTO)
# =====================================================
def baixar_parcela(
    parcela_id,
    usuario_id,
    data_pagamento=None,
    valor_pago=None,
    observacoes=None,
):
    """
    Baixa (paga) uma parcela, atualizando status, data e valor pago.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Confere se a parcela pertence ao usuário
        cursor.execute(
            """
            SELECT pd.id, pd.valor_parcela
            FROM parcelas_debito pd
            INNER JOIN lancamentos_debito ld
                ON pd.lancamento_debito_id = ld.id
            WHERE pd.id = %s
              AND ld.usuario_id = %s
        """,
            (parcela_id, usuario_id),
        )

        parcela = cursor.fetchone()
        if not parcela:
            conn.close()
            return False, "Parcela não encontrada ou sem permissão."

        if data_pagamento is None:
            data_pagamento = datetime.now().date()

        if valor_pago is None:
            valor_pago = parcela["valor_parcela"]

        cursor.execute(
            """
            UPDATE parcelas_debito
            SET status_id = 2,         -- Pago
                data_pagamento = %s,
                valor_pago = %s,
                observacoes = %s
            WHERE id = %s
        """,
            (data_pagamento, valor_pago, observacoes, parcela_id),
        )

        conn.commit()
        conn.close()
        return True, "Parcela baixada com sucesso!"

    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Erro ao baixar parcela: {str(e)}"


# =====================================================
# ✏️ EDITAR PARCELA
# =====================================================
def editar_parcela(
    parcela_id,
    usuario_id,
    valor_parcela=None,
    data_vencimento=None,
    status_id=None,
    observacoes=None,
):
    """
    Edita campos de uma parcela (valor, vencimento, status, observações).
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Validar se a parcela pertence ao usuário
        cursor.execute(
            """
            SELECT pd.id
            FROM parcelas_debito pd
            INNER JOIN lancamentos_debito ld
                ON pd.lancamento_debito_id = ld.id
            WHERE pd.id = %s
              AND ld.usuario_id = %s
        """,
            (parcela_id, usuario_id),
        )

        if not cursor.fetchone():
            conn.close()
            return False, "Sem permissão para editar esta parcela."

        updates = []
        params = []

        if valor_parcela is not None:
            updates.append("valor_parcela = %s")
            params.append(valor_parcela)

        if data_vencimento is not None:
            updates.append("data_vencimento = %s")
            params.append(data_vencimento)

        if status_id is not None:
            updates.append("status_id = %s")
            params.append(status_id)

        if observacoes is not None:
            updates.append("observacoes = %s")
            params.append(observacoes)

        if not updates:
            conn.close()
            return False, "Nada para atualizar."

        params.append(parcela_id)

        cursor.execute(
            f"""
            UPDATE parcelas_debito
            SET {', '.join(updates)}
            WHERE id = %s
        """,
            params,
        )

        conn.commit()
        conn.close()
        return True, "Parcela atualizada com sucesso!"

    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Erro ao atualizar parcela: {str(e)}"


# =====================================================
# 🔍 OBTER PARCELA (DETALHES)
# =====================================================
def get_parcela(parcela_id, usuario_id):
    """
    Retorna os detalhes de uma parcela específica.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            pd.*,
            ld.descricao AS lancamento_descricao,
            ld.valor_total AS lancamento_valor_total,
            f.nome AS fornecedor_nome
        FROM parcelas_debito pd
        INNER JOIN lancamentos_debito ld
            ON pd.lancamento_debito_id = ld.id
        INNER JOIN fornecedores f
            ON ld.fornecedor_id = f.id
        WHERE pd.id = %s
          AND ld.usuario_id = %s
    """,
        (parcela_id, usuario_id),
    )

    row = cursor.fetchone()
    conn.close()
    return row


# =====================================================
# 📋 LISTAR LANÇAMENTOS DE DÉBITO
# =====================================================
def listar_lancamentos_debito(usuario_id, fornecedor_id=None):
    """
    Lista lançamentos de débito do usuário (cabecalho).
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            ld.*,
            f.nome AS fornecedor_nome,
            td.descricao AS tipo_documento,
            fp.descricao AS forma_pagamento,
            bc.descricao AS bandeira_cartao
        FROM lancamentos_debito ld
        INNER JOIN fornecedores f ON ld.fornecedor_id = f.id
        INNER JOIN tipos_documento td ON ld.tipo_documento_id = td.id
        INNER JOIN formas_pagamento fp ON ld.forma_pagamento_id = fp.id
        LEFT JOIN bandeiras_cartao bc ON ld.bandeira_cartao_id = bc.id
        WHERE ld.usuario_id = %s
    """

    params = [usuario_id]

    if fornecedor_id:
        query += " AND ld.fornecedor_id = %s"
        params.append(fornecedor_id)

    query += " ORDER BY ld.data_lancamento DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return rows
