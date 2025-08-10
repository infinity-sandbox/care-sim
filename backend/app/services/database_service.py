import asyncio
from typing import List, Optional
from app.core.config import logger_settings, Settings
logger = logger_settings.get_logger(__name__)
from fastapi import HTTPException
import pyodbc
import aiomysql
import aioodbc
from typing import AsyncGenerator

class MySQLDatabaseService:
    @staticmethod
    async def connection(settings: Optional[Settings] = None):
        """
        Establishes a connection to the MySQL database using aiomysql.
        Ensures the database exists, creating it if necessary.
        Returns:
            connection: aiomysql connection object.
        """
        try:
            # Reconnect to the specified database
            connection = await aiomysql.connect(
                host=settings.DB_HOST,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                db=settings.DB,
                port=int(settings.DB_PORT)
            )
            return connection
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error connecting to the database: {e}")
    
    @staticmethod
    async def get_db() -> AsyncGenerator[aiomysql.Connection, None]:
        """
        Provides an async database connection to FastAPI endpoints.
        Yields:
            aiomysql.Connection: MySQL connection instance.
        """
        connection = await MySQLDatabaseService.connection()
        try:
            yield connection
        except Exception as e:
            raise RuntimeError(f"Session error: {e}")
        finally:
            # connection.close()
            await connection.ensure_closed()
    
    @staticmethod
    async def ping_database():
        """
        Pings the database to check if the connection is active.
        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        try:
            connection = await MySQLDatabaseService.connection()
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT 1")
                result = await cursor.fetchone()
                if result[0] == 1:
                    return True
        except Exception as e:
            return False
        finally:
            # connection.close()
            await connection.ensure_closed()
        
    @staticmethod
    async def get_schema(settings: Optional[Settings] = None):
        """
        Fetches the schema and top 3 rows for each table.
        Args:
            settings: Settings object containing DB_TABLES.
        Returns:
            str: Formatted schema and data for each table.
        """
        try:
            logger.debug(f"Settings received in get_schema: {settings}")
            ALL_TABLES = await MySQLDatabaseService.list_tables(settings=settings)
            logger.debug(f"Tables retrieved: {ALL_TABLES}")
            
            # Get the existing tables
            existing_tables = [table for table in settings.DB_TABLES if table in ALL_TABLES]
            logger.debug(f"Existing tables: {existing_tables}")

            # Log missing tables
            # missing_tables = [table for table in settings.DB_TABLES if table not in ALL_TABLES]
            # if missing_tables:
            #     logger.warning(f"Missing tables: {missing_tables}")

            schema = [
                {"table_schema": await MySQLDatabaseService.get_table_schema(table, settings=settings),
                "table_data": await MySQLDatabaseService.get_table_data(table, settings=settings)}
                for table in existing_tables
            ]

            logger.info(f"Tables data fetched successfully!")
                    
            formatted_schema = "\n\n".join(
                [f"{entry['table_schema']}\n\n{entry['table_data']}" for entry in schema]
            )
            
            return formatted_schema
        except Exception as e:
            logger.error(f"Error fetching schema: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching schema: {e}")
    
    @staticmethod
    async def list_databases(settings: Optional[Settings] = None):
        """
        Lists all databases asynchronously.
        Returns:
            list: A list of database names.
        """
        try:
            # Establish connection to the MariaDB server
            connection = await MySQLDatabaseService.connection(settings=settings)
            
            async with connection.cursor() as cursor:
                # Execute the SHOW DATABASES query
                await cursor.execute("SHOW DATABASES")
                
                # Fetch all databases
                databases = await cursor.fetchall()
                
                # Extract the database names from the result
                database_names = [db[0] for db in databases]
                logger.debug(f"list databases: {database_names}")
                return database_names
        except Exception as e:
            raise Exception(f"Error fetching databases: {e}")
        finally:
            # connection.close()
            await connection.ensure_closed()
    
    @staticmethod
    async def list_tables(settings: Optional[Settings] = None) -> list:
        """
        Lists the tables in the current MariaDB database asynchronously.
        Returns:
            list: A list of table names.
        """
        try:
            connection = await MySQLDatabaseService.connection(settings=settings)
            
            async with connection.cursor() as cursor:
                await cursor.execute("SHOW TABLES")
                tables = await cursor.fetchall()
                table_names = [table[0] for table in tables]
                logger.debug(f"Tables: {table_names}")
                return table_names
        except Exception as e:
            raise Exception(f"Error fetching tables: {e}")
        finally:
            # connection.close()
            await connection.ensure_closed()

    @staticmethod
    async def list_columns(table_name: str, settings: Optional[Settings] = None) -> list:
        """
        Lists the columns of a given table asynchronously.
        Args:
            table_name (str): The name of the table whose columns are to be listed.
        Returns:
            list: A list of column names.
        """
        try:
            # Establish connection to the MariaDB server
            connection = await MySQLDatabaseService.connection(settings=settings)
            
            async with connection.cursor() as cursor:
                # Execute the DESCRIBE query to get table columns
                await cursor.execute(f"DESCRIBE {table_name}")
                
                # Fetch all columns
                columns = await cursor.fetchall()
                
                # Extract column names from the result
                column_names = [col[0] for col in columns]
                
                return column_names
        except Exception as e:
            raise Exception(f"Error fetching columns for table '{table_name}': {e}")
        finally:
            # connection.close()
            await connection.ensure_closed()

    @staticmethod
    async def run_query(query: str, settings: Optional[Settings] = None):
        """
        Executes a given SQL query asynchronously.
        Args:
            query (str): The SQL query to execute.
        Returns:
            result: The result of the query execution.
        """
        try:
            # Establish connection to the MariaDB server
            connection = await MySQLDatabaseService.connection(settings=settings)
            
            async with connection.cursor() as cursor:
                # Execute the provided query
                await cursor.execute(query)
                
                # Fetch all results (use fetchone() if you need only one result)
                result = await cursor.fetchall()
                
                return result
        except Exception as e:
            raise Exception(f"Error executing query: {e}")
        finally:
            # connection.close()
            await connection.ensure_closed()
    
    @staticmethod
    async def get_table_schema(table_name, settings: Optional[Settings] = None) -> str:
        """
        Fetches the schema (columns and their data types) for a table.
        Args:
            table_name: Name of the table.
        Returns:
            str: CREATE TABLE script for the specified table.
        """
        try:
            connection = await MySQLDatabaseService.connection(settings=settings)
            async with connection.cursor() as cursor:
                await cursor.execute(f"DESCRIBE {table_name}")
                columns_info = await cursor.fetchall()

                create_script = f"CREATE TABLE {table_name} (\n"
                columns = []

                columns = [
                    f"{column[0]} {column[1]} "
                    f"{'NULL' if column[2] == 'YES' else 'NOT NULL'} "
                    f"{f'DEFAULT {column[4]}' if column[4] else ''} "
                    f"{column[5] if column[5] else ''}".strip()
                    for column in columns_info
                ]

                create_script += ",\n    ".join(columns)
                create_script += "\n);"
                logger.debug(f"get table schema: {create_script}")
                return create_script
        except Exception as e:
            logger.error(f"Error fetching schema for table '{table_name}': {e}")
            raise Exception(f"Error fetching schema for table '{table_name}': {e}")
        finally:
            # connection.close()
            await connection.ensure_closed()
    
    @staticmethod
    async def get_table_data(table_name, settings: Optional[Settings] = None) -> str:
        """
        Fetches the top 3 rows from the specified table.
        Args:
            table_name: Name of the table.
        Returns:
            str: Top 3 rows formatted as a string.
        """
        try:
            connection = await MySQLDatabaseService.connection(settings=settings)
            async with connection.cursor() as cursor:
                # Get column names
                await cursor.execute(f"DESCRIBE {table_name}")
                columns_info = await cursor.fetchall()
                column_names = [column[0] for column in columns_info]

                # Fetch top 3 rows
                await cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = await cursor.fetchall()

                # Format the result
                table_data = "\n".join([" | ".join(map(str, row)) for row in rows])
                result = f"/*\n3 rows from {table_name} table:\n"
                result += f"{' | '.join(column_names)}\n"
                result += f"{table_data}\n*/"
                logger.debug(f"get table data: {result}")
                return result    
        except Exception as e:
            logger.error(f"Error fetching data for table '{table_name}': {e}")
            raise Exception(f"Error fetching data for table '{table_name}': {e}")
        finally:
            # connection.close()
            await connection.ensure_closed()

class MariaDbDatabaseService:
    @staticmethod
    async def connection(settings: Optional[Settings] = None):
        """
        Establishes a connection to the MySQL database using aiomysql.
        Ensures the database exists, creating it if necessary.
        Returns:
            connection: aiomysql connection object.
        """
        try:
            # Reconnect to the specified database
            connection = await aiomysql.connect(
                host=settings.DB_HOST,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                db=settings.DB,
                port=int(settings.DB_PORT)
            )
            return connection
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error connecting to the database: {e}")
        
    @staticmethod
    async def get_db() -> AsyncGenerator[aiomysql.Connection, None]:
        """
        Provides an async database connection to FastAPI endpoints.
        Yields:
            aiomysql.Connection: MySQL connection instance.
        """
        connection = await MariaDbDatabaseService.connection()
        try:
            yield connection
        except Exception as e:
            raise RuntimeError(f"Session error: {e}")
        finally:
            connection.close()
            
    @staticmethod
    async def ping_database():
        """
        Pings the database to check if the connection is active.
        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        try:
            connection = await MariaDbDatabaseService.connection()
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT 1")
                result = await cursor.fetchone()
                if result[0] == 1:
                    return True
        except Exception as e:
            return False
        finally:
            connection.close()
            
    @staticmethod
    async def get_schema(settings: Optional[Settings] = None):
        """
        Fetches the schema and top 3 rows for each table.
        Args:
            settings: Settings object containing DB_TABLES.
        Returns:
            str: Formatted schema and data for each table.
        """
        try:
            ALL_TABLES = await MariaDbDatabaseService.list_tables(settings=settings)

            # Get the existing tables
            existing_tables = [table for table in settings.DB_TABLES if table in ALL_TABLES]
            logger.debug(f"Existing tables: {existing_tables}")

            # Log missing tables
            missing_tables = [table for table in settings.DB_TABLES if table not in ALL_TABLES]
            if missing_tables:
                logger.warning(f"Missing tables: {missing_tables}")

            schema = [
                {"table_schema": await MariaDbDatabaseService.get_table_schema(table, settings=settings),
                "table_data": await MariaDbDatabaseService.get_table_data(table, settings=settings)}
                for table in existing_tables
            ]

            logger.info(f"Tables data fetched successfully!")
                    
            formatted_schema = "\n\n".join(
                [f"{entry['table_schema']}\n\n{entry['table_data']}" for entry in schema]
            )
            
            return formatted_schema
        except Exception as e:
            logger.error(f"Error fetching schema: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching schema: {e}")
    
    @staticmethod
    async def list_databases(settings: Optional[Settings] = None):
        """
        Lists all databases asynchronously.
        Returns:
            list: A list of database names.
        """
        try:
            # Establish connection to the MariaDB server
            connection = await MariaDbDatabaseService.connection(settings=settings)
            
            async with connection.cursor() as cursor:
                # Execute the SHOW DATABASES query
                await cursor.execute("SHOW DATABASES")
                
                # Fetch all databases
                databases = await cursor.fetchall()
                
                # Extract the database names from the result
                database_names = [db[0] for db in databases]
                
                return database_names
        except Exception as e:
            raise Exception(f"Error fetching databases: {e}")
        finally:
            connection.close()
    
    @staticmethod
    async def list_tables(settings: Optional[Settings] = None) -> list:
        """
        Lists the tables in the current MariaDB database asynchronously.
        Returns:
            list: A list of table names.
        """
        try:
            connection = await MariaDbDatabaseService.connection(settings=settings)
            
            async with connection.cursor() as cursor:
                await cursor.execute("SHOW TABLES")
                tables = await cursor.fetchall()
                table_names = [table[0] for table in tables]

                return table_names
        except Exception as e:
            raise Exception(f"Error fetching tables: {e}")
        finally:
            connection.close()

    @staticmethod
    async def list_columns(table_name: str, settings: Optional[Settings] = None) -> list:
        """
        Lists the columns of a given table asynchronously.
        Args:
            table_name (str): The name of the table whose columns are to be listed.
        Returns:
            list: A list of column names.
        """
        try:
            # Establish connection to the MariaDB server
            connection = await MariaDbDatabaseService.connection(settings=settings)
            
            async with connection.cursor() as cursor:
                # Execute the DESCRIBE query to get table columns
                await cursor.execute(f"DESCRIBE {table_name}")
                
                # Fetch all columns
                columns = await cursor.fetchall()
                
                # Extract column names from the result
                column_names = [col[0] for col in columns]

                return column_names
        except Exception as e:
            raise Exception(f"Error fetching columns for table '{table_name}': {e}")
        finally:
            connection.close()

    @staticmethod
    async def run_query(query: str, settings: Optional[Settings] = None):
        """
        Executes a given SQL query asynchronously.
        Args:
            query (str): The SQL query to execute.
        Returns:
            result: The result of the query execution.
        """
        try:
            # Establish connection to the MariaDB server
            connection = await MariaDbDatabaseService.connection(settings=settings)
            
            async with connection.cursor() as cursor:
                # Execute the provided query
                await cursor.execute(query)
                
                # Fetch all results (use fetchone() if you need only one result)
                result = await cursor.fetchall()

                return result
        except Exception as e:
            raise Exception(f"Error executing query: {e}")
        finally:
            connection.close()
    
    @staticmethod
    async def get_table_schema(table_name, settings: Optional[Settings] = None) -> str:
        """
        Fetches the schema (columns and their data types) for a table.
        Args:
            table_name: Name of the table.
        Returns:
            str: CREATE TABLE script for the specified table.
        """
        try:
            connection = await MariaDbDatabaseService.connection(settings=settings)
            async with connection.cursor() as cursor:
                await cursor.execute(f"DESCRIBE {table_name}")
                columns_info = await cursor.fetchall()

                create_script = f"CREATE TABLE {table_name} (\n"
                columns = []

                columns = [
                    f"{column[0]} {column[1]} "
                    f"{'NULL' if column[2] == 'YES' else 'NOT NULL'} "
                    f"{f'DEFAULT {column[4]}' if column[4] else ''} "
                    f"{column[5] if column[5] else ''}".strip()
                    for column in columns_info
                ]

                create_script += ",\n    ".join(columns)
                create_script += "\n);"

                return create_script
        except Exception as e:
            logger.error(f"Error fetching schema for table '{table_name}': {e}")
            raise Exception(f"Error fetching schema for table '{table_name}': {e}")
        finally:
            connection.close()
    
    @staticmethod
    async def get_table_data(table_name, settings: Optional[Settings] = None) -> str:
        """
        Fetches the top 3 rows from the specified table.
        Args:
            table_name: Name of the table.
        Returns:
            str: Top 3 rows formatted as a string.
        """
        try:
            connection = await MariaDbDatabaseService.connection(settings=settings)
            async with connection.cursor() as cursor:
                # Get column names
                await cursor.execute(f"DESCRIBE {table_name}")
                columns_info = await cursor.fetchall()
                column_names = [column[0] for column in columns_info]

                # Fetch top 3 rows
                await cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = await cursor.fetchall()

                # Format the result
                table_data = "\n".join([" | ".join(map(str, row)) for row in rows])
                result = f"/*\n3 rows from {table_name} table:\n"
                result += f"{' | '.join(column_names)}\n"
                result += f"{table_data}\n*/"

                return result
        except Exception as e:
            logger.error(f"Error fetching data for table '{table_name}': {e}")
            raise Exception(f"Error fetching data for table '{table_name}': {e}")
        finally:
            connection.close()
 
