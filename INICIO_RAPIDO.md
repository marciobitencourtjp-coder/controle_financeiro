# 🚀 Guia de Início Rápido - Controle Financeiro

## Instalação em 3 Passos

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Executar a Aplicação
```bash
streamlit run app.py
```

### 3. Acessar no Navegador
A aplicação abrirá automaticamente em: `http://localhost:8501`

---

## Primeiros Passos

### 1️⃣ Criar sua Conta
1. Clique na aba **"Criar Conta"**
2. Preencha: Usuário, Nome Completo, Senha
3. Clique em **"Criar Conta"**
4. Faça **Login** com suas credenciais

### 2️⃣ Cadastrar um Fornecedor
1. Menu lateral → **"Fornecedores"**
2. Aba **"Cadastrar Novo"**
3. Digite o nome do fornecedor
4. Clique em **"Cadastrar Fornecedor"**

### 3️⃣ Lançar seu Primeiro Débito
1. Menu lateral → **"Lançar Débito"**
2. Selecione o **fornecedor**
3. Escolha **forma de pagamento** (À Vista ou A Prazo)
4. Selecione **tipo de documento** (Boleto, Cartão, PIX, etc.)
5. Digite o **valor total**
6. Digite uma **descrição**
7. Se parcelado, informe **quantas parcelas**
8. Clique em **"Lançar Débito"**

✅ **Pronto!** O sistema gerou automaticamente todas as parcelas!

### 4️⃣ Lançar um Crédito
1. Menu lateral → **"Lançar Crédito"**
2. Selecione o **tipo** (Salário, Premiação, etc.)
3. Digite o **valor**
4. Digite uma **descrição**
5. Clique em **"Lançar Crédito"**

### 5️⃣ Baixar uma Parcela (Marcar como Pago)
1. Menu lateral → **"Gestão de Parcelas"**
2. Encontre a parcela que você pagou
3. Clique no botão **"✅ Baixar"**

### 6️⃣ Ver seus Relatórios
1. Menu lateral → **"Relatórios"**
2. Escolha o tipo de relatório:
   - **Conta Corrente**: Extrato completo com saldo
   - **Mensal**: Débitos do mês
   - **Por Fornecedor**: Análise detalhada

---

## Funcionalidades Principais

### 💳 Tipos de Documento Suportados
- Carnê
- Promissória
- Boleto Bancário
- Cartão de Crédito (com bandeira)
- Cartão de Débito (com bandeira)
- Dinheiro
- PIX
- Financiamento (até 360 parcelas!)

### 💰 Tipos de Crédito
- Salário
- Premiação
- 13º Salário
- Férias
- Outros

### 📊 Status das Parcelas
- 🟠 **Aberto**: Ainda não venceu
- 🟢 **Pago**: Você já pagou
- 🔴 **Vencido**: Passou da data de vencimento
- ⚫ **Cancelado**: Cancelado manualmente

---

## Dicas Importantes

✅ **Cadastre fornecedores primeiro** - Você precisa de pelo menos um fornecedor para lançar débitos

✅ **Parcelas automáticas** - O sistema divide o valor e gera as parcelas automaticamente

✅ **Vencimento padrão** - 30 dias entre cada parcela (você pode editar)

✅ **Status automático** - Parcelas viram "Vencido" automaticamente após a data

✅ **Dashboard atualizado** - Veja sempre suas parcelas próximas do vencimento

✅ **Multi-usuário** - Cada pessoa vê apenas seus próprios dados

---

## Estrutura de Arquivos

```
controle_financeiro/
├── app.py                    # ← Execute este arquivo
├── database.py
├── auth.py
├── cadastros.py
├── debitos.py
├── creditos.py
├── relatorios.py
├── controle_financeiro.db    # ← Seu banco de dados
├── requirements.txt
└── README.md
```

---

## Comandos Úteis

### Executar a aplicação
```bash
streamlit run app.py
```

### Fazer backup do banco de dados
```bash
cp controle_financeiro.db backup_$(date +%Y%m%d).db
```

### Resetar o banco (CUIDADO: apaga tudo!)
```bash
rm controle_financeiro.db
python3 database.py
```

---

## Precisa de Ajuda?

📖 Consulte o **README.md** para documentação completa

🔍 Todos os módulos têm comentários explicativos no código

💡 Use o **Dashboard** para ver um resumo rápido das suas finanças

---

**Pronto para começar! 🎉**

Qualquer dúvida, consulte a documentação completa no arquivo README.md
