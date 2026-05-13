@echo off
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
timeout /t 5
color 7
cls
echo -- Kontrola winget nástroje --
where winget >nul 2>&1
if %errorlevel% neq 0 (
    echo winget není nainstalován.
    echo zkouším nainstalovat winget...

    powershell -Command Add-AppxPackage -RegisterByFamilyName -MainPackage Microsoft.DesktopAppInstaller_8wekyb3d8bbwe
    if %errorlevel% neq 0 (
        echo Nepodařilo se nainstalovat winget. Prosím nainstalujte Python ručně a poté spusťte tento skript znovu.
        pause
    )
)
timeout /t 5
cls
echo -- Kontrola Python 3.14 --
python --version 2>nul | findstr /r "Python 3\.14" >nul
if %errorlevel% neq 0 (
    echo Python 3.14 není nainstalován. Instaluji nyní...
    winget install Python.Python.3.14
    timeout /t 5
    GOTO :next1
)

echo Python 3.14 již byl nainstalován.

:next1

timeout /t 5
echo Instaluji požadavky...
pip install requests
echo Hotovo!
pause