class MSSQLDatabaseService:
    @staticmethod
    async def connection(settings: Optional[Settings] = None):
        """
        Establish an async connection to MSSQL using aioodbc.
        Returns:
            connection: An aioodbc connection pool object.
        """
        try:
            dsn = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={settings.DB_HOST},{settings.DB_PORT};"
                f"DATABASE={settings.DB};"
                f"UID={settings.DB_USER};"
                f"PWD={settings.DB_PASSWORD};"
                "TrustServerCertificate=yes;"
            )

            # Create a connection pool
            connection_pool = await aioodbc.create_pool(dsn=dsn, autocommit=True)
            logger.info("MSSQL database connection pool created!")
            return connection_pool
        except Exception as e:
            logger.error(f"Error creating MSSQL connection pool: {e}")
            raise HTTPException(status_code=500, detail=f"Database connection error: {e}")

    @staticmethod
    async def get_db() -> AsyncGenerator[aioodbc.Connection, None]:
        """Async database connection generator"""
        pool = await MSSQLDatabaseService.connection()
        try:
            async with pool.acquire() as conn:
                yield conn
        finally:
            await MSSQLDatabaseService.close_connection(pool)
            
    @staticmethod
    async def list_databases(settings: Optional[Settings] = None) -> list:
        """
        Fetch a list of databases from the MSSQL server.
        """
        try:
            pool = await MSSQLDatabaseService.connection(settings)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT name FROM sys.databases")
                    databases = await cursor.fetchall()
                    logger.debug(f"Databases: {databases}")
                    return [db[0] for db in databases]
        except Exception as e:
            logger.error(f"Error listing databases: {e}")
            raise HTTPException(status_code=500, detail=f"Error listing databases: {e}")
        finally:
            await MSSQLDatabaseService.close_connection(pool)
            
    @staticmethod
    async def list_tables(settings: Optional[Settings] = None) -> list:
        """
        Fetch a list of tables from the current database.
        """
        try:
            pool = await MSSQLDatabaseService.connection(settings)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT name FROM sys.tables")
                    tables = await cursor.fetchall()
                    logger.debug(f"Tables: {tables}")
                    return [table[0] for table in tables]
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            raise HTTPException(status_code=500, detail=f"Error listing tables: {e}")
        finally:
            await MSSQLDatabaseService.close_connection(pool)

    @staticmethod
    async def list_columns(table_name: str, settings: Optional[Settings] = None) -> list:
        """
        Fetch a list of columns for a specified table.
        """
        try:
            pool = await MSSQLDatabaseService.connection(settings)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'"
                    )
                    logger.debug(f"Columns for table '{table_name}': {cursor}")
                    return await cursor.fetchall()
        except Exception as e:
            logger.error(f"Error listing columns: {e}")
            raise HTTPException(status_code=500, detail=f"Error listing columns: {e}")
        finally:
            await MSSQLDatabaseService.close_connection(pool)

    @staticmethod
    async def run_query(query: str, settings: Optional[Settings] = None):
        """
        Run a custom SQL query asynchronously.
        """
        try:
            pool = await MSSQLDatabaseService.connection(settings)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query)
                    result = await cursor.fetchall()
                    logger.debug(f"Query result: {result}")
                    return result
        except Exception as e:
            logger.error(f"Error when running query: {e}")
            raise HTTPException(status_code=500, detail=f"Error when running query: {e}")
        finally:
            await MSSQLDatabaseService.close_connection(pool)

    @staticmethod
    async def get_schema(settings: Optional[Settings] = None) -> str:
        """
        Fetch schema details and sample data for specified tables.
        """
        try:
            all_tables = await MSSQLDatabaseService.list_tables(settings)

            # Filter only the existing tables
            existing_tables = [table for table in settings.DB_TABLES if table in all_tables]
            missing_tables = [table for table in settings.DB_TABLES if table not in all_tables]

            if missing_tables:
                logger.warning(f"Missing tables: {missing_tables}")

            schema = []
            for table in existing_tables:
                table_schema = await MSSQLDatabaseService.get_table_create_script(table, settings)
                table_data = await MSSQLDatabaseService.get_table_data(table, settings)
                schema.append({"table_schema": table_schema, "table_data": table_data})

            formatted_schema = "\n\n".join(
                f"{entry['table_schema']}\n\n{entry['table_data']}" for entry in schema
            )
            return formatted_schema
        except Exception as e:
            logger.error(f"Error fetching schema: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching schema: {e}")

    @staticmethod
    async def get_table_create_script(table_name: str, settings: Optional[Settings] = None) -> str:
        """
        Generate the CREATE TABLE script for the given table.
        """
        try:
            pool = await MSSQLDatabaseService.connection(settings)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"""
                        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = '{table_name}'
                        ORDER BY ORDINAL_POSITION
                    """)

                    columns = []
                    async for row in cursor:
                        column_name, data_type, max_length = row
                        column_definition = (
                            f"{column_name} {data_type}({max_length})"
                            if max_length else f"{column_name} {data_type}"
                        )
                        columns.append(column_definition)

                    create_script = f"CREATE TABLE {table_name} (\n    {',\n    '.join(columns)}\n);"
                    return create_script
        except Exception as e:
            logger.error(f"Error when getting table create script: {e}")
            raise HTTPException(status_code=500, detail=f"Error when getting table create script: {e}")
        finally:
            await MSSQLDatabaseService.close_connection(pool)

    @staticmethod
    async def get_table_data(table_name: str, settings: Optional[Settings] = None) -> str:
        """
        Fetch the first 3 rows of data for a table.
        """
        try:
            pool = await MSSQLDatabaseService.connection(settings)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Get column names
                    await cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
                    column_names = [row[0] for row in await cursor.fetchall()]

                    # Get the top 3 rows
                    await cursor.execute(f"SELECT TOP 3 * FROM {table_name}")
                    rows = await cursor.fetchall()

                    # Format the data
                    data_rows = "\n".join([" | ".join(map(str, row)) for row in rows])
                    result = f"/*\n3 rows from {table_name} table:\n{', '.join(column_names)}\n{data_rows}\n*/"
                    return result
        except Exception as e:
            logger.error(f"Error when getting table data: {e}")
            raise HTTPException(status_code=500, detail=f"Error when getting table data: {e}")
        finally:
            await MSSQLDatabaseService.close_connection(pool)
        
    @staticmethod
    async def close_connection(connection):
        """
        Close an MSSQL connection.
        """
        try:
            if connection:
                logger.info("Closing MSSQL database connection...")
                connection.close()
                await connection.wait_closed()
                logger.info("MSSQL database connection closed!")
        except Exception as e:
            logger.error(f"Error closing MSSQL connection: {e}")
            raise HTTPException(status_code=500, detail=f"Error closing the connection: {e}")

