@echo off

setlocal enabledelayedexpansion
pushd .
cd ..
set apikey=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzay1zdmNhY2N0LWszUE5wSVhvX0xFWHBFWWpNWDZIcmxtNTdfSUtMRS1xek8xMlh1dGhWYXFKeDV6VEw3N2lUM0JsYmtGSnUtcG5OdmNWSVZQNU5qSnlzMFlSTDB1TS10MktkRy11QVo3TUtkM0NtNWx6T1JoMmI0Y0EifQ.jds9Gy603ivwpzNkh_x-4170QIxq9lwccGkEXPRrn30
set wurl=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJodHRwczovL2RtbnNra3F0cWdzYWV0aWlxcncuYzAudXMtZWFzdDEuZ2NwLndlYXZpYXRlLmNsb3VkIn0.Ib61b6RyTtSIZ8E22RqYofY1d3eMQJuF_ZWx-gzMtu8
set wkey=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJvcVBTTGhTZ3IzT01kWFltNnZTdGs3WW9jUU9BcnpYTHpNTTcifQ.GJRGldNQgQ5Utz6j9GVXOPKCaWoWzny5roB3ArIsYUo
set model=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJncHQtMy41LXR1cmJvIn0.ZHvSZD1eh8s3kH-ARH-Ac3FpOCliR-uYlBWU3Uecr1w
set propsFile=ApplicareController.props
set serverIp=0.0.0.0
set protocol=http
set dbhost=localhost
set dbport=3306
set database=applicare
set dbUsername=root
set dbPassword=root
set dbtables=business_transaction,intellitrace_errors,monitor_data,process_details,server,server_details,slow_txn,txn,txn_slow,http_errors,oshistory_detail
set dbtype=mysql
set mongodbconstr="mongodb://%serverIp%:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.10"
set authdbhost=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vbXlzcWwubXlzcWwuZGF0YWJhc2UuYXp1cmUuY29tIn0.mtuz_M5U6ko1YwbIguL3xSUybmg42b-By4_bQNTIY7I
set authdbport=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMzA2In0.KhR3z5a_t-8k-R6OTiG2WdsaX69VKNLqSEwdcfZwJrw
set authdbuser=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhcHBsaWNhcmVfc2FhcyJ9.frDf1iIRnEnd_ymoxxDQ_zzvJE3Y6OhvJlSgNPnfCe0
set authdbpassword=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJBcmN0ZWNoMDEifQ.KVGXF4jChvo60DmNlri7h4fHvpSKvK4ceeciqQgqn5o
set authdb=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vIn0.JqhKus2y59SHbeHkJwILDl5BISFWVabbp8mr8pLIuSQ

if not exist "%propsFile%" (
    set propsFile=Applicare.props
)

if exist "%propsFile%" (
    rem Extract serverIp value
    for /f "tokens=2 delims==" %%A in ('findstr "applicare.serverIP" "%propsFile%"') do (
        set serverIp=%%A
    )

    rem Extract serverSSL value to determine protocol
    for /f "tokens=2 delims==" %%B in ('findstr "applicare.serverSSL" "%propsFile%"') do (
        if /I "%%B"=="true" (
            set protocol=https
        )
    )

    rem Extract dburl value
    for /f "tokens=2 delims==" %%C in ('findstr "applicare.dburl" "%propsFile%"') do (
        set dburl=%%C
    )
	
	rem Extract dbUsername value
    for /f "tokens=2 delims==" %%D in ('findstr "applicare.dbUsername" "%propsFile%"') do (
        set dbUsername=%%D
    )
    
    rem Remove the prefix up to "jdbc:mysql://"
    set dburl=!dburl:jdbc\:mysql\://=!
    set dburl=!dburl:jdbc:mysql://=!

    rem Extract dbhost, dbport, and database name using delimiters
    for /f "tokens=1,2 delims=/:?" %%D in ("!dburl!") do (
        set dbhost=%%D
        set portAndDb=%%E
    )
    
    rem Remove trailing backslash from dbhost if it exists
    if "!dbhost:~-1!"=="\" (
        set dbhost=!dbhost:~0,-1!
    )
	
    rem Extract the dbport and database name from the remaining part
    for /f "tokens=1 delims=/" %%F in ("!portAndDb!") do (
        set dbport=%%F
    )  
	
	rem Extract the part after the port number (3306) using slash as the delimiter
	for /f "tokens=2 delims=/" %%G in ("!dburl!") do (
		set dbAndParams=%%G
	)

	rem Extract the database name before the question mark, if present
	for /f "tokens=1 delims=?" %%H in ("!dbAndParams!") do (
		set database=%%H
	)
	
	if "%dbPassword%"=="" (
		rem Check if an argument is provided
		if "%~1"=="" (
			rem No argument provided, prompt for the database password
			set /p dbPassword="Please enter the database password: "
		) else (
			rem Use the provided argument as the database password
			set dbPassword=%~1
		)
	)
	
	echo Server IP: !serverIp!
	echo Protocol: !protocol!
	echo DBHost: !dbhost!
	echo DBPort: !dbport!
	echo Database: !database!
	echo DBUsername: !dbUsername!
	echo DBPassword: !dbPassword!
	
)

popd

echo Setup Backend Environments...

set "ENV_FILE=backend\.env"

:: Create the backend directory if it doesn't exist
if not exist "backend" (
    mkdir backend
)

:: Write content to the backend .env file
(
    echo DB_HOST="%dbhost%"
    echo DB_PORT="%dbport%"
    echo DB_USER="%dbUsername%"
    echo DB_PASSWORD="%dbPassword%"
    echo DB="%database%"
	echo DB_TABLES="%dbtables%"
	echo DB_MS="%dbtype%"
    echo FRONTEND_API_URL="%protocol%://%serverIp%:3000"
    echo BACKEND_API_URL="%protocol%://%serverIp%:8000"
    echo JWT_SECRET_KEY="d8d8dd321e08dd2e2dd6fdf2f07e2ff3"
    echo JWT_REFRESH_SECRET_KEY="47eacd8a01ee705177f1678d675884cf"
    echo MONGO_CONNECTION_STRING=%mongodbconstr%
    echo MY_EMAIL_PASSWORD=""
    echo MY_EMAIL=""
    echo EMAIL_APP_PASSWORD=""
    echo OPENAI_API_KEY="%apikey%"
    echo MODEL="%model%"
	echo WEAVIATE_URL="%wurl%"
	echo WEAVIATE_API_KEY="%wkey%"
    echo AUTH_DB_HOST="%authdbhost%"
    echo AUTH_DB_PORT="%authdbport%"
    echo AUTH_DB_USER="%authdbuser%"
    echo AUTH_DB_PASSWORD="%authdbpassword%"
    echo AUTH_DB="%authdb%"
) > "%ENV_FILE%"

echo Environment variables written to %ENV_FILE%

echo Setup Frontend Environments...

set "ENV_FILE_DEV=frontend\.env"

:: Create the frontend directory if it doesn't exist
if not exist "frontend" (
    mkdir frontend
)

:: Write content to the frontend .env file
(
    echo REACT_APP_BACKEND_API_URL="%protocol%://%serverIp%:8000"
    echo REACT_APP_FRONTEND_API_URL="%protocol%://%serverIp%:3000"
    echo REACT_APP_WEBSOCKET_URL="ws://%serverIp%:8000"
) > "%ENV_FILE_DEV%"

echo Environment variables written to %ENV_FILE_DEV%
