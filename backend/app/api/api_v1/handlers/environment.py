from fastapi import APIRouter, HTTPException, Header, status, Depends
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, Query
from app.schemas.env_schema import UserEnvPayload, AdminEnvPayload
from app.services.auth_service import AuthDatabaseService
from app.core.config import logger_settings
logger = logger_settings.get_logger(__name__)
import aiomysql
import asyncio
import aioodbc
import json
from app.services.database_service import (MySQLDatabaseService, 
                                           MariaDbDatabaseService, 
                                           OracleDatabaseService, 
                                           MSSQLDatabaseService)
from app.core.security import get_user_id

env_router = APIRouter()

# Updated version of the endpoint
@env_router.put("/admin")
async def handle_admin_env(payload: AdminEnvPayload, db: aiomysql.Connection = Depends(AuthDatabaseService.get_db)):
    """
        @param: payload: will accept json admin input
        @return: success message after writing the input data on the database 
    """
    try:
        # decoded_usr = await get_user_id(payload.email)
        async with db.cursor(aiomysql.DictCursor) as cursor:
            # Check if the user is an admin by verifying the email domain
            # TODO: change checking admin not by email but by support site 'role' response
            await cursor.execute(
                "SELECT * FROM env_auth WHERE email = %s AND email LIKE %s",
                (payload.email, "%@arcturustech.com")  # Filter for email domain
            )
            admin = await cursor.fetchone()  # Fetch the first matching admin

            if admin:
                # If admin exists, update the user with the new data
                await cursor.execute(
                    "SELECT * FROM env_auth WHERE email = %s",
                    (payload.email_user,)
                )
                user = await cursor.fetchone()  # Fetch the user to be updated

                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"User with email '{payload.email_user}' not found"
                    )

                # Prepare the data to be updated, excluding unset fields
                updated_data = payload.dict(exclude_unset=True)
                # Handle special case for 'email' field
                if 'email' in updated_data:
                    updated_data['email'] = payload.email_user
                
                if 'DB_TABLES' in updated_data:
                    updated_data['DB_TABLES'] = json.dumps(updated_data['DB_TABLES'])
                    
                # Delete the email_user key from the updated_data dictionary
                if 'email_user' in updated_data:
                    del updated_data['email_user']
                    
                # Filter out invalid values from the dictionary
                valid_updated_data = {key: value for key, value in updated_data.items() 
                    if value not in [None, "", [], [""], ["string"]] and not (isinstance(value, int) and value == 0)}

                if valid_updated_data:
                    # Dynamically construct the SET clause and values for the update
                    set_clause = ", ".join([f"{key} = %s" for key in valid_updated_data.keys()])
                    values = list(valid_updated_data.values()) + [payload.email_user]  # Email as the WHERE condition

                    query = f"UPDATE env_auth SET {set_clause} WHERE email = %s"

                    # Execute the query with the constructed values
                    await cursor.execute(query, values)
                await db.commit()  # Commit the transaction to the database

                logger.info(f"Admin environment for {payload.email_user} updated successfully")
                return JSONResponse(
                    content={"message": f"Admin environment for {payload.email_user} updated successfully"}
                )

            else:
                logger.error(f"Unauthorized access attempt by non-admin: {payload.email}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"The user with email '{payload.email}' is not authorized as an admin."
                )

    except Exception as e:
        logger.error(f"An unexpected error occurred. Please try again later. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred. Please try again later. Error: {e}"
        )

    finally:
        db.close()  # Ensure the connection is closed

