# ============================================================
# FILE: relatorios.py
# Relatórios financeiros (créditos, débitos, fornecedores)
# Compatível 100% com PostgreSQL (Supabase)
# ============================================================

from database import get_connection
from datetime import datetime
import pandas as pd


# ============================================================
# 🔍 (Opcional) Função de ajuste – hoje usamos direto %s
# ============================================================

def ajustar_placeholders(query, params):
    """
    Mantida apenas se você quiser reaproveitar queries com '?'
    (Hoje todas as queries deste arquivo já estão em %s).
    """
    count = query.count("?")
    query_corrigida = query.replace("?", "%s")
    return query_corrigida, params[:count]


# ============================================================
# 📌 RELATÓRIO: CONTA CORRENTE (CRÉDITOS + DÉBITOS)
# ============================================================

def gerar_relatorio_conta_corrente(usuario_id, data_inicio=None, data_fim=None, fornecedor_id=None):
    conn = get_connection()

    # --------------------------------------------
    # Créditos
    # --------------------------------------------
    query_creditos = """
        SELECT 
            lc.data_recebimento AS data,
            'CRÉDITO' AS tipo,
            tc.descricao AS categoria,
            lc.descricao AS descricao,
            lc.valor AS valor,
            0 AS debito,
            lc.valor AS credito,
            NULL AS fornecedor,
            NULL AS status,
            NULL AS status_cor
        FROM lancamentos_credito lc
        INNER JOIN tipos_credito tc ON lc.tipo_credito_id = tc.id
        WHERE lc.usuario_id = %s
    """
    params_creditos = [usuario_id]

    if data_inicio:
        query_creditos += " AND lc.data_recebimento >= %s"
        params_creditos.append(data_inicio)

    if data_fim:
        query_creditos += " AND lc.data_recebimento <= %s"
        params_creditos.append(data_fim)

    # --------------------------------------------
    # Débitos
    # --------------------------------------------
    query_debitos = """
        SELECT 
            pd.data_vencimento AS data,
            'DÉBITO' AS tipo,
            td.descricao AS categoria,
            ld.descricao AS descricao,
            pd.valor_parcela AS valor,
            pd.valor_parcela AS debito,
            0 AS credito,
            f.nome AS fornecedor,
            s.descricao AS status,
            s.cor AS status_cor
        FROM parcelas_debito pd
        INNER JOIN lancamentos_debito ld ON pd.lancamento_debito_id = ld.id
        INNER JOIN fornecedores f ON ld.fornecedor_id = f.id
        INNER JOIN tipos_documento td ON ld.tipo_documento_id = td.id
        INNER JOIN status_documento s ON pd.status_id = s.id
        WHERE ld.usuario_id = %s
    """
    params_debitos = [usuario_id]

    if data_inicio:
        query_debitos += " AND pd.data_vencimento >= %s"
        params_debitos.append(data_inicio)

    if data_fim:
        query_debitos += " AND pd.data_vencimento <= %s"
        params_debitos.append(data_fim)

    if fornecedor_id:
        query_debitos += " AND f.id = %s"
        params_debitos.append(fornecedor_id)

    # --------------------------------------------
    # UNION FINAL — 100% PostgreSQL válido
    # --------------------------------------------
    query_final = f"""
        {query_creditos}
        UNION ALL
        {query_debitos}
        ORDER BY data, tipo DESC
    """

    params_final = params_creditos + params_debitos

    df = pd.read_sql(query_final, conn, params=params_final)
    conn.close()

    # Saldo acumulado
    if not df.empty:
        df["saldo"] = (df["credito"] - df["debito"]).cumsum()
    else:
        df["saldo"] = 0

    return df


# ============================================================
# 📅 RELATÓRIO MENSAL DE DÉBITOS
# ============================================================

def gerar_relatorio_mensal_debitos(usuario_id, ano, mes):
    from calendar import monthrange
    conn = get_connection()

    ultimo = monthrange(ano, mes)[1]
    inicio = f"{ano}-{mes:02d}-01"
    fim = f"{ano}-{mes:02d}-{ultimo}"

    query = """
        SELECT 
            pd.data_vencimento,
            f.nome AS fornecedor,
            ld.descricao,
            td.descricao AS tipo_documento,
            pd.numero_parcela,
            ld.quantidade_parcelas,
            pd.valor_parcela,
            s.descricao AS status,
            s.cor AS status_cor,
            pd.data_pagamento,
            pd.valor_pago
        FROM parcelas_debito pd
        INNER JOIN lancamentos_debito ld ON pd.lancamento_debito_id = ld.id
        INNER JOIN fornecedores f ON ld.fornecedor_id = f.id
        INNER JOIN tipos_documento td ON ld.tipo_documento_id = td.id
        INNER JOIN status_documento s ON pd.status_id = s.id
        WHERE ld.usuario_id = %s
        AND pd.data_vencimento BETWEEN %s AND %s
        ORDER BY pd.data_vencimento, f.nome
    """

    df = pd.read_sql(query, conn, params=[usuario_id, inicio, fim])
    conn.close()

    return df


# ============================================================
# 🧾 RELATÓRIO POR FORNECEDOR
# ============================================================

