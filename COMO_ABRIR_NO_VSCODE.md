# 💻 Como Abrir o Projeto no VS Code

## Opção 1: Abrir Pasta no VS Code

1. Abra o **VS Code**
2. Clique em **File** → **Open Folder** (ou `Ctrl+K Ctrl+O`)
3. Navegue até a pasta `controle_financeiro`
4. Clique em **Selecionar Pasta**

## Opção 2: Via Terminal

```bash
cd /caminho/para/controle_financeiro
code .
```

## Opção 3: Arrastar e Soltar

1. Abra o **VS Code**
2. Arraste a pasta `controle_financeiro` para a janela do VS Code

---

## Configuração Recomendada no VS Code

### Extensões Úteis

Instale estas extensões para melhor experiência:

1. **Python** (Microsoft) - Suporte completo para Python
2. **Pylance** (Microsoft) - IntelliSense avançado
3. **SQLite Viewer** - Visualizar o banco de dados
4. **Better Comments** - Comentários coloridos

### Como Instalar Extensões

1. Clique no ícone de **Extensões** na barra lateral (ou `Ctrl+Shift+X`)
2. Pesquise o nome da extensão
3. Clique em **Install**

---

## Executar o Projeto no VS Code

### Método 1: Terminal Integrado

1. Abra o terminal integrado: **Terminal** → **New Terminal** (ou `` Ctrl+` ``)
2. Execute:
   ```bash
   streamlit run app.py
   ```

### Método 2: Botão de Play (se configurado)

1. Abra o arquivo `app.py`
2. Clique no botão ▶️ no canto superior direito
3. Selecione "Run Python File"

---

## Estrutura do Projeto no VS Code

Você verá esta estrutura na barra lateral:

```
CONTROLE_FINANCEIRO/
│
├── 📄 app.py                    ← Arquivo principal
├── 📄 database.py               ← Banco de dados
├── 📄 auth.py                   ← Autenticação
├── 📄 cadastros.py              ← Cadastros
├── 📄 debitos.py                ← Débitos
├── 📄 creditos.py               ← Créditos
├── 📄 relatorios.py             ← Relatórios
│
├── 🗄️ controle_financeiro.db   ← Banco SQLite
│
├── 📖 README.md                 ← Documentação completa
├── 📖 INICIO_RAPIDO.md          ← Guia rápido
├── 📖 COMO_ABRIR_NO_VSCODE.md   ← Este arquivo
│
├── 📋 requirements.txt          ← Dependências
└── 🚫 .gitignore                ← Arquivos ignorados pelo Git
```

---

## Dicas de Uso no VS Code

### 1. Atalhos Úteis

- `Ctrl+P` - Buscar arquivo rapidamente
- `Ctrl+Shift+F` - Buscar em todos os arquivos
- `Ctrl+B` - Mostrar/ocultar barra lateral
- `Ctrl+J` - Mostrar/ocultar painel inferior
- `Ctrl+` ` - Abrir terminal
- `F5` - Iniciar debug

### 2. Visualizar o Banco de Dados

Se você instalou a extensão **SQLite Viewer**:

1. Clique com botão direito em `controle_financeiro.db`
2. Selecione **"Open Database"**
3. Explore as tabelas e dados

### 3. Formatar Código Automaticamente

1. Instale a extensão **Black Formatter**
2. Pressione `Shift+Alt+F` para formatar o arquivo atual

### 4. IntelliSense (Autocompletar)

O VS Code oferece sugestões automáticas enquanto você digita:
- Nomes de funções
- Parâmetros
- Imports
- Variáveis

### 5. Debug

Para debugar o código:

1. Coloque um breakpoint clicando à esquerda do número da linha
2. Pressione `F5` para iniciar o debug
3. Use os controles de debug na parte superior

---

## Instalar Dependências no VS Code

### Abra o terminal integrado e execute:

```bash
pip install -r requirements.txt
```

### Ou, se tiver múltiplas versões do Python:

```bash
python3 -m pip install -r requirements.txt
```

---

## Executar a Aplicação

### No terminal integrado do VS Code:

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`

---

## Editar o Código

### Arquivos Principais para Edição:

- **app.py** - Interface do usuário (Streamlit)
- **database.py** - Estrutura do banco de dados
- **debitos.py** - Lógica de débitos e parcelas
- **creditos.py** - Lógica de créditos
- **relatorios.py** - Geração de relatórios

### Ao Editar:

1. Salve o arquivo (`Ctrl+S`)
2. O Streamlit detecta mudanças automaticamente
3. Clique em **"Rerun"** no navegador para ver as alterações

---

## Criar um Ambiente Virtual (Recomendado)

### Windows:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### No VS Code:

1. Pressione `Ctrl+Shift+P`
2. Digite "Python: Select Interpreter"
3. Selecione o interpretador do ambiente virtual

---

## Solução de Problemas no VS Code

### Problema: "Python não encontrado"

**Solução:**
1. Instale Python 3.11 ou superior
2. No VS Code, pressione `Ctrl+Shift+P`
3. Digite "Python: Select Interpreter"
4. Selecione a versão correta do Python

### Problema: "Módulo não encontrado"

**Solução:**
```bash
pip install -r requirements.txt
```

### Problema: "Streamlit não reconhecido"

**Solução:**
```bash
pip install streamlit
```

---

## Recursos Adicionais

### Documentação Oficial:
- [VS Code Python](https://code.visualstudio.com/docs/python/python-tutorial)
- [Streamlit Docs](https://docs.streamlit.io)
- [SQLite Docs](https://www.sqlite.org/docs.html)

### Atalhos do VS Code:
- [Keyboard Shortcuts (Windows)](https://code.visualstudio.com/shortcuts/keyboard-shortcuts-windows.pdf)
- [Keyboard Shortcuts (Mac)](https://code.visualstudio.com/shortcuts/keyboard-shortcuts-macos.pdf)
- [Keyboard Shortcuts (Linux)](https://code.visualstudio.com/shortcuts/keyboard-shortcuts-linux.pdf)

---

**Pronto para desenvolver! 🚀**

Qualquer dúvida, consulte o README.md ou INICIO_RAPIDO.md
