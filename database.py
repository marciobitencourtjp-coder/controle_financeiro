import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os
import toml
import streamlit as st


# ============================================
# 📌 Caminho banco SQLite local
# ============================================
DB_PATH = os.path.join(os.path.dirname(__file__), "controle_financeiro.db")


# ============================================
# 📌 Carregar secrets (prioridade: streamlit > local)
# ============================================
POSTGRES_CONFIG = None

if "postgres" in st.secrets:
    POSTGRES_CONFIG = dict(st.secrets["postgres"])
else:
    try:
        secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
        if os.path.exists(secrets_path):
            secrets = toml.load(secrets_path)
            POSTGRES_CONFIG = secrets.get("postgres")
    except Exception:
        POSTGRES_CONFIG = None


# ============================================
# 🔌 Conexão
# ============================================
def get_connection():
    if POSTGRES_CONFIG:
        try:
            conn = psycopg2.connect(
                **POSTGRES_CONFIG,
                cursor_factory=RealDictCursor
            )
            return conn
        except Exception as e:
            print("❌ Erro PostgreSQL:", e)
            print("➡️ Usando SQLite...")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================
# 🏗️ Criar tabelas
# ============================================
def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    is_postgres = isinstance(conn, psycopg2.extensions.connection)

    def ddl(sql):
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            if "already exists" not in str(e):
                print("Erro DDL:", e)

    # ---------------------------
    # ✔ Tabelas principais
    # ---------------------------
    ddl(f"""
        CREATE TABLE IF NOT EXISTS usuarios (
            id {'SERIAL' if is_postgres else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nome_completo TEXT NOT NULL,
            email TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    ddl(f"""
        CREATE TABLE IF NOT EXISTS fornecedores (
            id {'SERIAL' if is_postgres else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            cpf_cnpj TEXT,
            telefone TEXT,
            email TEXT,
            ativo {'BOOLEAN DEFAULT TRUE' if is_postgres else 'BOOLEAN DEFAULT 1'},
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    ddl(f"""
        CREATE TABLE IF NOT EXISTS formas_pagamento (
            id {'SERIAL' if is_postgres else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
            descricao TEXT NOT NULL,
            ativo BOOLEAN DEFAULT TRUE
        )
    """)

    ddl(f"""
        CREATE TABLE IF NOT EXISTS tipos_documento (
            id {'SERIAL' if is_postgres else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
            descricao TEXT NOT NULL,
            requer_bandeira BOOLEAN DEFAULT FALSE,
            permite_parcelamento BOOLEAN DEFAULT FALSE,
            ativo BOOLEAN DEFAULT TRUE
        )
    """)

    ddl(f"""
        CREATE TABLE IF NOT EXISTS bandeiras_cartao (
            id {'SERIAL' if is_postgres else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
            descricao TEXT NOT NULL,
            ativo BOOLEAN DEFAULT TRUE
        )
    """)

    ddl(f"""
        CREATE TABLE IF NOT EXISTS status_documento (
            id {'SERIAL' if is_postgres else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
            descricao TEXT NOT NULL,
            cor TEXT
        )
    """)

    ddl(f"""
        CREATE TABLE IF NOT EXISTS tipos_credito (
            id {'SERIAL' if is_postgres else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
            descricao TEXT NOT NULL,
            ativo BOOLEAN DEFAULT TRUE
        )
    """)

    ddl(f"""
        CREATE TABLE IF NOT EXISTS lancamentos_debito (
            id {'SERIAL' if is_postgres else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
            usuario_id INTEGER NOT NULL,
            fornecedor_id INTEGER NOT NULL,
            forma_pagamento_id INTEGER NOT NULL,
            tipo_documento_id INTEGER NOT NULL,
            bandeira_cartao_id INTEGER,
            valor_total DECIMAL(10,2) NOT NULL,
            descricao TEXT,
            quantidade_parcelas INTEGER DEFAULT 1,
            data_lancamento DATE NOT NULL,
            observacoes TEXT
        )
    """)

    ddl(f"""
        CREATE TABLE IF NOT EXISTS parcelas_debito (
            id {'SERIAL' if is_postgres else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
            lancamento_debito_id INTEGER NOT NULL,
            numero_parcela INTEGER NOT NULL,
            valor_parcela DECIMAL(10,2) NOT NULL,
            data_vencimento DATE NOT NULL,
            status_id INTEGER DEFAULT 1,
            data_pagamento DATE,
            valor_pago DECIMAL(10,2),
            observacoes TEXT
        )
    """)

    ddl(f"""
        CREATE TABLE IF NOT EXISTS lancamentos_credito (
            id {'SERIAL' if is_postgres else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
            usuario_id INTEGER NOT NULL,
            tipo_credito_id INTEGER NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
            descricao TEXT,
            data_recebimento DATE NOT NULL,
            observacoes TEXT,
            data_lancamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------------------------
    # ✔ NOVA TABELA — meios de pagamento por usuário
    # ---------------------------
    ddl(f"""
        CREATE TABLE IF NOT EXISTS meios_pagamento_usuario (
            id {'SERIAL' if is_postgres else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
            usuario_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,                 -- cartao_credito | cartao_debito | pix
            banco TEXT NOT NULL,                -- Nubank | Caixa | Santander...
            bandeira TEXT,                      -- Visa | Master (somente cartões)
            ultimos_digitos TEXT,               -- 4 últimos dígitos
            ativo {'BOOLEAN DEFAULT TRUE' if is_postgres else 'BOOLEAN DEFAULT 1'},
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    _insert_default_data(cursor, is_postgres)
    conn.close()


# ============================================
# Inserir dados padrão
# ============================================
def _insert_default_data(cursor, is_postgres):

    def empty(table):
        cursor.execute(f"SELECT COUNT(*) as total FROM {table}")
        row = cursor.fetchone()
        return (row["total"] if isinstance(row, dict) else row[0]) == 0

    q_pg = "%s, %s" if is_postgres else "?, ?"
    q_pg4 = "%s, %s, %s, %s" if is_postgres else "?, ?, ?, ?"

    # formas_pagamento
    if empty("formas_pagamento"):
        cursor.executemany(
            f"INSERT INTO formas_pagamento (descricao, ativo) VALUES ({q_pg})",
            [('À Vista', True), ('A Prazo', True)]
        )

    # tipos_documento
    if empty("tipos_documento"):
        cursor.executemany(
            f"INSERT INTO tipos_documento (descricao, requer_bandeira, permite_parcelamento, ativo) VALUES ({q_pg4})",
            [
                ('Carnê', False, True, True),
                ('Promissória', False, True, True),
                ('Boleto Bancário', False, True, True),
                ('Cartão de Crédito', True, True, True),
                ('Cartão de Débito', True, False, True),
                ('Dinheiro', False, False, True),
                ('PIX', False, False, True),
                ('Financiamento', False, True, True),
            ]
        )

    # bandeiras_cartao
    if empty("bandeiras_cartao"):
        cursor.executemany(
            f"INSERT INTO bandeiras_cartao (descricao, ativo) VALUES ({q_pg})",
            [('Visa', True), ('Mastercard', True), ('Elo', True),
             ('American Express', True), ('Hipercard', True)]
        )

    # status_documento
    if empty("status_documento"):
        cursor.executemany(
            f"INSERT INTO status_documento (descricao, cor) VALUES ({q_pg})",
            [('Aberto', '#FFA500'), ('Pago', '#28A745'),
             ('Vencido', '#DC3545'), ('Cancelado', '#6C757D')]
        )

    # tipos_credito
    if empty("tipos_credito"):
        cursor.executemany(
            f"INSERT INTO tipos_credito (descricao, ativo) VALUES ({q_pg})",
            [('Salário', True), ('Premiação', True),
             ('13º Salário', True), ('Férias', True), ('Outros', True)]
        )

    cursor.connection.commit()


# ============================================
# Execução direta
# ============================================
if __name__ == "__main__":
    print("Inicializando banco...")
    init_database()
    print("Banco iniciado com sucesso!")