@env_router.put("/user")
async def handle_user_env(payload: UserEnvPayload, db: aiomysql.Connection = Depends(AuthDatabaseService.get_db)):
    try:
        decoded_usr = await get_user_id(payload.email)
        # TODO: makesure the table is sent and formated in a list of strings from the frontend ... but they have to write it in a selection manner
        async with db.cursor(aiomysql.DictCursor) as cursor:
            # Check if the user exists based on email
            await cursor.execute(
                "SELECT * FROM env_auth WHERE email = %s",
                (decoded_usr,)
            )
            user = await cursor.fetchone()  # Fetch the first matching user
            logger.info(f"User: {user}")
            if user:
                update_data = payload.dict(exclude_unset=True)  # Only includes fields provided in the payload

                update_data['DB_TABLES'] = json.dumps(update_data['DB_TABLES'])
                update_data['email'] = decoded_usr
                
                # Filter out fields with invalid values (None, empty string, empty list, etc.)
                valid_update_data = {key: value for key, value in update_data.items() if value not in [None, "", [], [""]] and not (isinstance(value, int) and value == 0)}
                logger.info(f"Valid update data: {valid_update_data}")
                if valid_update_data:
                    # Dynamically construct the SET clause and values for the update
                    set_clause = ", ".join([f"{key} = %s" for key in valid_update_data.keys()])
                    values = list(valid_update_data.values()) + [decoded_usr]

                    query = f"UPDATE env_auth SET {set_clause} WHERE email = %s"

                    # Execute the query with the constructed values
                    await cursor.execute(query, values)

                await db.commit()  # Commit the transaction to the database
                logger.info(f"User environment for {decoded_usr} updated successfully")
                return JSONResponse(
                    content={"message": f"User environment for {decoded_usr} updated successfully"}
                )
            else:
                # If user does not exist, create a new user entry
                # new_user_data = payload.dict(exclude_unset=True)  # Only includes fields provided in the payload
                db_tables_str = json.dumps(payload.DB_TABLES)
                await cursor.execute(
                    "INSERT INTO env_auth (email, DB_MS, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB, DB_TABLES) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        decoded_usr,
                        payload.DB_MS,
                        payload.DB_USER,
                        payload.DB_PASSWORD,
                        payload.DB_HOST,
                        payload.DB_PORT,
                        payload.DB,
                        db_tables_str
                    )
                )
                await db.commit()  # Commit the transaction to the database
                logger.info(f"User environment for {decoded_usr} created successfully")
                return JSONResponse(
                    content={"message": f"User environment for {decoded_usr} created successfully"}
                )
    except Exception as e:
        logger.error(f"An unexpected error occurred. Please try again later. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred. Please try again later. Error: {e}"
        )

    finally:
        db.close()  # Ensure the connection is closed after the operation
 
@env_router.get("/get-user")
async def get_user_env(email: str, db: aiomysql.Connection = Depends(AuthDatabaseService.get_db)):
    try:
        # decoded_usr = await get_user_id(email)
        decoded_usr = str(email)
        async with db.cursor(aiomysql.DictCursor) as cursor:
            # Fetch user environment from the database based on email
            await cursor.execute(
                "SELECT * FROM env_auth WHERE email = %s", 
                (decoded_usr,)
            )
            user = await cursor.fetchone()  # Fetch the first matching user
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No user environment found for email: {decoded_usr}"
                )

            # Prepare the response payload
            response_payload = {
                "DB_MS": user.get("DB_MS"),
                "DB_USER": user.get("DB_USER"),
                "DB_PASSWORD": user.get("DB_PASSWORD"),
                "DB_HOST": user.get("DB_HOST"),
                "DB_PORT": user.get("DB_PORT"),
                "DB": user.get("DB"),
                "DB_TABLES": json.loads(user.get("DB_TABLES")),
            }

            logger.info(f"Fetched environment details for email: {decoded_usr}")
            return JSONResponse(content=response_payload)

    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching user environment. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred. Please try again later. Error: {e}"
        )
    
    finally:
        db.close()  # Ensure the connection is closed after the operation

# TODO: add table fetching mechanisms
# @env_router.get("/fetch-tables")
# async def fetch_tables(db: aiomysql.Connection = Depends(AuthDatabaseService.connection)):
#     """
#     Fetch all table names from the connected database.
#     Args:
#         db (aiomysql.Connection): Database connection.
#     Returns:
#         List of table names as strings.
#     """
#     try:
#         async with db.cursor() as cursor:
#             # Query to fetch all table names
#             await cursor.execute("SHOW TABLES;")
#             tables = await cursor.fetchall()  # Fetch all rows

