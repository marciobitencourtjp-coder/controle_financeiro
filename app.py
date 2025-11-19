# FILE: app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import sqlite3  # ainda usado se cair no fallback do database

# Importa os módulos do sistema
import database
import auth
import cadastros
import debitos
import creditos
import relatorios

# -------------------------------------------------
# 🚩 Helpers para datas em padrão brasileiro
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
    """
    Input de data em formato brasileiro (dd/mm/aaaa),
    usando text_input + parse para date.
    """
    default_str = format_br_date(value)
    s = st.text_input(label, value=default_str, key=key)
    return parse_br_date(s, value)


# Configuração da página
st.set_page_config(
    page_title="Controle Financeiro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa o banco de dados
database.init_database()

# Inicializa o estado da sessão
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

# CSS customizado
st.markdown(
    """
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .credito {
        color: #28A745;
        font-weight: bold;
    }
    .debito {
        color: #DC3545;
        font-weight: bold;
    }
    .saldo-positivo {
        color: #28A745;
        font-weight: bold;
    }
    .saldo-negativo {
        color: #DC3545;
        font-weight: bold;
    }
</style>
""",
    unsafe_allow_html=True,
)


def login_page():
    """Página de login"""
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


def logout():
    """Função de logout"""
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()


def pagina_dashboard():
    """Dashboard principal"""
    st.title("📊 Dashboard Financeiro")

    # Atualiza status de parcelas vencidas
    debitos.atualizar_status_parcela_vencida()

    # Filtros de período (datas em dd/mm/aaaa)
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = date_input_br(
            "Data Início", value=date.today().replace(day=1), key="dash_data_inicio"
        )
    with col2:
        data_fim = date_input_br(
            "Data Fim", value=date.today(), key="dash_data_fim"
        )

    # Resumo financeiro
    resumo = relatorios.get_resumo_financeiro(
        st.session_state.user["id"], data_inicio, data_fim
    )

    # Métricas (3 cards: créditos, débitos, saldo)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("💚 Total Créditos", f"R$ {resumo['total_creditos']:,.2f}")

    with col2:
        st.metric("❤️ Total Débitos", f"R$ {resumo['total_debitos']:,.2f}")

    with col3:
        saldo_emoji = "💰" if resumo["saldo"] >= 0 else "⚠️"
        st.metric(f"{saldo_emoji} Saldo", f"R$ {resumo['saldo']:,.2f}")

    st.divider()

    # Parcelas próximas do vencimento (próximos 30 dias)
    st.subheader("📅 Parcelas Próximas do Vencimento")

    hoje = date.today()
    proximos_30_dias = hoje + timedelta(days=30)

    parcelas_proximas = debitos.listar_parcelas_debito(
        st.session_state.user["id"], data_inicio=hoje, data_fim=proximos_30_dias
    )

    if parcelas_proximas:
        df_proximas = pd.DataFrame(parcelas_proximas)
        # Apenas abertas e vencidas
        df_proximas = df_proximas[df_proximas["status_id"].isin([1, 3])]

        if not df_proximas.empty:
            df_display = df_proximas[
                [
                    "data_vencimento",
                    "fornecedor_nome",
                    "lancamento_descricao",
                    "valor_parcela",
                    "status_descricao",
                ]
            ].copy()
            df_display.columns = [
                "Vencimento",
                "Fornecedor",
                "Descrição",
                "Valor",
                "Status",
            ]
            df_display["Valor"] = df_display["Valor"].apply(
                lambda x: f"R$ {x:,.2f}"
            )

            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma parcela em aberto nos próximos 30 dias.")
    else:
        st.info("Nenhuma parcela em aberto nos próximos 30 dias.")


def pagina_fornecedores():
    """Página de gestão de fornecedores"""
    st.title("🏢 Gestão de Fornecedores")

    tab1, tab2 = st.tabs(["Lista de Fornecedores", "Cadastrar Novo"])

    with tab1:
        fornecedores = cadastros.listar_fornecedores(st.session_state.user["id"])

        if fornecedores:
            for forn in fornecedores:
                with st.expander(f"📋 {forn['nome']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(
                            f"**CPF/CNPJ:** {forn['cpf_cnpj'] or 'Não informado'}"
                        )
                        st.write(
                            f"**Telefone:** {forn['telefone'] or 'Não informado'}"
                        )
                    with col2:
                        st.write(
                            f"**Email:** {forn['email'] or 'Não informado'}"
                        )
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


def pagina_lancamento_debito():
    """Página de lançamento de débitos"""
    st.title("💳 Lançamento de Débito")

    # Carrega dados necessários
    fornecedores = cadastros.listar_fornecedores(st.session_state.user["id"])
    formas_pagamento = cadastros.listar_formas_pagamento()
    tipos_documento = cadastros.listar_tipos_documento()
    bandeiras = cadastros.listar_bandeiras_cartao()

    if not fornecedores:
        st.warning(
            "⚠️ Você precisa cadastrar pelo menos um fornecedor antes de lançar débitos!"
        )
        if st.button("Ir para Cadastro de Fornecedores"):
            st.session_state.menu_option = "Fornecedores"
            st.rerun()
        return

    col1, col2 = st.columns(2)

    with col1:
        fornecedor_selecionado = st.selectbox(
            "Fornecedor *",
            options=fornecedores,
            format_func=lambda x: x["nome"],
        )

        forma_pagamento = st.selectbox(
            "Forma de Pagamento *",
            options=formas_pagamento,
            format_func=lambda x: x["descricao"],
        )

        tipo_documento = st.selectbox(
            "Tipo de Documento *",
            options=tipos_documento,
            format_func=lambda x: x["descricao"],
        )

        # Mostra campo de bandeira se necessário
        bandeira_selecionada = None
        if tipo_documento["requer_bandeira"]:
            bandeira_selecionada = st.selectbox(
                "Bandeira do Cartão *",
                options=bandeiras,
                format_func=lambda x: x["descricao"],
            )

    with col2:
        valor_total = st.number_input(
            "Valor Total *", min_value=0.01, step=0.01, format="%.2f"
        )

        descricao = st.text_input("Descrição *")

        quantidade_parcelas = 1
        if tipo_documento["permite_parcelamento"]:
            quantidade_parcelas = st.number_input(
                "Quantidade de Parcelas *",
                min_value=1,
                max_value=360,
                value=1,
            )

        data_primeira_parcela = date_input_br(
            "Vencimento da 1ª Parcela",
            value=date.today() + timedelta(days=30),
            key="deb_data_primeira_parcela",
        )

    observacoes = st.text_area("Observações")

    if st.button("Lançar Débito", type="primary"):
        if (
            fornecedor_selecionado
            and forma_pagamento
            and tipo_documento
            and valor_total > 0
            and descricao
        ):
            success, lancamento_id, message = debitos.criar_lancamento_debito(
                usuario_id=st.session_state.user["id"],
                fornecedor_id=fornecedor_selecionado["id"],
                forma_pagamento_id=forma_pagamento["id"],
                tipo_documento_id=tipo_documento["id"],
                valor_total=valor_total,
                descricao=descricao,
                quantidade_parcelas=quantidade_parcelas,
                bandeira_cartao_id=(
                    bandeira_selecionada["id"]
                    if bandeira_selecionada
                    else None
                ),
                data_primeira_parcela=data_primeira_parcela,
                observacoes=observacoes,
            )

            if success:
                st.success(message)
                st.info(
                    f"**Valor de cada parcela:** R$ {valor_total/quantidade_parcelas:.2f}"
                )
                st.rerun()
            else:
                st.error(message)
        else:
            st.warning("Preencha todos os campos obrigatórios!")


def pagina_lancamento_credito():
    """Página de lançamento de créditos"""
    st.title("💰 Lançamento de Crédito")

    tipos_credito = cadastros.listar_tipos_credito()

    col1, col2 = st.columns(2)

    with col1:
        tipo_credito = st.selectbox(
            "Tipo de Crédito *",
            options=tipos_credito,
            format_func=lambda x: x["descricao"],
        )

        valor = st.number_input(
            "Valor *", min_value=0.01, step=0.01, format="%.2f"
        )

    with col2:
        descricao = st.text_input("Descrição *")

        data_recebimento = date_input_br(
            "Data de Recebimento",
            value=date.today(),
            key="cred_data_recebimento",
        )

    observacoes = st.text_area("Observações")

    if st.button("Lançar Crédito", type="primary"):
        if tipo_credito and valor > 0 and descricao:
            success, credito_id, message = creditos.criar_lancamento_credito(
                usuario_id=st.session_state.user["id"],
                tipo_credito_id=tipo_credito["id"],
                valor=valor,
                descricao=descricao,
                data_recebimento=data_recebimento,
                observacoes=observacoes,
            )

            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        else:
            st.warning("Preencha todos os campos obrigatórios!")


def pagina_gestao_parcelas():
    """Página de gestão de parcelas"""
    st.title("📝 Gestão de Parcelas")

    # Atualiza status de parcelas vencidas
    debitos.atualizar_status_parcela_vencida()

    # Filtros
    col1, col2, col3 = st.columns(3)

    fornecedores = cadastros.listar_fornecedores(st.session_state.user["id"])
    status_list = cadastros.listar_status_documento()

    with col1:
        fornecedor_filtro = st.selectbox(
            "Filtrar por Fornecedor",
            options=[None] + fornecedores,
            format_func=lambda x: "Todos" if x is None else x["nome"],
        )

    with col2:
        status_filtro = st.selectbox(
            "Filtrar por Status",
            options=[None] + status_list,
            format_func=lambda x: "Todos" if x is None else x["descricao"],
        )

    with col3:
        periodo = st.selectbox(
            "Período",
            options=[
                "Todos",
                "Este Mês",
                "Próximos 30 dias",
                "Vencidas",
                "Personalizado",
            ],
        )

    # Define datas baseado no período
    data_inicio = None
    data_fim = None

    if periodo == "Este Mês":
        hoje = date.today()
        data_inicio = hoje.replace(day=1)
        from calendar import monthrange

        ultimo_dia = monthrange(hoje.year, hoje.month)[1]
        data_fim = hoje.replace(day=ultimo_dia)
    elif periodo == "Próximos 30 dias":
        data_inicio = date.today()
        data_fim = date.today() + timedelta(days=30)
    elif periodo == "Vencidas":
        data_fim = date.today() - timedelta(days=1)
    elif periodo == "Personalizado":
        col_data1, col_data2 = st.columns(2)
        with col_data1:
            data_inicio = date_input_br(
                "Data Início",
                value=date.today().replace(day=1),
                key="gest_parc_data_inicio",
            )
        with col_data2:
            data_fim = date_input_br(
                "Data Fim",
                value=date.today(),
                key="gest_parc_data_fim",
            )

    # Busca parcelas
    parcelas = debitos.listar_parcelas_debito(
        usuario_id=st.session_state.user["id"],
        fornecedor_id=fornecedor_filtro["id"] if fornecedor_filtro else None,
        status_id=status_filtro["id"] if status_filtro else None,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )

    if parcelas:
        st.write(f"**Total de parcelas encontradas:** {len(parcelas)}")

        for parcela in parcelas:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

            with col1:
                st.write(f"**{parcela['fornecedor_nome']}**")
                st.write(
                    f"{parcela['lancamento_descricao']} - Parcela {parcela['numero_parcela']}/{parcela['quantidade_parcelas']}"
                )

            with col2:
                st.write(f"**Vencimento:** {parcela['data_vencimento']}")
                st.write(
                    f"**Valor:** R$ {parcela['valor_parcela']:,.2f}"
                )

            with col3:
                cor = parcela["status_cor"]
                st.markdown(
                    f"<span style='color: {cor}'>●</span> {parcela['status_descricao']}",
                    unsafe_allow_html=True,
                )
                st.write(f"**Tipo:** {parcela['tipo_documento']}")

            with col4:
                if parcela["status_id"] in [1, 3]:  # Aberto ou Vencido
                    if st.button("✅ Baixar", key=f"baixar_{parcela['id']}"):
                        success, message = debitos.baixar_parcela(
                            parcela["id"],
                            st.session_state.user["id"],
                        )
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

            st.divider()
    else:
        st.info("Nenhuma parcela encontrada com os filtros selecionados.")


def pagina_relatorios():
    """Página de relatórios"""
    st.title("📈 Relatórios Financeiros")

    tab1, tab2, tab3 = st.tabs(["Conta Corrente", "Mensal", "Por Fornecedor"])

    # -------------------------------------------------
    # TAB 1 – Conta Corrente
    # -------------------------------------------------
    with tab1:
        st.subheader("Extrato Tipo Conta Corrente")

        col1, col2 = st.columns(2)
        with col1:
            data_inicio = date_input_br(
                "Data Início",
                value=date.today().replace(day=1),
                key="rel1_inicio",
            )
        with col2:
            data_fim = date_input_br(
                "Data Fim", value=date.today(), key="rel1_fim"
            )

        fornecedores = cadastros.listar_fornecedores(
            st.session_state.user["id"]
        )
        fornecedor_filtro = st.selectbox(
            "Filtrar por Fornecedor (opcional)",
            options=[None] + fornecedores,
            format_func=lambda x: "Todos" if x is None else x["nome"],
            key="rel1_forn",
        )

        if st.button("Gerar Relatório", key="btn_rel1"):
            df = relatorios.gerar_relatorio_conta_corrente(
                st.session_state.user["id"],
                data_inicio,
                data_fim,
                fornecedor_filtro["id"] if fornecedor_filtro else None,
            )

            if not df.empty:
                df_display = df.copy()
                df_display["credito"] = df_display["credito"].apply(
                    lambda x: f"R$ {x:,.2f}" if x > 0 else ""
                )
                df_display["debito"] = df_display["debito"].apply(
                    lambda x: f"R$ {x:,.2f}" if x > 0 else ""
                )
                df_display["saldo"] = df_display["saldo"].apply(
                    lambda x: f"R$ {x:,.2f}"
                )

                df_display = df_display[
                    ["data", "tipo", "descricao", "fornecedor", "credito", "debito", "saldo"]
                ]
                df_display.columns = [
                    "Data",
                    "Tipo",
                    "Descrição",
                    "Fornecedor",
                    "Crédito",
                    "Débito",
                    "Saldo",
                ]

                st.dataframe(df_display, use_container_width=True, hide_index=True)

                total_credito = df["credito"].sum()
                total_debito = df["debito"].sum()
                saldo_final = df["saldo"].iloc[-1]

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "💚 Total Créditos", f"R$ {total_credito:,.2f}"
                    )
                with col2:
                    st.metric(
                        "❤️ Total Débitos", f"R$ {total_debito:,.2f}"
                    )
                with col3:
                    st.metric("💰 Saldo Final", f"R$ {saldo_final:,.2f}")
            else:
                st.info("Nenhuma movimentação encontrada no período.")

    # -------------------------------------------------
    # TAB 2 – Relatório Mensal de Débitos
    # -------------------------------------------------
    with tab2:
        st.subheader("Relatório Mensal de Débitos")

        col1, col2 = st.columns(2)
        with col1:
            ano = st.number_input(
                "Ano",
                min_value=2000,
                max_value=2100,
                value=date.today().year,
            )
        with col2:
            mes = st.selectbox(
                "Mês",
                options=list(range(1, 13)),
                format_func=lambda x: [
                    "Janeiro",
                    "Fevereiro",
                    "Março",
                    "Abril",
                    "Maio",
                    "Junho",
                    "Julho",
                    "Agosto",
                    "Setembro",
                    "Outubro",
                    "Novembro",
                    "Dezembro",
                ][x - 1],
                index=date.today().month - 1,
            )

        if st.button("Gerar Relatório", key="btn_rel2"):
            df = relatorios.gerar_relatorio_mensal_debitos(
                st.session_state.user["id"], ano, mes
            )

            if not df.empty:
                df_display = df.copy()
                df_display["valor_parcela"] = df_display["valor_parcela"].apply(
                    lambda x: f"R$ {x:,.2f}"
                )
                df_display["valor_pago"] = df_display["valor_pago"].apply(
                    lambda x: f"R$ {x:,.2f}" if pd.notna(x) else ""
                )

                st.dataframe(df_display, use_container_width=True, hide_index=True)

                st.metric(
                    "💰 Total do Mês",
                    f"R$ {df['valor_parcela'].sum():,.2f}",
                )
            else:
                st.info("Nenhum débito encontrado neste mês.")

    # -------------------------------------------------
    # TAB 3 – Relatório por Fornecedor
    # -------------------------------------------------
    with tab3:
        st.subheader("Relatório por Fornecedor")

        fornecedores = cadastros.listar_fornecedores(
            st.session_state.user["id"]
        )

        if fornecedores:
            fornecedor_selecionado = st.selectbox(
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
                        key="rel3_inicio",
                    )
                with col2:
                    data_fim_forn = date_input_br(
                        "Data Fim",
                        value=date.today(),
                        key="rel3_fim",
                    )

            if st.button("Gerar Relatório", key="btn_rel3"):
                relatorio = relatorios.gerar_relatorio_por_fornecedor(
                    st.session_state.user["id"],
                    fornecedor_selecionado["id"],
                    data_inicio_forn,
                    data_fim_forn,
                )

                if relatorio:
                    # Informações do fornecedor
                    st.write("### Informações do Fornecedor")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Nome:** {relatorio['fornecedor']['nome']}")
                        st.write(
                            f"**CPF/CNPJ:** {relatorio['fornecedor']['cpf_cnpj'] or 'Não informado'}"
                        )
                    with col2:
                        st.write(
                            f"**Telefone:** {relatorio['fornecedor']['telefone'] or 'Não informado'}"
                        )
                        st.write(
                            f"**Email:** {relatorio['fornecedor']['email'] or 'Não informado'}"
                        )

                    st.divider()

                    # Estatísticas
                    st.write("### Estatísticas")
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric(
                            "Total de Parcelas",
                            relatorio["estatisticas"]["total_parcelas"],
                        )
                    with col2:
                        st.metric(
                            "Parcelas Pagas",
                            relatorio["estatisticas"]["parcelas_pagas"],
                        )
                    with col3:
                        st.metric(
                            "Parcelas em Aberto",
                            relatorio["estatisticas"]["parcelas_abertas"],
                        )
                    with col4:
                        st.metric(
                            "Parcelas Vencidas",
                            relatorio["estatisticas"]["parcelas_vencidas"],
                        )

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "💚 Valor Pago",
                            f"R$ {relatorio['estatisticas']['valor_pago']:,.2f}",
                        )
                    with col2:
                        st.metric(
                            "⚠️ Valor em Aberto",
                            f"R$ {relatorio['estatisticas']['valor_em_aberto']:,.2f}",
                        )

                    st.divider()

                    # Parcelas
                    if not relatorio["parcelas"].empty:
                        st.write("### Parcelas")
                        df_display = relatorio["parcelas"].copy()
                        df_display["valor_parcela"] = df_display[
                            "valor_parcela"
                        ].apply(lambda x: f"R$ {x:,.2f}")
                        df_display["valor_pago"] = df_display[
                            "valor_pago"
                        ].apply(
                            lambda x: f"R$ {x:,.2f}"
                            if pd.notna(x)
                            else ""
                        )

                        st.dataframe(df_display, use_container_width=True, hide_index=True)
                else:
                    st.error("Fornecedor não encontrado.")
        else:
            st.info("Nenhum fornecedor cadastrado ainda.")


def main():
    """Função principal"""

    if not st.session_state.logged_in:
        login_page()
    else:
        # Sidebar
        with st.sidebar:
            st.title("💰 Controle Financeiro")
            st.write(
                f"**Usuário:** {st.session_state.user['nome_completo']}"
            )
            st.divider()

            menu_option = st.radio(
                "Menu",
                [
                    "Dashboard",
                    "Fornecedores",
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

        # Conteúdo principal
        if menu_option == "Dashboard":
            pagina_dashboard()
        elif menu_option == "Fornecedores":
            pagina_fornecedores()
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
