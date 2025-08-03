@echo off
:: YouTube Downloader Launcher for Windows
:: This script provides easy access to all downloader features

echo.
echo ================================
echo    YouTube Downloader
echo ================================
echo.

:menu
echo Choose an option:
echo.
echo 1. Command Line Interface (Interactive)
echo 2. Graphical User Interface (GUI)
echo 3. Batch Download from File
echo 4. Create Sample URLs File
echo 5. Run Examples
echo 6. Run Tests
echo 7. Setup/Install Requirements
echo 8. Exit
echo.

set /p choice=Enter your choice (1-8): 

if "%choice%"=="1" goto cli
if "%choice%"=="2" goto gui
if "%choice%"=="3" goto batch
if "%choice%"=="4" goto sample
if "%choice%"=="5" goto examples
if "%choice%"=="6" goto tests
if "%choice%"=="7" goto setup
if "%choice%"=="8" goto exit

echo Invalid choice. Please try again.
echo.
goto menu

:cli
echo.
echo Starting Command Line Interface...
python youtube_downloader.py
goto end

:gui
echo.
echo Starting Graphical User Interface...
python gui.py
goto end

:batch
echo.
set /p filename=Enter URLs filename (or press Enter for 'urls.txt'): 
if "%filename%"=="" set filename=urls.txt
echo Starting batch download from %filename%...
python batch_download.py "%filename%"
goto end

:sample
echo.
set /p filename=Enter filename for sample file (or press Enter for 'urls.txt'): 
if "%filename%"=="" set filename=urls.txt
echo Creating sample URLs file: %filename%...
python batch_download.py --create-sample "%filename%"
goto end

:examples
echo.
echo Running examples...
python examples.py
goto end

:tests
echo.
echo Running tests...
python test_downloader.py
goto end

:setup
echo.
echo Running setup...
python setup.py
goto end

:exit
echo.
echo Goodbye!
exit /b 0

:end
echo.
echo Press any key to return to menu...
pause >nul
echo.
goto menu
