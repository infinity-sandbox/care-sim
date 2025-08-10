@echo off

:: Path to the version file
set VERSION_FILE=backend\version

:: Set the version file to be read and writable
attrib +R %VERSION_FILE%

:: Read current version from the version file
for /F "tokens=1" %%A in (%VERSION_FILE%) do set current_version=%%A

:: Set build date
for /F %%A in ('powershell -command "Get-Date -Format yyyyMMddHHmmss"') do set build_date=%%A

:: Function to increment the version number
:increment_version
for /F "tokens=1,2,3 delims=." %%a in ("%current_version%") do (
    set major=%%a
    set minor=%%b
    set patch=%%c
)

:: Increment patch version
if %patch% lss 99 (
    set /A patch=patch+1
) else if %minor% lss 99 (
    set /A minor=minor+1
    set patch=0
) else if %major% lss 9 (
    set /A major=major+1
    set minor=0
    set patch=0
) else (
    echo Version limit reached!
    exit /b 1
)

set new_version=%major%.%minor%.%patch%

:: Write the new version and build date to the version file
echo %new_version% > %VERSION_FILE%
echo %build_date% >> %VERSION_FILE%

:: Check if the tag already exists
git rev-parse "v%new_version%" >nul 2>&1
if not errorlevel 1 (
    echo Tag v%new_version% already exists. Skipping tag creation.
) else (
    :: Create a new Git tag and push it
    git tag -a "v%new_version%" -m "Version %new_version%"
    git push origin "v%new_version%"
    echo Updated version to %new_version% and created tag v%new_version%
)

exit /b 0
