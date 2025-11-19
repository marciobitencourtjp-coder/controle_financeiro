# 💰 Sistema de Controle Financeiro

Sistema completo de controle financeiro pessoal multi-usuário desenvolvido em Python com Streamlit e SQLite.

## 📋 Características Principais

### Autenticação e Segurança
- Sistema multi-usuário com login e senha
- Senhas criptografadas com bcrypt
- Isolamento completo de dados entre usuários
- Cada usuário acessa apenas suas próprias informações

### Gestão de Fornecedores
- Cadastro completo de fornecedores
- Informações: Nome, CPF/CNPJ, Telefone, Email
- Ativação/Desativação de fornecedores
- Histórico de transações por fornecedor

### Lançamento de Débitos
- Múltiplas formas de pagamento: À Vista e A Prazo
- Tipos de documento suportados:
  - Carnê
  - Promissória
  - Boleto Bancário
  - Cartão de Crédito (com seleção de bandeira)
  - Cartão de Débito (com seleção de bandeira)
  - Dinheiro
  - PIX
  - Financiamento (até 360 parcelas)
- Geração automática de parcelas
- Divisão automática do valor total
- Vencimento padrão: 30 dias entre parcelas (editável)
- Status automático: Aberto, Pago, Vencido, Cancelado

### Lançamento de Créditos
- Tipos de crédito: Salário, Premiação, 13º Salário, Férias, Outros
- Data de recebimento personalizável
- Descrição e observações

### Gestão de Parcelas
- Visualização de todas as parcelas
- Filtros por fornecedor, status e período
- Baixa de parcelas (marcação como pago)
- Atualização automática de status vencido
- Alertas de parcelas próximas do vencimento

### Relatórios Financeiros
- **Conta Corrente**: Visualização tipo extrato bancário
  - Créditos em verde
  - Débitos em vermelho
  - Saldo acumulado
  - Filtros por período e fornecedor
- **Relatório Mensal**: Débitos agrupados por mês
- **Relatório por Fornecedor**: Análise detalhada por fornecedor com estatísticas

### Dashboard
- Resumo financeiro em tempo real
- Métricas de créditos, débitos e saldo
- Parcelas próximas do vencimento (30 dias)
- Alertas de parcelas vencidas

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### Passo 1: Instalar Dependências

```bash
pip install -r requirements.txt
```

### Passo 2: Executar a Aplicação

```bash
streamlit run app.py
```

A aplicação será aberta automaticamente no navegador em `http://localhost:8501`

## 📁 Estrutura do Projeto

```
controle_financeiro/
│
├── app.py                      # Aplicação principal Streamlit
├── database.py                 # Gerenciamento do banco de dados
├── auth.py                     # Autenticação e usuários
├── cadastros.py                # Módulo de cadastros
├── debitos.py                  # Módulo de débitos e parcelas
├── creditos.py                 # Módulo de créditos
├── relatorios.py               # Módulo de relatórios
├── controle_financeiro.db      # Banco de dados SQLite (gerado automaticamente)
├── requirements.txt            # Dependências do projeto
└── README.md                   # Esta documentação
```

## 🗄️ Estrutura do Banco de Dados

### Tabelas Principais

**usuarios**
- Armazena informações dos usuários do sistema
- Senhas criptografadas com bcrypt

**fornecedores**
- Cadastro de fornecedores por usuário
- Isolamento de dados por usuario_id

**lancamentos_debito**
- Registro de compras e débitos
- Vinculado a fornecedor, forma de pagamento e tipo de documento

**parcelas_debito**
- Parcelas geradas automaticamente
- Controle de status (Aberto, Pago, Vencido, Cancelado)
- Datas de vencimento e pagamento

**lancamentos_credito**
- Registro de receitas e créditos
- Tipos personalizáveis

### Tabelas Auxiliares

- **formas_pagamento**: À Vista, A Prazo
- **tipos_documento**: Carnê, Boleto, Cartão, PIX, etc.
- **bandeiras_cartao**: Visa, Mastercard, Elo, etc.
- **status_documento**: Aberto, Pago, Vencido, Cancelado
- **tipos_credito**: Salário, Premiação, 13º, Férias, Outros

## 📖 Guia de Uso

### 1. Primeiro Acesso

1. Acesse a aplicação
2. Clique na aba "Criar Conta"
3. Preencha os dados:
   - Usuário (único no sistema)
   - Nome Completo
   - Email (opcional)
   - Senha e confirmação
4. Clique em "Criar Conta"
5. Faça login com suas credenciais

### 2. Cadastrar Fornecedores

1. No menu lateral, clique em "Fornecedores"
2. Vá para a aba "Cadastrar Novo"
3. Preencha o nome (obrigatório) e demais informações
4. Clique em "Cadastrar Fornecedor"

### 3. Lançar um Débito

1. No menu lateral, clique em "Lançar Débito"
2. Selecione o fornecedor
3. Escolha a forma de pagamento (À Vista ou A Prazo)
4. Selecione o tipo de documento
5. Se for cartão, selecione a bandeira
6. Informe o valor total
7. Digite a descrição da compra
8. Se permitir parcelamento, informe a quantidade de parcelas
9. Defina a data de vencimento da primeira parcela (padrão: 30 dias)
10. Adicione observações se necessário
11. Clique em "Lançar Débito"

**O sistema irá:**
- Dividir automaticamente o valor total pelo número de parcelas
- Gerar todas as parcelas com vencimento de 30 em 30 dias
- Marcar todas como status "Aberto"

### 4. Lançar um Crédito