class OracleDatabaseService:
    @staticmethod
    async def connection(settings: Optional[Settings] = None):
        """Create async Oracle connection pool using aioodbc"""
        try:
            dsn = (
                f"DRIVER={{Oracle}};"
                f"DBQ={settings.DB_HOST}:{settings.DB_PORT}/{settings.DB};"
                f"UID={settings.DB_USER};"
                f"PWD={settings.DB_PASSWORD}"
            )
            pool = await aioodbc.create_pool(dsn=dsn, autocommit=True)
            logger.info("Oracle connection pool created!")
            return pool
        except Exception as e:
            logger.error(f"Oracle connection error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Oracle connection failed: {str(e)}")

    @staticmethod
    async def get_db() -> AsyncGenerator[aioodbc.Connection, None]:
        """Async database connection generator"""
        pool = await OracleDatabaseService.connection()
        try:
            async with pool.acquire() as conn:
                yield conn
        finally:
            await OracleDatabaseService.close_connection(pool)

    @staticmethod
    async def list_databases(settings: Optional[Settings] = None) -> List[str]:
        """List available Oracle PDBs (Pluggable Databases)"""
        try:
            pool = await OracleDatabaseService.connection(settings)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT name FROM v$pdbs WHERE open_mode = 'READ WRITE'")
                    databases = await cursor.fetchall()
                    return [db[0] for db in databases]
        except Exception as e:
            logger.error(f"Error listing databases: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await OracleDatabaseService.close_connection(pool)

    @staticmethod
    async def list_tables(settings: Optional[Settings] = None) -> List[str]:
        """List tables in current schema"""
        try:
            pool = await OracleDatabaseService.connection(settings)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT table_name FROM user_tables")
                    tables = await cursor.fetchall()
                    return [table[0] for table in tables]
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await OracleDatabaseService.close_connection(pool)

    @staticmethod
    async def list_columns(table_name: str, settings: Optional[Settings] = None) -> List[str]:
        """List columns for specified table"""
        try:
            pool = await OracleDatabaseService.connection(settings)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"""
                        SELECT column_name 
                        FROM user_tab_columns 
                        WHERE table_name = UPPER('{table_name}')
                        ORDER BY column_id
                    """)
                    return [col[0] for col in await cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error listing columns: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await OracleDatabaseService.close_connection(pool)

    @staticmethod
    async def run_query(query: str, settings: Optional[Settings] = None):
        """Execute custom SQL query"""
        try:
            pool = await OracleDatabaseService.connection(settings)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query)
                    return await cursor.fetchall()
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await OracleDatabaseService.close_connection(pool)

    @staticmethod
    async def get_schema(settings: Optional[Settings] = None) -> str:
        """Generate full schema documentation"""
        try:
            # Fetch database name and version
            db_info_query = "SELECT * FROM V$VERSION"
            db_info = await OracleDatabaseService.run_query(db_info_query, settings)
            logger.info(f"TODEL: db_info\n{db_info}")
            
            if db_info:
                db_version = "\n".join([row[0] for row in db_info])  # Extract version details
            else:
                db_version = "Database: OracleDB, Version: unavailable"
                
            all_tables = await OracleDatabaseService.list_tables(settings)
            # logger.debug(f"Tables: \n{all_tables}")
            existing_tables = [t for t in settings.DB_TABLES if t in all_tables]
            
            schema_entries = []
            for table in existing_tables:
                schema = await OracleDatabaseService.get_table_create_script(table, settings)
                data = await OracleDatabaseService.get_table_data(table, settings)
                schema_entries.append(f"{schema}\n\n{data}")
            
            full_schema = "\n\n".join(schema_entries)
            
            # Append database version on top
            return f"Database Version:\n{db_version}\n\n{full_schema}"
    
            return "\n\n".join(schema_entries)
        except Exception as e:
            logger.error(f"Schema generation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_table_create_script(table_name: str, settings: Optional[Settings] = None) -> str:
        """Generate CREATE TABLE script"""
        try:
            pool = await OracleDatabaseService.connection(settings)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Get columns
                    await cursor.execute(f"""
                        SELECT column_name, data_type, data_length, nullable, data_default
                        FROM user_tab_columns
                        WHERE table_name = UPPER('{table_name}')
                        ORDER BY column_id
                    """)
                    columns = []
                    async for row in cursor:
                        col_def = f"{row[0]} {row[1]}({row[2]})"
                        col_def += " NOT NULL" if row[3] == 'N' else ""
                        if row[4]: col_def += f" DEFAULT {row[4]}"
                        columns.append(col_def)
                    
                    # Get constraints
                    await cursor.execute(f"""
                        SELECT constraint_name, search_condition 
                        FROM user_constraints 
                        WHERE table_name = UPPER('{table_name}')
                    """)
                    constraints = [f"CONSTRAINT {row[0]} {row[1]}" async for row in cursor]
                    
                    create_script = f"CREATE TABLE {table_name} (\n  "
                    create_script += ",\n  ".join(columns + constraints)
                    create_script += "\n);"
                    return create_script
        except Exception as e:
            logger.error(f"Schema generation failed for {table_name}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await OracleDatabaseService.close_connection(pool)

    @staticmethod
    async def get_table_data(table_name: str, settings: Optional[Settings] = None) -> str:
        """Sample table data with headers"""
        try:
            pool = await OracleDatabaseService.connection(settings)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Get columns
                    await cursor.execute(f"""
                        SELECT column_name 
                        FROM user_tab_columns 
                        WHERE table_name = UPPER('{table_name}')
                        ORDER BY column_id
                    """)
                    columns = [col[0] async for col in cursor]
                    
                    # Get data
                    await cursor.execute(f"""
                        SELECT * FROM {table_name} 
                        FETCH FIRST 3 ROWS ONLY
                    """)
                    rows = [row async for row in cursor]
                    
                    # Format output
                    header = " | ".join(columns)
                    data = "\n".join([" | ".join(map(str, row)) for row in rows])
                    return f"/*\n3 rows from {table_name}:\n{header}\n{data}\n*/"
        except Exception as e:
            logger.error(f"Data fetch failed for {table_name}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await OracleDatabaseService.close_connection(pool)

    @staticmethod
    async def close_connection(pool):
        """Cleanup connection pool"""
        try:
            if pool:
                logger.info("Closing Oracle connection pool...")
                pool.close()
                await pool.wait_closed()
        except Exception as e:
            logger.error(f"Error closing connections: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        