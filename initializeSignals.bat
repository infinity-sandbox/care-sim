@echo off

REM Change to backend directory
cd backend
REM Change permissions (not applicable in Windows, but can be omitted)
REM You can execute install.bat directly instead of changing permissions
call install.bat

cd ..

cd frontend
REM Change permissions (not applicable in Windows, but can be omitted)
REM You can execute install.bat directly instead of changing permissions
call install.bat

REM List all running Docker containers
echo Listing all running containers...
docker ps
