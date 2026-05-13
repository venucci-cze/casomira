@echo off
setlocal enabledelayedexpansion
title Instalátor požadavků. Created by: SVM 2026
color 2
echo Created by: 
echo -----------------------------------------------------------------------------                                                                        
echo    SSSSSSSSSSSSSSS VVVVVVVV           VVVVVVVVMMMMMMMM               MMMMMMMM
echo  SS:::::::::::::::SV::::::V           V::::::VM:::::::M             M:::::::M
echo S:::::SSSSSS::::::SV::::::V           V::::::VM::::::::M           M::::::::M
echo S:::::S     SSSSSSSV::::::V           V::::::VM:::::::::M         M:::::::::M
echo S:::::S             V:::::V           V:::::V M::::::::::M       M::::::::::M
echo S:::::S              V:::::V         V:::::V  M:::::::::::M     M:::::::::::M
echo  S::::SSSS            V:::::V       V:::::V   M:::::::M::::M   M::::M:::::::M
echo   SS::::::SSSSS        V:::::V     V:::::V    M::::::M M::::M M::::M M::::::M
echo     SSS::::::::SS       V:::::V   V:::::V     M::::::M  M::::M::::M  M::::::M
echo        SSSSSS::::S       V:::::V V:::::V      M::::::M   M:::::::M   M::::::M
echo             S:::::S       V:::::V:::::V       M::::::M    M:::::M    M::::::M
echo             S:::::S        V:::::::::V        M::::::M     MMMMM     M::::::M
echo SSSSSSS     S:::::S         V:::::::V         M::::::M               M::::::M
echo S::::::SSSSSS:::::S          V:::::V          M::::::M               M::::::M
echo S:::::::::::::::SS            V:::V           M::::::M               M::::::M
echo  SSSSSSSSSSSSSSS               VVV            MMMMMMMM               MMMMMMMM
echo -----------------------------------------------------------------------------
timeout /t 2 >nul
cls

:: =========================
:: Kontrola winget
:: =========================

echo [INFO] Kontroluji winget...

where winget >nul 2>&1

if errorlevel 1 (
    color 0C
    echo [ERROR] winget nebyl nalezen!
    echo.
    echo Nainstalujte App Installer z Microsoft Store.
    echo.
    pause
    exit /b
)

color 0A
echo [OK] winget nalezen.
echo.

:: =========================
:: Kontrola Pythonu
:: =========================

echo [INFO] Kontroluji Python 3.14...

python --version 2>nul | findstr "3.14" >nul

if errorlevel 1 (
    echo [WARN] Python 3.14 není nainstalován.
    echo [INFO] Instaluji Python...

    winget install -e --id Python.Python.3.14

    if errorlevel 1 (
        color 0C
        echo [ERROR] Instalace Pythonu selhala!
        pause
        exit /b
    )
)

echo [OK] Python připraven.
echo.

:: =========================
:: Instalace knihoven
:: =========================

echo [INFO] Instaluji Python balíčky...

python -m pip install --upgrade pip
python -m pip install requests customtkinter

if errorlevel 1 (
    color 0C
    echo [ERROR] Instalace balíčků selhala.
    pause
    exit /b
)

:: =========================
:: Hotovo
:: =========================

color 0A
echo.
echo ==========================================
echo            HOTOVO!
echo ==========================================
echo.

pause
