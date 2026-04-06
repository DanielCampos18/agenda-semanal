@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ============================================
echo  Setup — Dashboard Comercial Externo
echo ============================================
echo.

:: Verificar Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python nao encontrado. Tentando instalar via winget...
    winget install Python.Python.3.12 --silent
    if %errorlevel% neq 0 (
        echo.
        echo ATENCAO: Instalacao automatica falhou.
        echo Instale manualmente em: https://www.python.org/downloads/
        echo Marque a opcao "Add Python to PATH" durante a instalacao.
        echo Depois execute este arquivo novamente.
        pause
        exit /b 1
    )
    echo Python instalado com sucesso!
) else (
    echo Python encontrado:
    python --version
)

echo.
echo Instalando dependencias...
python -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Setup concluido! Use atualizar.bat para
echo  gerar o dashboard.
echo ============================================
pause
