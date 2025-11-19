@echo off
echo ========================================
echo  Instalacao do Sistema Controle Financeiro
echo ========================================
echo.

echo [1/6] Verificando Python...
python --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Instale Python em: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo OK!
echo.

echo [2/6] Atualizando pip...
python -m pip install --upgrade pip
echo.

echo [3/6] Criando ambiente virtual...
if exist venv (
    echo Ambiente virtual ja existe. Pulando...
) else (
    python -m venv venv
    echo Ambiente virtual criado!
)
echo.

echo [4/6] Ativando ambiente virtual...
call venv\Scripts\activate.bat
echo.

echo [5/6] Instalando bibliotecas (isso pode demorar)...
echo.
echo Instalando pandas...
pip install pandas==2.0.3
echo.
echo Instalando bcrypt...
pip install bcrypt==4.0.1
echo.
echo Instalando streamlit...
pip install streamlit==1.28.0
echo.

echo [6/6] Verificando instalacao...
python -c "import pandas; import bcrypt; import streamlit; print('Todas as bibliotecas instaladas com sucesso!')"
if errorlevel 1 (
    echo.
    echo ERRO na instalacao!
    echo Consulte o arquivo INSTALACAO_WINDOWS.md para solucoes.
    pause
    exit /b 1
)
echo.

echo ========================================
echo  INSTALACAO CONCLUIDA COM SUCESSO!
echo ========================================
echo.
echo Para executar o sistema:
echo 1. venv\Scripts\activate
echo 2. streamlit run app.py
echo.
pause