#             # Extract table names from the query result
#             table_names = [table[0] for table in tables]

#             return JSONResponse(content={"tables": table_names})

#     except Exception as e:
#         # Handle exceptions and log the error
#         logger.error(f"Failed to fetch table names. Error: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"An error occurred while fetching table names: {e}"
#         )

#     finally:
#         db.close()  # Ensure the database connection is closed

@env_router.post("/test-connect")
async def test_database_connection(payload: UserEnvPayload):
    """
    Endpoint to test database connections for MySQL, MariaDB, Oracle, and MSSQL.
    Returns a success or failure message for the provided database type.
    """
    try:
        # decoded_usr = await get_user_id(payload.email)
        settings = {
            "DB_HOST": payload.DB_HOST,
            "DB_PORT": payload.DB_PORT,
            "DB_USER": payload.DB_USER,
            "DB_PASSWORD": payload.DB_PASSWORD,
            "DB": payload.DB,
        }

        async def ping_mysql():
            connection = None
            try:
                connection = await aiomysql.connect(
                    host=settings["DB_HOST"],
                    user=settings["DB_USER"],
                    password=settings["DB_PASSWORD"],
                    db=settings["DB"],
                    port=int(settings["DB_PORT"]),
                )
                async with connection.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    result = await cursor.fetchone()
                    return result[0] == 1
            except Exception as e:
                logger.error(status_code=500, detail=f"MySQL Error: {e}")
            finally:
                if connection:
                    connection.close()

        async def ping_mariadb():
            # Reuse MySQL logic since they are compatible
            return await ping_mysql()

        async def ping_oracle():
            connection = None
            try:
                dsn = (
                    f"DRIVER={{Oracle}};"
                    f"DBQ={settings["DB_HOST"]}:{settings["DB_PORT"]}/{settings["DB"]};"
                    f"UID={settings["DB_USER"]};"
                    f"PWD={settings["DB_PASSWORD"]}"
                )
                pool = await aioodbc.create_pool(dsn=dsn, autocommit=True)
                
                async with pool.acquire() as conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute("SELECT 1 FROM DUAL")
                        result = await cursor.fetchone()
                        return result[0] == 1
            except Exception as e:
                logger.error(status_code=500, detail=f"Oracle Error: {e}")
            finally:
                if connection:
                    connection.close()

        async def ping_mssql():
            connection_pool = None
            try:
                dsn = (
                    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                    f"SERVER={settings['DB_HOST']},{settings['DB_PORT']};"
                    f"DATABASE={settings['DB']};"
                    f"UID={settings['DB_USER']};"
                    f"PWD={settings['DB_PASSWORD']};"
                    "TrustServerCertificate=yes;"
                )
                connection_pool = await aioodbc.create_pool(dsn=dsn, autocommit=True)
                async with connection_pool.acquire() as connection:
                    async with connection.cursor() as cursor:
                        await cursor.execute("SELECT 1")
                        result = await cursor.fetchone()
                        return result[0] == 1
            except Exception as e:
                logger.error(status_code=500, detail=f"MSSQL Error: {e}")
            finally:
                if connection_pool:
                    connection_pool.close()

        # Map database type to corresponding ping function
        db_ping_functions = {
            "mysql": ping_mysql,
            "mariadb": ping_mariadb,
            "oracle": ping_oracle,
            "mssql": ping_mssql,
        }

        # Get the appropriate ping function for the provided DB_MS
        db_ms = payload.DB_MS.lower()
        if db_ms not in db_ping_functions:
            raise HTTPException(
                status_code=400, detail="Unsupported database type. Use 'mysql', 'mariadb', 'oracle', or 'mssql'."
            )

        # Call the corresponding ping function
        is_connected = await db_ping_functions[db_ms]()
        if is_connected:
            return {"status": 1, "message": "Connection Successful"}
        else:
            return {"status": 0, "message": "Connection Failed"}
    except Exception as e:
        return {"status": 0, "message": f"Connection Failed: {e}"} 
    
    
    