import os
import toml
import psycopg2
from psycopg2.extras import RealDictCursor

REQUIRED_SECRETS = {
    "host", "port", "dbname", "user", "password"
}

REQUIRED_TABLES = {
    "usuarios": ["id", "username", "password_hash", "nome_completo"],
    "fornecedores": ["id", "usuario_id", "nome", "cpf_cnpj"],
    "formas_pagamento": ["id", "descricao"],
    "tipos_documento": ["id", "descricao"],
    "bandeiras_cartao": ["id", "descricao"],
    "status_documento": ["id", "descricao", "cor"],
    "tipos_credito": ["id", "descricao"],
    "lancamentos_debito": ["id", "usuario_id", "fornecedor_id", "valor_total"],
    "parcelas_debito": ["id", "lancamento_debito_id", "valor_parcela"],
    "lancamentos_credito": ["id", "usuario_id", "valor", "data_recebimento"],
}

print("\n🔍 INICIANDO DIAGNÓSTICO DO PROJETO\n")


# ============================================================
# 1) Carregar o secrets.toml
# ============================================================
def carregar_secrets():
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    print(f"📂 Procurando secrets em: {secrets_path}")

    if not os.path.exists(secrets_path):
        print("❌ ERRO: Arquivo secrets.toml NÃO encontrado!")
        return None

    try:
        secrets = toml.load(secrets_path)
        if "postgres" not in secrets:
            print("❌ ERRO: Bloco [postgres] não encontrado no secrets.toml!")
            return None

        print("✔ secrets.toml carregado com sucesso.")
        return secrets["postgres"]

    except Exception as e:
        print("❌ ERRO ao ler secrets.toml:", e)
        return None


# ============================================================
# 2) Verificar consistência dos secrets
# ============================================================
def validar_secrets(cfg):
    print("\n📌 Validando campos obrigatórios do PostgreSQL...")

    missing = REQUIRED_SECRETS - cfg.keys()

    if missing:
        print(f"❌ Faltando campos: {missing}")
        return False

    print("✔ Todos os campos obrigatórios do PostgreSQL estão presentes.")
    return True


# ============================================================
# 3) Testar conexão ao PostgreSQL com mensagem detalhada
# ============================================================
def testar_conexao(cfg):
    print("\n🧪 Testando conexão com o PostgreSQL...")

    try:
        conn = psycopg2.connect(
            **cfg,
            cursor_factory=RealDictCursor
        )
        print("✔ Conectado ao PostgreSQL com sucesso!")
        return conn

    except psycopg2.OperationalError as e:
        if "password" in str(e).lower() or "scram" in str(e).lower():
            print("\n❌ SENHA ERRADA no PostgreSQL!")
            print("➡ Verifique se a senha do secrets TOML é a MESMA da tela:")
            print("   Supabase → Database → Connection Info → Password")
        else:
            print("\n❌ ERRO DE CONEXÃO:", str(e))

        return None


# ============================================================
# 4) Verificar se todas as tabelas existem no banco
# ============================================================
def verificar_tabelas(conn):
    print("\n📚 Verificando tabelas obrigatórias...")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """)

    existentes = {row["table_name"] for row in cursor.fetchall()}

    faltando = REQUIRED_TABLES.keys() - existentes

    if faltando:
        print(f"❌ Tabelas faltando: {faltando}")
    else:
        print("✔ Todas as tabelas obrigatórias existem.")

    return existentes


# ============================================================
# 5) Verificar colunas de cada tabela
# ============================================================
def verificar_colunas(conn, tabelas_existem):
    print("\n🔎 Verificando colunas das tabelas...")

    cursor = conn.cursor()

    for tabela, colunas in REQUIRED_TABLES.items():
        if tabela not in tabelas_existem:
            print(f"⚠ Tabela ausente, não é possível validar: {tabela}")
            continue

        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s
        """, (tabela,))

        existentes = {row["column_name"] for row in cursor.fetchall()}
        faltando = set(colunas) - existentes

        if faltando:
            print(f"❌ Colunas faltando na tabela {tabela}: {faltando}")
        else:
            print(f"✔ {tabela}: todas as colunas OK")


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================
cfg = carregar_secrets()

if not cfg:
    exit()

if not validar_secrets(cfg):
    exit()

conn = testar_conexao(cfg)

if conn:
    tabelas = verificar_tabelas(conn)
    verificar_colunas(conn, tabelas)
    conn.close()
else:
    print("\n⚠ O banco NÃO conectou. O app rodará em SQLite.")
    print("⚠ Corrija a senha do PostgreSQL.")
