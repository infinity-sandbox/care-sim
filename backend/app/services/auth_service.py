from typing import AsyncGenerator
from fastapi import HTTPException
from dotenv import load_dotenv
import os
import aiomysql
load_dotenv()
from typing import Optional, List, Dict, Tuple
from datetime import datetime

class AuthDatabaseService:
    @staticmethod
    async def connection():
        """
        Establishes a connection to the MySQL database using aiomysql.
        Ensures the database exists, creating it if necessary.
        Returns:
            connection: aiomysql connection object.
        """
        try:
            # Initial connection without specifying a database
            initial_connection = await aiomysql.connect(
                host=os.getenv("AUTH_DB_HOST"),
                user=os.getenv("AUTH_DB_USER"),
                password=os.getenv("AUTH_DB_PASSWORD"),
                port=int(os.getenv("AUTH_DB_PORT", 3306))
            )

            db_name = os.getenv("AUTH_DB")
            async with initial_connection.cursor() as cursor:
                # Check if the database exists
                await cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
                result = await cursor.fetchone()
                if not result:
                    # Create the database if it doesn't exist
                    await cursor.execute(f"CREATE DATABASE {db_name}")
                    print(f"Database '{db_name}' created successfully.")
                else:
                    pass
            
            # Close the initial connection
            initial_connection.close()

            # Reconnect to the specified database
            connection = await aiomysql.connect(
                host=os.getenv("AUTH_DB_HOST"),
                user=os.getenv("AUTH_DB_USER"),
                password=os.getenv("AUTH_DB_PASSWORD"),
                db=db_name,
                port=int(os.getenv("AUTH_DB_PORT", 3306))
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
        connection = await AuthDatabaseService.connection()
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
            connection = await AuthDatabaseService.connection()
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
    async def auth_shutdown():
        """
        Close the MySQL connection during shutdown.
        """
        connection = await AuthDatabaseService.connection()
        connection.close()
    
    @staticmethod
    async def ensure_env_table_exists():
        """
        Checks if the `env_auth` table exists and creates it if it doesn't exist.
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS env_auth (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(50) UNIQUE NOT NULL,
            DB_MS VARCHAR(100),
            DB_USER VARCHAR(100),
            DB_PASSWORD VARCHAR(100),
            DB_HOST VARCHAR(100),
            DB_PORT INT,
            DB VARCHAR(100),
            DB_TABLES JSON,
            DB_DRIVER VARCHAR(100),
            MODEL VARCHAR(500),
            OPENAI_API_KEY VARCHAR(1000),
            WEAVIATE_URL VARCHAR(1000),
            WEAVIATE_API_KEY VARCHAR(1000),
            REDIS_HOST VARCHAR(1000),
            REDIS_PORT INT,
            MY_EMAIL VARCHAR(500),
            MY_EMAIL_PASSWORD VARCHAR(500),
            EMAIL_APP_PASSWORD VARCHAR(500),
            FRONTEND_API_URL VARCHAR(500),
            BACKEND_API_URL VARCHAR(500),
            REQUESTS_PER_WINDOW INT,
            TIME_WINDOW INT,
            ALLOWED_HTTP_REQUEST_METHODS JSON,
            RESTRICTED_HTTP_REQUEST_METHODS JSON,
            CRITICAL_RESTRICTED_HTTP_REQUEST_METHODS JSON,
            BACKEND_CORS_ORIGINS JSON,
            ACCESS_TOKEN_EXPIRE_MINUTES INT,
            REFRESH_TOKEN_EXPIRE_MINUTES INT,
            ALGORITHM VARCHAR(100),
            JWT_SECRET_KEY VARCHAR(1000),
            JWT_REFRESH_SECRET_KEY VARCHAR(1000)
        );
        """

        try:
            connection = await AuthDatabaseService.connection()
            async with connection.cursor() as cursor:
                await cursor.execute(create_table_query)
                await connection.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error ensuring table exists: {e}")
        finally:
            connection.close()

    @staticmethod
    async def retrieve_cache_history(userId: str, sessionId: str) -> Optional[List[Dict]]:
        """
        Retrieve cache history from MySQL based on userId and sessionId.

        Args:
            userId (str): User ID.
            sessionId (str): Session ID.

        Returns:
            Optional[List[Dict]]: List of cache history records, or None if no records found.
        """
        query = """
        SELECT userId, query, `system`, messageId, sessionId, timestamp, `sql`
        FROM Cache
        WHERE userId = %s AND sessionId = %s
        ORDER BY timestamp DESC;
        """
        connection = await AuthDatabaseService.connection()
        try:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (userId, sessionId))
                results = await cursor.fetchall()
                return results if results else []
        except Exception as e:
            raise RuntimeError(f"Error retrieving cache history: {e}")
        finally:
            connection.close()
            
    @staticmethod
    async def add_semantic_cache(
        query: str,
        system: str,
        userId: str,
        messageId: str,
        sessionId: str,
        timestamp: str,
        sql: str
    ) -> None:
        """
        Add a new entry to the Cache table in MySQL.

        Args:
            query (str): User query.
            system (str): System message.
            userId (str): User ID.
            messageId (str): Message ID.
            sessionId (str): Session ID.
            timestamp (str): Timestamp (in ISO 8601 format or equivalent).
            sql (str): SQL query.
        
        Returns:
            None
        """
        insert_query = """
        INSERT INTO Cache (userId, query, `system`, messageId, sessionId, timestamp, `sql`)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        
        connection = await AuthDatabaseService.connection()
        try:
            async with connection.cursor() as cursor:
                await cursor.execute(insert_query, (
                    userId, query, system, messageId, sessionId, timestamp, sql
                ))
                await connection.commit()
            print(f"Saved to cache for query: {query}")
        except Exception as e:
            print(f"Error saving to cache: {e}")
            raise RuntimeError(f"Failed to save cache for query: {query}")
        finally:
            connection.close()
    
    @staticmethod
    async def ensure_cache_schema_exists():
        """
        Checks if the `env_auth` table exists and creates it if it doesn't exist.
        """
        create_cache_table = """
        CREATE TABLE IF NOT EXISTS Cache (
        id INT AUTO_INCREMENT PRIMARY KEY,
        userId VARCHAR(255) NOT NULL,
        query TEXT,
        `system` TEXT,
        messageId VARCHAR(500),
        sessionId VARCHAR(500) NOT NULL,
        timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `sql` TEXT
        );
        """
        
        create_reaction_table = """
        CREATE TABLE IF NOT EXISTS Reaction (
        id INT AUTO_INCREMENT PRIMARY KEY,
        userId VARCHAR(255) NOT NULL,
        rating VARCHAR(50),
        feedbackText TEXT,
        messageId VARCHAR(500),
        sessionId VARCHAR(500) NOT NULL,
        timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        cacheId INT,
        FOREIGN KEY (cacheId) REFERENCES Cache(id) ON DELETE CASCADE
        );
        """

        try:
            connection = await AuthDatabaseService.connection()
            async with connection.cursor() as cursor:
                await cursor.execute(create_cache_table)
                await cursor.execute(create_reaction_table)
                await connection.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error ensuring table exists: {e}")
        finally:
            connection.close()
            
    @staticmethod
    async def add_reaction(
        userId: str,
        sessionId: str,
        messageId: str,
        rating: str,
        feedbackText: str
    ) -> tuple:
        """
        Add a new entry to the Reaction table in MySQL.

        Args:
            userId (str): User ID.
            sessionId (str): Session ID.
            messageId (str): Message ID.
            rating (str): User rating.
            feedbackText (str): User feedback text.
        
        Returns:
            tuple: The inserted data as a tuple.
        """
        # Generate the current timestamp in ISO 8601 format
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # SQL query to insert data into the Reaction table
        insert_query = """
        INSERT INTO Reaction (userId, sessionId, messageId, rating, feedbackText, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        
        connection = await AuthDatabaseService.connection()
        try:
            async with connection.cursor() as cursor:
                await cursor.execute(insert_query, (
                    userId, sessionId, messageId, rating, feedbackText, timestamp
                ))
                await connection.commit()
            print(f"Successfully stored reaction data for messageId: {messageId}")
            return (userId, sessionId, messageId, timestamp, rating, feedbackText)
        except Exception as e:
            print(f"Error storing reaction data: {e}")
            raise RuntimeError(f"Failed to store reaction data for messageId: {messageId}")
        finally:
            connection.close()

    @staticmethod
    async def fetch_system_and_feedback_text(message_id: str) -> Optional[Tuple[str, str, str]]:
        try:
            # Define the SQL query to join Cache and Reaction tables based on messageId
            query = """
            SELECT 
                c.system AS system_response,
                c.sql AS sql_query,
                r.feedbackText AS feedback_text
            FROM 
                Cache c
            LEFT JOIN 
                Reaction r
            ON 
                c.messageId = r.messageId
            WHERE 
                c.messageId = %s;
            ORDER BY 
                c.timestamp DESC;
            LIMIT 1;
            """

            # Use the existing connection method from AuthDatabaseService
            connection = await AuthDatabaseService.connection()

            try:
                async with connection.cursor() as cursor:
                    # Execute the query with the given messageId
                    await cursor.execute(query, (message_id,))
                    result = await cursor.fetchone()

                    # Extract and return the results
                    if result:
                        system_response, sql_query, feedback_text = result
                        return system_response or "", feedback_text or "", sql_query or ""
                    else:
                        return None, None, None
            finally:
                connection.close()

        except Exception as e:
            # Log and re-raise the exception
            print(f"Failed to fetch system and feedback text: {str(e)}")
            return None, None, None
        