def gerar_relatorio_por_fornecedor(usuario_id, fornecedor_id, data_inicio=None, data_fim=None):
    conn = get_connection()
    cursor = conn.cursor()

    # Dados do fornecedor
    cursor.execute("""
        SELECT id, nome, cpf_cnpj, telefone, email
        FROM fornecedores
        WHERE id = %s AND usuario_id = %s
    """, (fornecedor_id, usuario_id))

    fornecedor = cursor.fetchone()
    if not fornecedor:
        conn.close()
        return None

    fornecedor_info = fornecedor

    # Parcelas
    query = """
        SELECT 
            pd.id,
            pd.data_vencimento,
            ld.descricao,
            td.descricao AS tipo_documento,
            pd.numero_parcela,
            ld.quantidade_parcelas,
            pd.valor_parcela,
            s.descricao AS status,
            s.cor AS status_cor,
            pd.data_pagamento,
            pd.valor_pago
        FROM parcelas_debito pd
        INNER JOIN lancamentos_debito ld ON pd.lancamento_debito_id = ld.id
        INNER JOIN tipos_documento td ON ld.tipo_documento_id = td.id
        INNER JOIN status_documento s ON pd.status_id = s.id
        WHERE ld.fornecedor_id = %s
        AND ld.usuario_id = %s
    """

    params = [fornecedor_id, usuario_id]

    if data_inicio:
        query += " AND pd.data_vencimento >= %s"
        params.append(data_inicio)

    if data_fim:
        query += " AND pd.data_vencimento <= %s"
        params.append(data_fim)

    query += " ORDER BY pd.data_vencimento DESC"

    df_parcelas = pd.read_sql(query, conn, params=params)

    # Estatísticas
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_parcelas,
            SUM(CASE WHEN pd.status_id = 1 THEN 1 ELSE 0 END) AS parcelas_abertas,
            SUM(CASE WHEN pd.status_id = 2 THEN 1 ELSE 0 END) AS parcelas_pagas,
            SUM(CASE WHEN pd.status_id = 3 THEN 1 ELSE 0 END) AS parcelas_vencidas,
            SUM(CASE WHEN pd.status_id IN (1,3) THEN pd.valor_parcela ELSE 0 END) AS valor_em_aberto,
            SUM(CASE WHEN pd.status_id = 2 THEN COALESCE(pd.valor_pago, pd.valor_parcela) ELSE 0 END) AS valor_pago
        FROM parcelas_debito pd
        INNER JOIN lancamentos_debito ld ON pd.lancamento_debito_id = ld.id
        WHERE ld.fornecedor_id = %s
        AND ld.usuario_id = %s
    """, (fornecedor_id, usuario_id))

    estatisticas = cursor.fetchone()
    conn.close()

    return {
        "fornecedor": fornecedor_info,
        "parcelas": df_parcelas,
        "estatisticas": estatisticas
    }


# ============================================================
# 📊 RESUMO FINANCEIRO DO USUÁRIO (Dashboard)
# ============================================================

def get_resumo_financeiro(usuario_id, data_inicio=None, data_fim=None):
    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------------
    # Créditos
    # -----------------------------
    where_cred = "WHERE usuario_id = %s"
    params_cred = [usuario_id]

    if data_inicio:
        where_cred += " AND data_recebimento >= %s"
        params_cred.append(data_inicio)

    if data_fim:
        where_cred += " AND data_recebimento <= %s"
        params_cred.append(data_fim)

    cursor.execute(f"""
        SELECT COALESCE(SUM(valor), 0) AS total_creditos
        FROM lancamentos_credito
        {where_cred}
    """, params_cred)
    total_creditos = float(cursor.fetchone()["total_creditos"])

    # -----------------------------
    # Débitos totais
    # -----------------------------
    where_deb = "WHERE ld.usuario_id = %s"
    params_deb = [usuario_id]

    if data_inicio:
        where_deb += " AND pd.data_vencimento >= %s"
        params_deb.append(data_inicio)

    if data_fim:
        where_deb += " AND pd.data_vencimento <= %s"
        params_deb.append(data_fim)

    cursor.execute(f"""
        SELECT COALESCE(SUM(pd.valor_parcela), 0) AS total_debitos
        FROM parcelas_debito pd
        INNER JOIN lancamentos_debito ld ON pd.lancamento_debito_id = ld.id
        {where_deb}
    """, params_deb)
    total_debitos = float(cursor.fetchone()["total_debitos"])

    # -----------------------------
    # Débitos em aberto (status 1 e 3)
    # -----------------------------
    cursor.execute(f"""
        SELECT COALESCE(SUM(pd.valor_parcela), 0) AS debitos_em_aberto
        FROM parcelas_debito pd
        INNER JOIN lancamentos_debito ld ON pd.lancamento_debito_id = ld.id
        {where_deb} AND pd.status_id IN (1,3)
    """, params_deb)
    debitos_em_aberto = float(cursor.fetchone()["debitos_em_aberto"])

    # -----------------------------
    # Débitos pagos (status 2)
    # -----------------------------
    cursor.execute(f"""
        SELECT COALESCE(SUM(COALESCE(pd.valor_pago, pd.valor_parcela)), 0) AS debitos_pagos
        FROM parcelas_debito pd
        INNER JOIN lancamentos_debito ld ON pd.lancamento_debito_id = ld.id
        {where_deb} AND pd.status_id = 2
    """, params_deb)
    debitos_pagos = float(cursor.fetchone()["debitos_pagos"])

    conn.close()

    saldo = total_creditos - total_debitos

    return {
        "total_creditos": total_creditos,
        "total_debitos": total_debitos,
        "debitos_em_aberto": debitos_em_aberto,
        "debitos_pagos": debitos_pagos,
        "saldo": saldo,
    }
