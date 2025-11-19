# 🚀 Guia de Deploy - Controle Financeiro (Streamlit + Supabase)

Este guia detalha como hospedar seu aplicativo de Controle Financeiro na internet usando serviços gratuitos: **Supabase** (para o banco de dados PostgreSQL) e **Streamlit Community Cloud** (para o aplicativo web).

## 🎯 Pré-requisitos

1.  **Conta no GitHub:** Necessária para hospedar o código.
2.  **Conta no Supabase:** Para o banco de dados PostgreSQL gratuito.
3.  **Conta no Streamlit Community Cloud:** Para hospedar o aplicativo web.
4.  **Código-fonte atualizado:** O código que você recebeu já está adaptado para PostgreSQL.

---

## FASE 1: Configuração do Banco de Dados (Supabase)

O Supabase oferece um banco de dados PostgreSQL gratuito e é ideal para este projeto.

### 1. Criar um Projeto no Supabase

1.  Acesse o [Supabase Dashboard](https://app.supabase.com/) e clique em **"New Project"**.
2.  Escolha um nome para o projeto (ex: `controle-financeiro-db`).
3.  Defina uma senha forte para o banco de dados.
4.  Escolha a região mais próxima de você.
5.  Clique em **"Create new project"**.

### 2. Obter a String de Conexão

1.  No Dashboard do seu projeto, vá para **"Project Settings"** (ícone de engrenagem).
2.  Clique em **"Database"** no menu lateral.
3.  Role a tela até a seção **"Connection String"**.
4.  Copie a **"URI"** (ela começa com `postgresql://`).

A string de conexão terá o formato:
`postgresql://[USER]:[PASSWORD]@[HOST]:[PORT]/[DATABASE]`

### 3. Criar as Tabelas no Supabase

Você precisa executar o script de criação de tabelas no seu novo banco de dados.

1.  No Dashboard do Supabase, vá para **"SQL Editor"** (ícone de folha).
2.  Clique em **"New Query"**.
3.  **Copie e cole o conteúdo do arquivo `database.py`** (apenas a parte de criação de tabelas e inserção de dados padrão).
    - **Dica:** Você pode usar um cliente SQL (como DBeaver ou pgAdmin) para se conectar e executar o script `database.py` de forma mais fácil.
4.  **Execute o script** para criar as 10 tabelas e inserir os dados padrão (`formas_pagamento`, `status_documento`, etc.).

---

## FASE 2: Preparação do Código (GitHub)

### 1. Criar Repositório no GitHub

1.  Acesse o [GitHub](https://github.com/) e crie um **novo repositório privado** (ex: `controle-financeiro-app`).
2.  **Faça o upload de todos os arquivos** do seu projeto (`app.py`, `database.py`, `requirements.txt`, etc.) para este repositório.

### 2. Criar o Arquivo de Secrets

O Streamlit Cloud precisa de um arquivo de secrets para acessar o banco de dados.

1.  Crie uma pasta chamada `.streamlit` na raiz do seu projeto.
2.  Dentro dela, crie um arquivo chamado **`secrets.toml`**.
3.  Adicione o seguinte conteúdo, substituindo os valores pela sua string de conexão do Supabase (obtida no Passo 1.2):

```toml
# .streamlit/secrets.toml

[postgres]
user = "seu_usuario_supabase"
password = "sua_senha_supabase"
host = "seu_host_supabase"
port = 5432
database = "seu_database_supabase"
```

4.  **IMPORTANTE:** Adicione o arquivo `.streamlit/secrets.toml` ao seu arquivo **`.gitignore`** para garantir que ele **NÃO** seja enviado para o GitHub.

---

## FASE 3: Deploy no Streamlit Community Cloud

### 1. Conectar o GitHub

1.  Acesse o [Streamlit Community Cloud](https://share.streamlit.io/) e faça login com sua conta GitHub.
2.  Clique em **"New app"** no canto superior direito.

### 2. Configurar o Deploy

1.  **Repository:** Selecione o repositório que você criou (ex: `seu-usuario/controle-financeiro-app`).
2.  **Branch:** Selecione a branch principal (ex: `main`).
3.  **Main file path:** Digite `app.py`.
4.  **App URL:** Escolha um nome para a URL (ex: `controle-financeiro-seu-nome`).

### 3. Configurar Secrets

1.  Na seção **"Advanced settings"**, clique em **"Show advanced settings"**.
2.  **Copie o conteúdo do seu arquivo `.streamlit/secrets.toml`** (que você **NÃO** enviou para o GitHub).
3.  Cole o conteúdo na caixa de texto **"Secrets"** do Streamlit Cloud.

### 4. Finalizar o Deploy

1.  Clique em **"Deploy!"**.

O Streamlit Cloud irá instalar as dependências (`requirements.txt`) e iniciar seu aplicativo. O processo pode levar alguns minutos.

---

## ✅ Verificação Final

1.  Acesse a URL do seu aplicativo (ex: `https://share.streamlit.io/seu-usuario/controle-financeiro-seu-nome/main/app.py`).
2.  Tente **Criar uma Conta**.
3.  Se a conta for criada com sucesso, significa que a conexão com o Supabase está funcionando!
4.  Faça login e teste as funcionalidades.

---

## 💡 Dicas de Manutenção

- **Atualizar o Código:** Sempre que você fizer alterações no código e der `git push` para o GitHub, o Streamlit Cloud irá detectar e atualizar seu aplicativo automaticamente.
- **Monitorar o Banco:** Use o Dashboard do Supabase para monitorar o uso do seu banco de dados (o plano gratuito tem limites).
- **Logs:** Se o aplicativo falhar, verifique os logs no Dashboard do Streamlit Cloud.

---

**Este guia completo te dará todas as ferramentas para fazer o deploy do seu sistema de controle financeiro de forma segura e gratuita!**