1. No menu lateral, clique em "Lançar Crédito"
2. Selecione o tipo de crédito
3. Informe o valor
4. Digite a descrição
5. Defina a data de recebimento
6. Adicione observações se necessário
7. Clique em "Lançar Crédito"

### 5. Gerenciar Parcelas

1. No menu lateral, clique em "Gestão de Parcelas"
2. Use os filtros para encontrar parcelas específicas:
   - Por fornecedor
   - Por status
   - Por período
3. Para baixar uma parcela (marcar como paga):
   - Clique no botão "✅ Baixar" ao lado da parcela
   - O sistema registrará a data de pagamento como hoje
   - O status mudará para "Pago"

### 6. Visualizar Relatórios

#### Conta Corrente
1. Acesse "Relatórios" no menu
2. Vá para a aba "Conta Corrente"
3. Defina o período (data início e fim)
4. Opcionalmente, filtre por fornecedor
5. Clique em "Gerar Relatório"
6. Visualize:
   - Coluna de Créditos (valores em verde)
   - Coluna de Débitos (valores em vermelho)
   - Coluna de Saldo (acumulado)

#### Relatório Mensal
1. Acesse "Relatórios" no menu
2. Vá para a aba "Mensal"
3. Selecione o ano e o mês
4. Clique em "Gerar Relatório"
5. Visualize todos os débitos do mês com seus status

#### Relatório por Fornecedor
1. Acesse "Relatórios" no menu
2. Vá para a aba "Por Fornecedor"
3. Selecione o fornecedor
4. Opcionalmente, ative o filtro de período
5. Clique em "Gerar Relatório"
6. Visualize:
   - Informações do fornecedor
   - Estatísticas (total de parcelas, valores, etc.)
   - Lista detalhada de todas as parcelas

### 7. Dashboard

O Dashboard é atualizado automaticamente e mostra:
- Total de créditos no período
- Total de débitos no período
- Valor em aberto (parcelas não pagas)
- Saldo atual
- Parcelas próximas do vencimento (30 dias)

**Importante:** O sistema atualiza automaticamente o status das parcelas para "Vencido" quando a data de vencimento passa e o status ainda está como "Aberto".

## 🔐 Segurança

- Todas as senhas são criptografadas com bcrypt antes de serem armazenadas
- Cada usuário tem acesso apenas aos seus próprios dados
- Todas as consultas ao banco de dados incluem validação de usuario_id
- Não há possibilidade de um usuário acessar dados de outro

## 💡 Dicas de Uso

1. **Cadastre fornecedores antes de lançar débitos** - O sistema exige pelo menos um fornecedor cadastrado

2. **Use descrições claras** - Facilita a identificação posterior nos relatórios

3. **Verifique o Dashboard regularmente** - Para acompanhar parcelas próximas do vencimento

4. **Use os filtros nos relatórios** - Para análises específicas por período ou fornecedor

5. **Baixe as parcelas assim que pagar** - Mantém o controle atualizado

6. **Financiamentos longos** - O sistema suporta até 360 parcelas (30 anos)

## 🛠️ Manutenção

### Backup do Banco de Dados

O banco de dados está no arquivo `controle_financeiro.db`. Para fazer backup:

```bash
cp controle_financeiro.db controle_financeiro_backup_$(date +%Y%m%d).db
```

### Resetar o Banco de Dados

Para começar do zero (CUIDADO: apaga todos os dados):

```bash
rm controle_financeiro.db
python3 database.py
```

## 📊 Funcionalidades Automáticas

1. **Geração de Parcelas**: Ao criar um débito parcelado, o sistema gera automaticamente todas as parcelas

2. **Cálculo de Valores**: O valor de cada parcela é calculado automaticamente, com ajuste na última parcela para compensar arredondamentos

3. **Status Vencido**: Parcelas com status "Aberto" que passam da data de vencimento são automaticamente marcadas como "Vencido"

4. **Saldo Acumulado**: Nos relatórios de conta corrente, o saldo é calculado automaticamente linha a linha

5. **Datas de Vencimento**: Por padrão, as parcelas vencem de 30 em 30 dias a partir da primeira parcela

## 🎨 Interface

A interface foi desenvolvida com Streamlit e possui:
- Design limpo e profissional
- Cores intuitivas (verde para créditos, vermelho para débitos)
- Navegação por menu lateral
- Filtros e buscas em todas as telas
- Métricas visuais no dashboard
- Tabelas responsivas

## 📝 Observações Importantes

- O sistema é **local** e roda na sua máquina
- Os dados ficam armazenados no arquivo SQLite
- Não há limite de usuários, fornecedores ou lançamentos
- Suporta parcelamentos de 1 até 360 meses
- Todas as datas são editáveis
- Os valores suportam centavos (2 casas decimais)

## 🆘 Solução de Problemas

**Erro ao iniciar a aplicação:**
- Verifique se todas as dependências estão instaladas: `pip install -r requirements.txt`
- Certifique-se de estar no diretório correto

**Banco de dados corrompido:**
- Faça backup do arquivo `.db`
- Delete o arquivo `controle_financeiro.db`
- Execute `python3 database.py` para criar um novo

**Esqueci minha senha:**
- Não há recuperação de senha implementada
- Você precisará criar um novo usuário ou acessar diretamente o banco de dados

## 📄 Licença

Este sistema foi desenvolvido para uso pessoal e educacional.

## 🤝 Suporte

Para dúvidas ou problemas, consulte esta documentação ou revise o código-fonte comentado.

---

**Desenvolvido com Python 3.11, Streamlit e SQLite**
