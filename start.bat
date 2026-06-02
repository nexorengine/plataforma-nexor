@echo off
title NEXOR QUIZ ENGINE
color 0B
echo.
echo  =========================================
echo    NEXOR QUIZ ENGINE v3.0
echo    Sistema de Preparacao para Certificacoes
echo  =========================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERRO] Python nao encontrado.
    echo  Instale em: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check API Key
if "%ANTHROPIC_API_KEY%"=="" (
    echo  [CONFIG] Insira sua Anthropic API Key:
    set /p ANTHROPIC_API_KEY="  API Key: "
    echo.
)

:: Install dependencies
echo  [1/3] Verificando dependencias...
pip install -r requirements.txt --quiet --disable-pip-version-check

:: Start server
echo  [2/3] Iniciando servidor NEXOR...
echo  [3/3] Abrindo navegador...
echo.
echo  Acesse: http://localhost:8765
echo  Para encerrar: feche esta janela
echo.

:: Open browser after 2s delay
start /b cmd /c "timeout /t 2 >nul && start http://localhost:8765"

:: Run server
python server.py
pause
