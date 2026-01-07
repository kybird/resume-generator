@echo off
setlocal

:: Check if .env exists
if not exist .env (
    echo [WARN] .env file not found! Copying .env.example to .env...
    copy .env.example .env
    echo Please edit .env with your configuration.
    pause
    exit /b
)

:MENU
cls
echo ==========================================
echo    Career Statement Generator Launcher
echo ==========================================
echo 1. Run Local CLI Application
echo 2. Run MCP Server (FastMCP)
echo 3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto RUN_CLI
if "%choice%"=="2" goto RUN_MCP
if "%choice%"=="3" goto ALL_DONE

echo Invalid choice.
pause
goto MENU

:RUN_CLI
echo.
echo Starting Local CLI...
:: Execute as module from root to preserve package structure
python -m career_writer.main
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application crashed or exited with error.
    pause
)
goto MENU

:RUN_MCP
echo.
echo Starting MCP Server...
echo Use 'fastmcp run mcp_server.py' manually if you want advanced options.
echo Press Ctrl+C to stop the server.
echo.
fastmcp run mcp_server.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] MCP Server failed.
    pause
)
goto MENU

:ALL_DONE
endlocal
