@echo off
setlocal enabledelayedexpansion

REM Set the target directories
set "TARGET_DIR_BE=bin\win\backend"
set "TARGET_DIR_FE=bin\win\frontend"
set "ZIP_FILE=bin\win"

echo Backend directory: %TARGET_DIR_BE%
echo Frontend directory: %TARGET_DIR_FE%
echo Zip file location: %ZIP_FILE%.zip

REM Check if the zip file exists; if so, delete it
if exist "%ZIP_FILE%.zip" (
    echo Deleting existing zip file...
    del /f /q "%ZIP_FILE%.zip"
)

REM Check if the backend directory exists; if so, delete it
if exist "%TARGET_DIR_BE%" (
    echo Deleting backend directory...
    rmdir /s /q "%TARGET_DIR_BE%"
)

REM Check if the frontend directory exists; if so, delete it
if exist "%TARGET_DIR_FE%" (
    echo Deleting frontend directory...
    rmdir /s /q "%TARGET_DIR_FE%"
)

REM Recreate the directories
echo Recreating directories...
mkdir "%TARGET_DIR_BE%"
mkdir "%TARGET_DIR_FE%"

REM Copy all files (including hidden files) from backend and frontend to the target directories
xcopy /e /h /i /y backend\* "%TARGET_DIR_BE%\"
xcopy /e /h /i /y frontend\* "%TARGET_DIR_FE%\"

echo All files have been copied successfully!

REM Navigate into the backend target directory
cd /d "%TARGET_DIR_BE%" || exit /b 1

echo Deleting unwanted files and directories...
if exist "venv" rmdir /s /q venv
if exist "logs\logs.log" del /f /q logs\logs.log
if exist "docs" rmdir /s /q docs
if exist "htmlcov" rmdir /s /q htmlcov
if exist "test1" del /f /q test1
if exist "build" rmdir /s /q build
if exist "utils\dist" rmdir /s /q utils\dist

icacls logs /grant Everyone:F

REM Removing specific lines from .dockerignore
(for /f "tokens=*" %%a in ('findstr /v /r /c:"\*.pyc" /c:"\*.pyo" /c:"\*.pyd" /c:"__pycache__" ".dockerignore"') do echo %%a) > temp && move /y temp .dockerignore

REM Compile Python files to .pyc
python -m compileall . || (echo Failed to compile Python files and exit /b 1)

REM Move .pyc files out of __pycache__ directories and rename them
for /r %%i in (*.pyc) do (
    set "pyc_path=%%~dpi"
    set "py_file_name=%%~ni"
    
    REM Remove the __pycache__ from the directory path
    set "parent_dir=!pyc_path:__pycache__=!"
    
    REM Remove the .cpython-312 part from the filename
    set "renamed_file=!py_file_name:.cpython-312=!"
    
    REM Move and rename the .pyc file to the parent directory
    if not exist "!parent_dir!" mkdir "!parent_dir!"
    move "%%i" "!parent_dir!\!renamed_file!.pyc"
)

REM Delete all __pycache__ directories
for /d /r %%i in (__pycache__) do rmdir /s /q "%%i"

REM Deleting all .py files except setup.py
for /r %%i in (*.py) do (
    if /i not "%%~nxi"=="setup.py" del /f /q "%%i"
)

echo Conversion process to binary for the backend completed!

cd ..\frontend || (echo Failed to navigate to frontend directory & exit /b 1)

echo Deleting unwanted files from frontend...
if exist "build" rmdir /s /q build
if exist "node_modules" rmdir /s /q node_modules

echo Conversion process to binary for the frontend completed!

cd /d "%~dp0" || (echo Debug: Failed to return to the initial directory and exit /b 1)

REM Copying the two files from the script location to the bin/binary/ directory
echo Debug: Copying additional files from the script directory...
if exist "%~dp0initializeGenieSignals.bat" (
    copy /y "%~dp0initializeGenieSignals.bat" "%ZIP_FILE%\initializeGenieSignals.bat" || (echo Failed to copy initializeGenieSignals.bat & pause & exit /b 1)
) else (
    echo initializeGenieSignals.bat not found in %~dp0
)

if exist "%~dp0readme.md" (
    copy /y "%~dp0readme.md" "%ZIP_FILE%\readme.md" || (echo Failed to copy readme.md & pause & exit /b 1)
) else (
    echo readme.md not found in %~dp0
)

if exist "%~dp0setupEnv.bat" (
    copy /y "%~dp0setupEnv.bat" "%ZIP_FILE%\setupEnv.bat" || (echo Failed to copy setupEnv.bat & pause & exit /b 1)
) else (
    echo setupEnv.bat not found in %~dp0
)

REM List the directory contents to verify file copy
echo Debug: Listing contents of %ZIP_FILE% after copying...
dir "%ZIP_FILE%" || (echo Failed to list directory contents & pause & exit /b 1)

REM List the directory contents to verify file copy
echo Debug: Listing contents of %ZIP_FILE% after copying...
dir "%ZIP_FILE%" || (echo Failed to list directory contents & pause & exit /b 1)

REM Check if PowerShell is available
where powershell.exe >nul 2>nul || (echo PowerShell is not available, exiting... & pause & exit /b 1)

REM Create the ZIP file using PowerShell
echo Zipping the contents of %ZIP_FILE% into %ZIP_FILE%...
powershell -Command "Compress-Archive -Path '%ZIP_FILE%\*' -DestinationPath '%ZIP_FILE%' -Force" || (echo Failed to create ZIP file & pause & exit /b 1)

REM Verify the ZIP file creation
if exist "%ZIP_FILE%" (
    echo Zip file created successfully at %ZIP_FILE%.
) else (
    echo Failed to create the zip file at %ZIP_FILE%.
    pause
    exit /b 1
)

echo Script completed successfully.

endlocal