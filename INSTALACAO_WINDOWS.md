# 🪟 Guia de Instalação no Windows - Por Fases

Este guia vai te ajudar a instalar as bibliotecas necessárias passo a passo, facilitando a identificação de problemas.

---

## ✅ Pré-requisitos

Antes de começar, verifique:

### 1. Versão do Python
```cmd
python --version
```
**Necessário:** Python 3.8 ou superior (recomendado 3.11+)

Se não tiver Python instalado:
- Baixe em: https://www.python.org/downloads/
- ⚠️ **IMPORTANTE**: Marque a opção "Add Python to PATH" durante a instalação

### 2. Atualizar pip
```cmd
python -m pip install --upgrade pip
```

---

## 📦 Instalação por Fases

### FASE 1: Criar e Ativar Ambiente Virtual

```cmd
cd caminho\para\controle_financeiro
python -m venv venv
venv\Scripts\activate
```

Você verá `(venv)` no início da linha do terminal quando ativado.

---

### FASE 2: Instalar Pandas

```cmd
pip install pandas
```

**Teste:**
```cmd
python -c "import pandas; print('Pandas OK:', pandas.__version__)"
```

Se der erro, tente:
```cmd
pip install pandas --no-cache-dir
```

---

### FASE 3: Instalar bcrypt

```cmd
pip install bcrypt
```

**Teste:**
```cmd
python -c "import bcrypt; print('bcrypt OK:', bcrypt.__version__)"
```

⚠️ **Se der erro no bcrypt:**

O bcrypt precisa de compiladores C++. Instale o Visual C++ Build Tools:
1. Baixe: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Instale apenas "Desktop development with C++"
3. Reinicie o terminal
4. Tente novamente: `pip install bcrypt`

**Alternativa (se ainda der erro):**
```cmd
pip install bcrypt --only-binary :all:
```

---

### FASE 4: Instalar Streamlit

```cmd
pip install streamlit
```

**Teste:**
```cmd
streamlit --version
```

Se der erro, tente:
```cmd
pip install streamlit --no-cache-dir
```

---

### FASE 5: Verificação Final

Execute este comando para verificar todas as bibliotecas:

```cmd
python -c "import pandas; import bcrypt; import streamlit; print('✅ Todas as bibliotecas instaladas com sucesso!')"
```

---

## 🚀 Executar a Aplicação

Depois de instalar tudo:

```cmd
cd caminho\para\controle_financeiro
venv\Scripts\activate
streamlit run app.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`

---

## 🔧 Solução de Problemas Comuns

### Problema 1: "python não é reconhecido"

**Solução:**
- Reinstale o Python marcando "Add Python to PATH"
- OU adicione manualmente ao PATH:
  - Painel de Controle → Sistema → Configurações Avançadas
  - Variáveis de Ambiente → PATH
  - Adicione: `C:\Users\SeuUsuario\AppData\Local\Programs\Python\Python311`

### Problema 2: "pip não é reconhecido"

**Solução:**
```cmd
python -m pip install --upgrade pip
```

### Problema 3: Erro de permissão

**Solução:**
Execute o CMD como Administrador:
- Clique com botão direito no CMD
- "Executar como Administrador"

### Problema 4: bcrypt não instala

**Soluções (tente nesta ordem):**

1. Instalar versão pré-compilada:
```cmd
pip install bcrypt --only-binary :all:
```

2. Instalar Visual C++ Build Tools:
   - https://visualstudio.microsoft.com/visual-cpp-build-tools/

3. Usar versão específica:
```cmd
pip install bcrypt==4.0.1
```

### Problema 5: Streamlit muito lento para instalar

**Solução:**
```cmd
pip install streamlit --no-cache-dir --timeout 1000
```

### Problema 6: Conflito de versões

**Solução - Limpar e reinstalar:**
```cmd
pip uninstall pandas bcrypt streamlit -y
pip cache purge
pip install pandas bcrypt streamlit
```

---

## 📋 Comandos Rápidos de Diagnóstico

### Verificar o que está instalado:
```cmd
pip list
```

### Verificar versão de uma biblioteca:
```cmd
pip show pandas
pip show bcrypt
pip show streamlit
```

### Desinstalar uma biblioteca:
```cmd
pip uninstall nome_da_biblioteca
```

### Reinstalar tudo do zero:
```cmd
pip uninstall pandas bcrypt streamlit -y
pip install pandas bcrypt streamlit
```

---

## 🎯 Instalação Alternativa (se nada funcionar)

### Opção 1: Usar Anaconda

1. Baixe o Anaconda: https://www.anaconda.com/download
2. Instale
3. Abra o Anaconda Prompt
4. Execute:
```cmd
conda create -n financeiro python=3.11
conda activate financeiro
conda install pandas
pip install bcrypt streamlit
```

### Opção 2: Usar versões específicas (mais estáveis)

Crie um arquivo `requirements_windows.txt`:
```
pandas==2.0.3
bcrypt==4.0.1
streamlit==1.28.0
```

Instale:
```cmd
pip install -r requirements_windows.txt
```

---

## ✅ Checklist de Instalação

Marque conforme for instalando:

- [ ] Python 3.8+ instalado
- [ ] pip atualizado
- [ ] Ambiente virtual criado
- [ ] Ambiente virtual ativado (vê `(venv)` no terminal)
- [ ] pandas instalado e testado
- [ ] bcrypt instalado e testado
- [ ] streamlit instalado e testado
- [ ] Aplicação executada com sucesso

---

## 📞 Ainda com Problemas?

Se mesmo seguindo este guia você tiver problemas:

1. **Anote a mensagem de erro completa**
2. **Verifique qual biblioteca está falhando**
3. **Tente a instalação alternativa com Anaconda**
4. **Use versões específicas mais antigas e estáveis**

---

## 🎓 Comandos Úteis para Lembrar

```cmd
# Ativar ambiente virtual
venv\Scripts\activate

# Desativar ambiente virtual
deactivate

# Atualizar pip
python -m pip install --upgrade pip

# Instalar biblioteca
pip install nome_biblioteca

# Listar instaladas
pip list

# Executar aplicação
streamlit run app.py
```

---

**Boa sorte com a instalação! 🚀**

Se seguir este guia passo a passo, você conseguirá identificar exatamente onde está o problema e resolvê-lo.
