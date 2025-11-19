@echo off
echo ========================================
echo  Iniciando Controle Financeiro
echo ========================================
echo.

if not exist venv (
    echo ERRO: Ambiente virtual nao encontrado!
    echo Execute primeiro: instalar_windows.bat
    pause
    exit /b 1
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Iniciando aplicacao...
echo.
echo A aplicacao abrira no navegador em: http://localhost:8501
echo.
echo Para parar a aplicacao, pressione Ctrl+C
echo.

streamlit run app.py
