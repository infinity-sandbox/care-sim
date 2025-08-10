#!/bin/bash

set -e  # Exit on error
set -o pipefail  # Exit if any part of a pipeline fails

# Save the current directory and move one directory up
pushd . > /dev/null
cd ..

# Set default values
apikey=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzay1zdmNhY2N0LWszUE5wSVhvX0xFWHBFWWpNWDZIcmxtNTdfSUtMRS1xek8xMlh1dGhWYXFKeDV6VEw3N2lUM0JsYmtGSnUtcG5OdmNWSVZQNU5qSnlzMFlSTDB1TS10MktkRy11QVo3TUtkM0NtNWx6T1JoMmI0Y0EifQ.jds9Gy603ivwpzNkh_x-4170QIxq9lwccGkEXPRrn30
wurl=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJodHRwczovL2RtbnNra3F0cWdzYWV0aWlxcncuYzAudXMtZWFzdDEuZ2NwLndlYXZpYXRlLmNsb3VkIn0.Ib61b6RyTtSIZ8E22RqYofY1d3eMQJuF_ZWx-gzMtu8
wkey=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJvcVBTTGhTZ3IzT01kWFltNnZTdGs3WW9jUU9BcnpYTHpNTTcifQ.GJRGldNQgQ5Utz6j9GVXOPKCaWoWzny5roB3ArIsYUo
model=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJncHQtMy41LXR1cmJvIn0.ZHvSZD1eh8s3kH-ARH-Ac3FpOCliR-uYlBWU3Uecr1w
propsFile="ApplicareController.props"
serverIp="0.0.0.0"
protocol="http"
dbhost="localhost"
dbport="3306"
database="applicare"
dbUsername=""
dbPassword=""
dbtables="business_transaction,intellitrace_errors,monitor_data,process_details,server,server_details,slow_txn,txn,txn_slow,http_errors,oshistory_detail"
dbtype=mysql
mongodbconstr="mongodb://$serverIp:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.10"
authdbhost="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vbXlzcWwubXlzcWwuZGF0YWJhc2UuYXp1cmUuY29tIn0.mtuz_M5U6ko1YwbIguL3xSUybmg42b-By4_bQNTIY7I"
authdbport="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMzA2In0.KhR3z5a_t-8k-R6OTiG2WdsaX69VKNLqSEwdcfZwJrw"
authdbuser="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhcHBsaWNhcmVfc2FhcyJ9.frDf1iIRnEnd_ymoxxDQ_zzvJE3Y6OhvJlSgNPnfCe0"
authdbpassword="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJBcmN0ZWNoMDEifQ.KVGXF4jChvo60DmNlri7h4fHvpSKvK4ceeciqQgqn5o"
authdb="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vIn0.JqhKus2y59SHbeHkJwILDl5BISFWVabbp8mr8pLIuSQ"

# Check if the props file exists, fall back to Applicare.props
if [ ! -f "$propsFile" ]; then
    propsFile="Applicare.props"
fi

if [ -f "$propsFile" ]; then
    # Extract serverIp value
    serverIp=$(grep -m 1 "applicare.serverIP" "$propsFile" | cut -d'=' -f2 | tr -d '\r')

    # Extract serverSSL value to determine protocol
    if grep -q "applicare.serverSSL=true" "$propsFile"; then
        protocol="https"
    fi

    # Extract dburl value
    dburl=$(grep -m 1 "applicare.dburl" "$propsFile" | cut -d'=' -f2)

    # Extract dbUsername value
    dbUsername=$(grep -m 1 "applicare.dbUsername" "$propsFile" | cut -d'=' -f2 | tr -d '\r')

    # Remove the prefix up to "jdbc:mysql://"
    dburl=${dburl#jdbc:mysql://}

    # Extract dbhost, dbport, and database name using delimiters
    dbhost=$(echo "$dburl" | cut -d'/' -f1 | cut -d':' -f1)
    dbhost="${dbhost%\\}"
    dbport=$(echo "$dburl" | cut -d'/' -f1 | cut -d':' -f2)
    database=$(echo "$dburl" | cut -d'/' -f2)
    database="${database%%\?*}"
	
	if [ -z "$dbPassword" ]; then
		# Check if a command-line argument is provided for the password
		if [ -z "$1" ]; then
			# Prompt for the database password if not provided
			read -sp "Please enter the Applicare database password: " dbPassword
			echo ""
		else
			dbPassword="$1"
		fi
	fi

	# Display the extracted values
	echo "Server IP: $serverIp"
	echo "Protocol: $protocol"
	echo "DBHost: $dbhost"
	echo "DBPort: $dbport"
	echo "Database: $database"
	echo "DBUsername: $dbUsername"
	echo "DBPassword: $dbPassword"
fi

# Return to the previous directory
popd > /dev/null

# Setup Backend Environments
echo "Setting up Backend Environments..."

ENV_FILE="backend/.env"
mkdir -p backend

# Write content to the backend .env file
cat > "$ENV_FILE" <<EOL
DB_HOST="$dbhost"
DB_PORT="$dbport"
DB_USER="$dbUsername"
DB_PASSWORD="$dbPassword"
DB="$database"
DB_TABLES="$dbtables"
DB_MS="$dbtype"
FRONTEND_API_URL="$protocol://$serverIp:3000"
BACKEND_API_URL="$protocol://$serverIp:8000"
JWT_SECRET_KEY="d8d8dd321e08dd2e2dd6fdf2f07e2ff3"
JWT_REFRESH_SECRET_KEY="47eacd8a01ee705177f1678d675884cf"
MONGO_CONNECTION_STRING="$mongodbconstr"
MY_EMAIL_PASSWORD=""
MY_EMAIL=""
EMAIL_APP_PASSWORD=""
OPENAI_API_KEY="$apikey"
MODEL="$model"
WEAVIATE_URL="$wurl"
WEAVIATE_API_KEY="$wkey"
AUTH_DB_HOST="$authdbhost"
AUTH_DB_PORT="$authdbport"
AUTH_DB_USER="$authdbuser"
AUTH_DB_PASSWORD="$authdbpassword"
AUTH_DB="$authdb"
EOL

echo "Environment variables written to $ENV_FILE"

# Setup Frontend Environments
echo "Setting up Frontend Environments..."

ENV_FILE_DEV="frontend/.env"
mkdir -p frontend

# Write content to the frontend .env file
cat > "$ENV_FILE_DEV" <<EOL
REACT_APP_BACKEND_API_URL="$protocol://$serverIp:8000"
REACT_APP_FRONTEND_API_URL="$protocol://$serverIp:3000"
REACT_APP_WEBSOCKET_URL="ws://$serverIp:8000"
EOL

echo "Environment variables written to $ENV_FILE_DEV"

