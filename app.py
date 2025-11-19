# FILE: app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import sqlite3  # fallback local
from database import POSTGRES_CONFIG

# Importa módulos internos
import database
import auth
import cadastros
import debitos
import creditos
import relatorios


# -------------------------------------------------
# 🚩 Helpers para datas no padrão brasileiro
# -------------------------------------------------
def format_br_date(d: date) -> str:
    if isinstance(d, (date, datetime)):
        return d.strftime("%d/%m/%Y")
    return ""


def parse_br_date(s: str, default: date) -> date:
    try:
        return datetime.strptime(s.strip(), "%d/%m/%Y").date()
    except Exception:
        return default


def date_input_br(label: str, value: date, key: str) -> date:
    default_str = format_br_date(value)
    s = st.text_input(label, value=default_str, key=key)
    return parse_br_date(s, value)


# -------------------------------------------------
# ⚙️ Configuração da página (tema claro)
# -------------------------------------------------
st.set_page_config(
    page_title="Controle Financeiro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializa banco
database.init_database()

# Inicializa sessão
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None


# -------------------------------------------------
# 🎨 CSS customizado (tema claro)
# -------------------------------------------------
st.markdown(
    """
<style>
    body {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    .stApp {
        background-color: #ffffff !important;
    }
    .stMetric {
        background-color: #f0f2f6 !important;
        padding: 10px;
        border-radius: 5px;
    }
    .credito { color: #28A745 !important; font-weight: bold; }
    .debito { color: #DC3545 !important; font-weight: bold; }
    .saldo-positivo { color: #28A745 !important; font-weight: bold; }
    .saldo-negativo { color: #DC3545 !important; font-weight: bold; }
    .meio-inativo { color: #999999 !important; font-style: italic; }
</style>
""",
    unsafe_allow_html=True,
)


# -------------------------------------------------
# 👤 LOGIN PAGE
# -------------------------------------------------
def login_page():
    st.title("🔐 Controle Financeiro - Login")

    tab1, tab2 = st.tabs(["Login", "Criar Conta"])

    with tab1:
        st.subheader("Entrar no Sistema")
        username = st.text_input("Usuário", key="login_username")
        password = st.text_input("Senha", type="password", key="login_password")

        if st.button("Entrar", type="primary"):
            if username and password:
                success, user_data = auth.authenticate_user(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user = user_data
                    st.success(f"Bem-vindo(a), {user_data['nome_completo']}!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos!")
            else:
                st.warning("Preencha todos os campos!")

    with tab2:
        st.subheader("Criar Nova Conta")
        novo_username = st.text_input("Usuário", key="novo_username")
        novo_nome = st.text_input("Nome Completo", key="novo_nome")
        novo_email = st.text_input("Email (opcional)", key="novo_email")
        nova_senha = st.text_input("Senha", type="password", key="nova_senha")
        confirma_senha = st.text_input("Confirmar Senha", type="password", key="confirma_senha")

        if st.button("Criar Conta", type="primary"):
            if novo_username and novo_nome and nova_senha and confirma_senha:
                if nova_senha == confirma_senha:
                    success, user_id, message = auth.create_user(
                        novo_username,
                        nova_senha,
                        novo_nome,
                        novo_email if novo_email else None,
                    )
                    if success:
                        st.success(message)
                        st.info("Agora você pode fazer login!")
                    else:
                        st.error(message)
                else:
                    st.error("As senhas não coincidem!")
            else:
                st.warning("Preencha todos os campos obrigatórios!")


# -------------------------------------------------
# 🚪 LOGOUT
# -------------------------------------------------
def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()


# -------------------------------------------------
# 📊 DASHBOARD PRINCIPAL
# -------------------------------------------------
def pagina_dashboard():
    st.title("📊 Dashboard Financeiro")

    debitos.atualizar_status_parcela_vencida()

    col1, col2 = st.columns(2)
    with col1:
        data_inicio = date_input_br(
            "Data Início", value=date.today().replace(day=1), key="dash_data_inicio"
        )
    with col2:
        data_fim = date_input_br(
            "Data Fim", value=date.today(), key="dash_data_fim"
        )

    resumo = relatorios.get_resumo_financeiro(
        st.session_state.user["id"], data_inicio, data_fim
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💚 Total Créditos", f"R$ {resumo['total_creditos']:,.2f}")
    with col2:
        st.metric("❤️ Total Débitos", f"R$ {resumo['total_debitos']:,.2f}")
    with col3:
        emoji = "💰" if resumo["saldo"] >= 0 else "⚠️"
        st.metric(f"{emoji} Saldo", f"R$ {resumo['saldo']:,.2f}")

    st.divider()

    st.subheader("📅 Parcelas Próximas do Vencimento")

    hoje = date.today()
    proximos_30 = hoje + timedelta(days=30)

    parcelas = debitos.listar_parcelas_debito(
        st.session_state.user["id"], data_inicio=hoje, data_fim=proximos_30
    )

    if parcelas:
        df = pd.DataFrame(parcelas)
        df = df[df["status_id"].isin([1, 3])]
        if not df.empty:
            df_display = df[
                ["data_vencimento", "fornecedor_nome", "lancamento_descricao", "valor_parcela", "status_descricao"]
            ].copy()
            df_display.columns = ["Vencimento", "Fornecedor", "Descrição", "Valor", "Status"]
            df_display["Valor"] = df_display["Valor"].apply(lambda x: f"R$ {x:,.2f}")

            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma parcela em aberto nos próximos 30 dias.")
    else:
        st.info("Nenhuma parcela em aberto nos próximos 30 dias.")


# -------------------------------------------------
# 🏢 Fornecedores
# -------------------------------------------------
def pagina_fornecedores():
    st.title("🏢 Gestão de Fornecedores")

    tab1, tab2 = st.tabs(["Lista de Fornecedores", "Cadastrar Novo"])

    with tab1:
        fornecedores = cadastros.listar_fornecedores(st.session_state.user["id"])
        if fornecedores:
            for forn in fornecedores:
                with st.expander(f"📋 {forn['nome']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**CPF/CNPJ:** {forn['cpf_cnpj'] or 'Não informado'}")
                        st.write(f"**Telefone:** {forn['telefone'] or 'Não informado'}")
                    with col2:
                        st.write(f"**Email:** {forn['email'] or 'Não informado'}")
                        st.write(f"**Cadastrado em:** {forn['data_criacao']}")
        else:
            st.info("Nenhum fornecedor cadastrado ainda.")

    with tab2:
        st.subheader("Cadastrar Novo Fornecedor")

        nome = st.text_input("Nome do Fornecedor *")
        cpf_cnpj = st.text_input("CPF/CNPJ")
        telefone = st.text_input("Telefone")
        email = st.text_input("Email")

        if st.button("Cadastrar Fornecedor", type="primary"):
            if nome:
                success, forn_id, message = cadastros.criar_fornecedor(
                    st.session_state.user["id"],
                    nome,
                    cpf_cnpj,
                    telefone,
                    email,
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("O nome do fornecedor é obrigatório!")


# -------------------------------------------------
# 🏧 Meios de Pagamento (cartões / PIX)
# -------------------------------------------------
def pagina_meios_pagamento():
    st.title("🏧 Meios de Pagamento (Cartões / PIX)")

    tab1, tab2 = st.tabs(["Meus Meios de Pagamento", "Cadastrar Novo"])

    # LISTA
    with tab1:
        meios = cadastros.listar_meios_pagamento_usuario(
            st.session_state.user["id"],
            incluir_inativos=True
        )

        if not meios:
            st.info("Nenhum meio de pagamento cadastrado ainda.")
        else:
            # agrupa por tipo_pagamento
            grupos = {
                "CARTAO_CREDITO": [],
                "CARTAO_DEBITO": [],
                "PIX": [],
                "OUTRO": []
            }
            for m in meios:
                t = (m.get("tipo_pagamento") or "OUTRO").upper()
                if t not in grupos:
                    grupos["OUTRO"].append(m)
                else:
                    grupos[t].append(m)

            def render_meio(m):
                ativo = m.get("ativo", True)
                classe = "" if ativo else "meio-inativo"
                status_txt = "Ativo" if ativo else "Inativo"
                linha = f"**{m.get('apelido', '')}**"
                banco = m.get("banco")
                bandeira = m.get("bandeira_cartao")
                ult = m.get("ultimos_digitos")
                chave_pix = m.get("chave_pix")

                detalhes = []
                if banco:
                    detalhes.append(f"Banco: {banco}")
                if bandeira:
                    detalhes.append(f"Bandeira: {bandeira}")
                if ult:
                    detalhes.append(f"Final: {ult}")
                if chave_pix:
                    detalhes.append(f"Chave PIX: {chave_pix}")

                with st.container():
                    st.markdown(f"<span class='{classe}'>{linha}</span>", unsafe_allow_html=True)
                    if detalhes:
                        st.write(" • " + " | ".join(detalhes))
                    st.write(f"**Status:** {status_txt}")
                    if ativo:
                        if st.button("Desativar", key=f"desativar_meio_{m['id']}"):
                            ok, msg = cadastros.desativar_meio_pagamento(m["id"], st.session_state.user["id"])
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                    st.divider()

            # Cartões de Crédito
            if grupos["CARTAO_CREDITO"]:
                st.subheader("💳 Cartões de Crédito")
                for m in grupos["CARTAO_CREDITO"]:
                    render_meio(m)

            # Cartões de Débito
            if grupos["CARTAO_DEBITO"]:
                st.subheader("💳 Cartões de Débito")
                for m in grupos["CARTAO_DEBITO"]:
                    render_meio(m)

            # PIX
            if grupos["PIX"]:
                st.subheader("⚡ PIX")
                for m in grupos["PIX"]:
                    render_meio(m)

            # Outros
            if grupos["OUTRO"]:
                st.subheader("💼 Outros")
                for m in grupos["OUTRO"]:
                    render_meio(m)

    # CADASTRO
    with tab2:
        st.subheader("Cadastrar Novo Meio de Pagamento")

        tipo_map = {
            "Cartão de Crédito": "CARTAO_CREDITO",
            "Cartão de Débito": "CARTAO_DEBITO",
            "PIX": "PIX",
            "Outro": "OUTRO",
        }

        tipo_label = st.selectbox(
            "Tipo de Pagamento *",
            list(tipo_map.keys()),
            index=0
        )
        tipo_pagamento = tipo_map[tipo_label]

        apelido = st.text_input(
            "Apelido *",
            help="Ex.: 'Santander – Master – 9999' ou 'Caixa – Principal'"
        )
        banco = st.text_input("Banco (opcional)", help="Ex.: Santander, Nubank, Caixa...")

        bandeira_cartao = None
        ultimos_digitos = None
        chave_pix = None

        if tipo_pagamento in ("CARTAO_CREDITO", "CARTAO_DEBITO"):
            bandeira_cartao = st.text_input("Bandeira do Cartão", help="Ex.: Visa, Master, Elo...")
            ultimos_digitos = st.text_input("Últimos 4 dígitos", max_chars=4)
        elif tipo_pagamento == "PIX":
            chave_pix = st.text_input("Chave PIX (opcional)", help="E-mail, CPF, telefone ou aleatória")

        if st.button("Salvar Meio de Pagamento", type="primary"):
            if not apelido:
                st.warning("Informe pelo menos o apelido.")
            else:
                ok, meio_id, msg = cadastros.criar_meio_pagamento(
                    usuario_id=st.session_state.user["id"],
                    tipo_pagamento=tipo_pagamento,
                    apelido=apelido,
                    banco=banco if banco else None,
                    bandeira_cartao=bandeira_cartao if bandeira_cartao else None,
                    ultimos_digitos=ultimos_digitos if ultimos_digitos else None,
                    chave_pix=chave_pix if chave_pix else None,
                )
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


# -------------------------------------------------
# Helper para mapear tipo_documento -> tipo_pagamento
# -------------------------------------------------
def inferir_tipo_pagamento_por_documento(descricao_tipo_doc: str):
    """
    Mapeia a descrição do tipo de documento para o tipo_pagamento
    usado em meios_pagamento_usuario.
    """
    if not descricao_tipo_doc:
        return None
    desc = descricao_tipo_doc.upper()
    if "CRÉDITO" in desc or "CREDITO" in desc:
        return "CARTAO_CREDITO"
    if "DÉBITO" in desc or "DEBITO" in desc:
        return "CARTAO_DEBITO"
    if "PIX" in desc:
        return "PIX"
    return None


# -------------------------------------------------
# 💳 Lançamento de Débito
# -------------------------------------------------
def pagina_lancamento_debito():
    st.title("💳 Lançamento de Débito")

    fornecedores = cadastros.listar_fornecedores(st.session_state.user["id"])
    formas_pagamento = cadastros.listar_formas_pagamento()
    tipos_documento = cadastros.listar_tipos_documento()

    if not fornecedores:
        st.warning("⚠️ Cadastre ao menos um fornecedor antes de lançar débitos!")
        if st.button("Ir para Cadastro de Fornecedores"):
            st.session_state.menu_option = "Fornecedores"
            st.rerun()
        return

    col1, col2 = st.columns(2)

    meio_selecionado = None
    tipo_pagamento_para_meio = None
    meios_disponiveis = []

    with col1:
        fornecedor = st.selectbox(
            "Fornecedor *",
            options=fornecedores,
            format_func=lambda x: x["nome"],
        )
        forma_pagamento = st.selectbox(
            "Forma de Pagamento *",
            options=formas_pagamento,
            format_func=lambda x: x["descricao"]
        )
        tipo_documento = st.selectbox(
            "Tipo de Documento *",
            options=tipos_documento,
            format_func=lambda x: x["descricao"]
        )

        # Descobre se esse tipo de documento usa cartão / pix
        tipo_pagamento_para_meio = inferir_tipo_pagamento_por_documento(
            tipo_documento["descricao"]
        )

        if tipo_pagamento_para_meio:
            meios_disponiveis = cadastros.listar_meios_pagamento_usuario(
                st.session_state.user["id"],
                tipo_pagamento=tipo_pagamento_para_meio,
                incluir_inativos=False,
            )

            if meios_disponiveis:
                meio_selecionado = st.selectbox(
                    "Cartão / Conta *",
                    options=meios_disponiveis,
                    format_func=lambda x: x["apelido"],
                )
            else:
                st.warning(
                    "Nenhum cartão/conta cadastrada para esse tipo de documento.\n"
                    "Cadastre em: **Meios de Pagamento** no menu lateral."
                )

    with col2:
        valor_total = st.number_input("Valor Total *", min_value=0.01, step=0.01, format="%.2f")
        descricao = st.text_input("Descrição *")
        quantidade_parcelas = 1

        if tipo_documento["permite_parcelamento"]:
            quantidade_parcelas = st.number_input(
                "Quantidade de Parcelas *", min_value=1, max_value=360, value=1
            )

        data_primeira = date_input_br(
            "Vencimento da 1ª Parcela",
            value=date.today() + timedelta(days=30),
            key="deb_data_primeira"
        )

    observacoes = st.text_area("Observações")

    if st.button("Lançar Débito", type="primary"):
        if fornecedor and forma_pagamento and tipo_documento and valor_total > 0 and descricao:
            # monta observação final com o meio selecionado (se houver)
            observacoes_final = observacoes or ""
            if meio_selecionado:
                tag_meio = f"[Meio: {meio_selecionado['apelido']}]"
                if observacoes_final:
                    observacoes_final = observacoes_final.strip() + " " + tag_meio
                else:
                    observacoes_final = tag_meio

            success, lanc_id, message = debitos.criar_lancamento_debito(
                usuario_id=st.session_state.user["id"],
                fornecedor_id=fornecedor["id"],
                forma_pagamento_id=forma_pagamento["id"],
                tipo_documento_id=tipo_documento["id"],
                valor_total=valor_total,
                descricao=descricao,
                quantidade_parcelas=quantidade_parcelas,
                bandeira_cartao_id=None,  # mantido por compatibilidade; usando meios_pagamento_usuario em observação
                data_primeira_parcela=data_primeira,
                observacoes=observacoes_final,
            )

            if success:
                st.success(message)
                st.info(f"Valor por parcela: R$ {valor_total/quantidade_parcelas:.2f}")
                st.rerun()
            else:
                st.error(message)
        else:
            st.warning("Preencha todos os campos obrigatórios!")


# -------------------------------------------------
# 💰 Lançamento de Crédito
# -------------------------------------------------
def pagina_lancamento_credito():
    st.title("💰 Lançamento de Crédito")

    tipos_credito = cadastros.listar_tipos_credito()

    col1, col2 = st.columns(2)

    with col1:
        tipo_credito = st.selectbox(
            "Tipo de Crédito *",
            options=tipos_credito,
            format_func=lambda x: x["descricao"]
        )
        valor = st.number_input("Valor *", min_value=0.01, step=0.01, format="%.2f")

    with col2:
        descricao = st.text_input("Descrição *")
        data_receb = date_input_br(
            "Data de Recebimento",
            value=date.today(),
            key="cred_data_receb"
        )

    observacoes = st.text_area("Observações")

    if st.button("Lançar Crédito", type="primary"):
        if tipo_credito and valor > 0 and descricao:
            success, cred_id, message = creditos.criar_lancamento_credito(
                usuario_id=st.session_state.user["id"],
                tipo_credito_id=tipo_credito["id"],
                valor=valor,
                descricao=descricao,
                data_recebimento=data_receb,
                observacoes=observacoes,
            )

            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        else:
            st.warning("Preencha todos os campos obrigatórios!")


# -------------------------------------------------
# 📝 Gestão de Parcelas
# -------------------------------------------------
def pagina_gestao_parcelas():
    st.title("📝 Gestão de Parcelas")

    debitos.atualizar_status_parcela_vencida()

    col1, col2, col3 = st.columns(3)

    fornecedores = cadastros.listar_fornecedores(st.session_state.user["id"])
    status_list = cadastros.listar_status_documento()

    with col1:
        fornecedor = st.selectbox(
            "Filtrar por Fornecedor",
            options=[None] + fornecedores,
            format_func=lambda x: "Todos" if x is None else x["nome"],
        )

    with col2:
        status = st.selectbox(
            "Filtrar por Status",
            options=[None] + status_list,
            format_func=lambda x: "Todos" if x is None else x["descricao"],
        )

    with col3:
        periodo = st.selectbox(
            "Período",
            ["Todos", "Este Mês", "Próximos 30 dias", "Vencidas", "Personalizado"],
        )

    data_inicio = None
    data_fim = None

    if periodo == "Este Mês":
        hoje = date.today()
        data_inicio = hoje.replace(day=1)
        from calendar import monthrange
        data_fim = hoje.replace(day=monthrange(hoje.year, hoje.month)[1])

    elif periodo == "Próximos 30 dias":
        data_inicio = date.today()
        data_fim = date.today() + timedelta(days=30)

    elif periodo == "Vencidas":
        data_fim = date.today() - timedelta(days=1)

    elif periodo == "Personalizado":
        col_a, col_b = st.columns(2)
        with col_a:
            data_inicio = date_input_br(
                "Data Início", value=date.today().replace(day=1),
                key="gest_parc_inicio"
            )
        with col_b:
            data_fim = date_input_br(
                "Data Fim", value=date.today(),
                key="gest_parc_fim"
            )

    parcelas = debitos.listar_parcelas_debito(
        usuario_id=st.session_state.user["id"],
        fornecedor_id=fornecedor["id"] if fornecedor else None,
        status_id=status["id"] if status else None,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )

    if parcelas:
        st.write(f"**Total de parcelas encontradas:** {len(parcelas)}")

        for p in parcelas:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

            with col1:
                st.write(f"**{p['fornecedor_nome']}**")
                st.write(
                    f"{p['lancamento_descricao']} - Parcela {p['numero_parcela']}/{p['quantidade_parcelas']}"
                )

            with col2:
                st.write(f"**Vencimento:** {p['data_vencimento']}")
                st.write(f"**Valor:** R$ {p['valor_parcela']:,.2f}")

            with col3:
                st.markdown(
                    f"<span style='color: {p['status_cor']}'>●</span> {p['status_descricao']}",
                    unsafe_allow_html=True,
                )
                st.write(f"**Tipo:** {p['tipo_documento']}")

            with col4:
                if p["status_id"] in (1, 3):
                    if st.button("✅ Baixar", key=f"baixar_{p['id']}"):
                        success, message = debitos.baixar_parcela(
                            p["id"],
                            st.session_state.user["id"]
                        )
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

            st.divider()

    else:
        st.info("Nenhuma parcela encontrada com os filtros selecionados.")


# -------------------------------------------------
# 📈 RELATÓRIOS
# -------------------------------------------------
def pagina_relatorios():
    st.title("📈 Relatórios Financeiros")

    tab1, tab2, tab3 = st.tabs(["Conta Corrente", "Mensal", "Por Fornecedor"])

    # TAB 1 – Extrato Conta Corrente
    with tab1:
        st.subheader("Extrato Tipo Conta Corrente")

        col1, col2 = st.columns(2)
        with col1:
            data_inicio = date_input_br(
                "Data Início", value=date.today().replace(day=1),
                key="rel1_inicio"
            )
        with col2:
            data_fim = date_input_br(
                "Data Fim", value=date.today(),
                key="rel1_fim"
            )

        fornecedores = cadastros.listar_fornecedores(st.session_state.user["id"])
        fornecedor = st.selectbox(
            "Filtrar por Fornecedor (opcional)",
            options=[None] + fornecedores,
            format_func=lambda x: "Todos" if x is None else x["nome"],
            key="rel1_forn"
        )

        if st.button("Gerar Relatório", key="btn_rel1"):
            df = relatorios.gerar_relatorio_conta_corrente(
                st.session_state.user["id"],
                data_inicio,
                data_fim,
                fornecedor["id"] if fornecedor else None,
            )

            if not df.empty:
                df_display = df.copy()
                df_display["credito"] = df_display["credito"].apply(lambda x: f"R$ {x:,.2f}" if x > 0 else "")
                df_display["debito"] = df_display["debito"].apply(lambda x: f"R$ {x:,.2f}" if x > 0 else "")
                df_display["saldo"] = df_display["saldo"].apply(lambda x: f"R$ {x:,.2f}")

                df_display = df_display[
                    ["data", "tipo", "descricao", "fornecedor", "credito", "debito", "saldo"]
                ]
                df_display.columns = ["Data", "Tipo", "Descrição", "Fornecedor", "Crédito", "Débito", "Saldo"]

                st.dataframe(df_display, use_container_width=True, hide_index=True)

                total_credito = df["credito"].sum()
                total_debito = df["debito"].sum()
                saldo_final = df["saldo"].iloc[-1]

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("💚 Total Créditos", f"R$ {total_credito:,.2f}")
                with col2:
                    st.metric("❤️ Total Débitos", f"R$ {total_debito:,.2f}")
                with col3:
                    st.metric("💰 Saldo Final", f"R$ {saldo_final:,.2f}")
            else:
                st.info("Nenhuma movimentação encontrada no período.")

    # TAB 2 – Relatório Mensal
    with tab2:
        st.subheader("Relatório Mensal de Débitos")

        col1, col2 = st.columns(2)
        with col1:
            ano = st.number_input("Ano", min_value=2000, max_value=2100, value=date.today().year)
        with col2:
            mes = st.selectbox(
                "Mês",
                options=list(range(1, 13)),
                format_func=lambda x: [
                    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
                ][x - 1],
                index=date.today().month - 1
            )

        if st.button("Gerar Relatório", key="btn_rel2"):
            df = relatorios.gerar_relatorio_mensal_debitos(
                st.session_state.user["id"], ano, mes
            )

            if not df.empty:
                df_display = df.copy()
                df_display["valor_parcela"] = df_display["valor_parcela"].apply(lambda x: f"R$ {x:,.2f}")
                df_display["valor_pago"] = df_display["valor_pago"].apply(
                    lambda x: f"R$ {x:,.2f}" if pd.notna(x) else ""
                )

                st.dataframe(df_display, use_container_width=True, hide_index=True)
                st.metric("💰 Total do Mês", f"R$ {df['valor_parcela'].sum():,.2f}")
            else:
                st.info("Nenhum débito encontrado neste mês.")

    # TAB 3 – Relatório por Fornecedor
    with tab3:
        st.subheader("Relatório por Fornecedor")

        fornecedores = cadastros.listar_fornecedores(st.session_state.user["id"])

        if fornecedores:
            fornecedor = st.selectbox(
                "Selecione o Fornecedor",
                options=fornecedores,
                format_func=lambda x: x["nome"],
                key="rel3_forn",
            )

            col1, col2 = st.columns(2)
            with col1:
                usar_filtro_data = st.checkbox("Filtrar por período")

            data_inicio_forn = None
            data_fim_forn = None

            if usar_filtro_data:
                with col1:
                    data_inicio_forn = date_input_br(
                        "Data Início",
                        value=date.today().replace(day=1),
                        key="rel3_inicio"
                    )
                with col2:
                    data_fim_forn = date_input_br(
                        "Data Fim",
                        value=date.today(),
                        key="rel3_fim"
                    )

            if st.button("Gerar Relatório", key="btn_rel3"):
                relatorio = relatorios.gerar_relatorio_por_fornecedor(
                    st.session_state.user["id"],
                    fornecedor["id"],
                    data_inicio_forn,
                    data_fim_forn,
                )

                if relatorio:
                    st.write("### Informações do Fornecedor")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Nome:** {relatorio['fornecedor']['nome']}")
                        st.write(f"**CPF/CNPJ:** {relatorio['fornecedor']['cpf_cnpj'] or 'Não informado'}")
                    with col2:
                        st.write(f"**Telefone:** {relatorio['fornecedor']['telefone'] or 'Não informado'}")
                        st.write(f"**Email:** {relatorio['fornecedor']['email'] or 'Não informado'}")

                    st.divider()

                    st.write("### Estatísticas")
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Total de Parcelas", relatorio["estatisticas"]["total_parcelas"])
                    with col2:
                        st.metric("Parcelas Pagas", relatorio["estatisticas"]["parcelas_pagas"])
                    with col3:
                        st.metric("Parcelas em Aberto", relatorio["estatisticas"]["parcelas_abertas"])
                    with col4:
                        st.metric("Parcelas Vencidas", relatorio["estatisticas"]["parcelas_vencidas"])

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("💚 Valor Pago", f"R$ {relatorio['estatisticas']['valor_pago']:,.2f}")
                    with col2:
                        st.metric("⚠️ Valor em Aberto", f"R$ {relatorio['estatisticas']['valor_em_aberto']:,.2f}")

                    st.divider()

                    if not relatorio["parcelas"].empty:
                        st.write("### Parcelas")
                        df_display = relatorio["parcelas"].copy()
                        df_display["valor_parcela"] = df_display["valor_parcela"].apply(lambda x: f"R$ {x:,.2f}")
                        df_display["valor_pago"] = df_display["valor_pago"].apply(
                            lambda x: f"R$ {x:,.2f}" if pd.notna(x) else ""
                        )

                        st.dataframe(df_display, use_container_width=True, hide_index=True)
                else:
                    st.error("Fornecedor não encontrado.")
        else:
            st.info("Nenhum fornecedor cadastrado ainda.")


# -------------------------------------------------
# 🚀 MAIN
# -------------------------------------------------
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        # SIDEBAR
        with st.sidebar:
            st.title("💰 Controle Financeiro")
            st.write(f"**Usuário:** {st.session_state.user['nome_completo']}")
            st.divider()

            menu_option = st.radio(
                "Menu",
                [
                    "Dashboard",
                    "Fornecedores",
                    "Meios de Pagamento",
                    "Lançar Débito",
                    "Lançar Crédito",
                    "Gestão de Parcelas",
                    "Relatórios",
                ],
                key="menu_option",
            )
            st.divider()

            if st.button("🚪 Sair", use_container_width=True):
                logout()

        # MAIN CONTENT
        if menu_option == "Dashboard":
            pagina_dashboard()
        elif menu_option == "Fornecedores":
            pagina_fornecedores()
        elif menu_option == "Meios de Pagamento":
            pagina_meios_pagamento()
        elif menu_option == "Lançar Débito":
            pagina_lancamento_debito()
        elif menu_option == "Lançar Crédito":
            pagina_lancamento_credito()
        elif menu_option == "Gestão de Parcelas":
            pagina_gestao_parcelas()
        elif menu_option == "Relatórios":
            pagina_relatorios()


if __name__ == "__main__":
    main()
