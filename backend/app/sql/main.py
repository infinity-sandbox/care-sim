import os, re
from typing import Optional
from app.core.config import logger_settings, Settings
logger = logger_settings.get_logger(__name__)
import aiofiles

class SqlQuery:
    @staticmethod
    async def read_sql(sql_name) -> str:
        try:
            SQL_PATH = os.path.join(logger_settings.SQL_DIR, f'{sql_name}.sql')
            async with aiofiles.open(SQL_PATH, 'r', encoding='utf-8') as file:
                return await file.read()
        except FileNotFoundError:
            logger.error(f"File {SQL_PATH} not found.")
            return ""
        except Exception as e:
            logger.error(f"An error occurred while reading {SQL_PATH}: {e}")
            return ""
    
    @staticmethod
    async def read_sql_full(sql_name: str, **kwargs) -> str:
        sql_text = await SqlQuery.read_sql(sql_name)
        if sql_text:  # Proceed only if the sql was successfully read
            try:
                return sql_text.format(**kwargs)
            except KeyError as e:
                logger.error(f"Error: Missing key {e} in formatting arguments.")
                return ""
            except Exception as e:
                logger.error(f"An error occurred during formatting: {e}")
                return ""
        return ""
    
    @staticmethod
    async def update_sql(sql_name, sql_text) -> None:
        try:
            SQL_PATH = os.path.join(logger_settings.SQL_DIR, f'{sql_name}.sql')
            async with aiofiles.open(SQL_PATH, 'w', encoding='utf-8') as file:
                await file.write(sql_text)
        except FileNotFoundError:
            logger.error(f"File {SQL_PATH} not found.")
        except Exception as e:
            logger.error(f"An error occurred while updating {SQL_PATH}: {e}")
    
    @staticmethod
    async def save_sql(sql_name, sql_text) -> None:
        try:
            SQL_PATH = os.path.join(logger_settings.SQL_DIR, f'{sql_name}.sql')
            async with aiofiles.open(SQL_PATH, 'w', encoding='utf-8') as file:
                await file.write(sql_text)
        except FileNotFoundError:
            logger.error(f"File {SQL_PATH} not found.")
        except Exception as e:
            logger.error(f"An error occurred while saving {SQL_PATH}: {e}")
            
    @staticmethod
    def get_sql(sql_name) -> str:
        try:
            SQL_PATH = os.path.join(logger_settings.SQL_DIR, f'{sql_name}.sql')
            return SQL_PATH
        except Exception as e:
            logger.error(f"An error occurred while getting {SQL_PATH} path: {e}")
    
    @staticmethod
    def delete_sql(sql_name) -> None:
        try:
            SQL_PATH = os.path.join(logger_settings.SQL_DIR, f'{sql_name}.sql')
            os.remove(SQL_PATH)
        except FileNotFoundError:
            logger.error(f"File {SQL_PATH} not found.")
        except Exception as e:
            logger.error(f"An error occurred while deleting {SQL_PATH}: {e}")
            
    @staticmethod
    async def create_sql(sql_name, sql_text) -> None:
        try:
            SQL_PATH = os.path.join(logger_settings.SQL_DIR, f'{sql_name}.sql')
            # Create the directory path if it doesn't exist
            os.makedirs(os.path.dirname(SQL_PATH), exist_ok=True)
            async with aiofiles.open(SQL_PATH, 'w', encoding='utf-8') as file:
                await file.write(sql_text)
        except FileNotFoundError:
            logger.error(f"File {SQL_PATH} not found.")
        except Exception as e:
            logger.error(f"An error occurred while creating and writting {SQL_PATH}: {e}")
            
    @staticmethod
    def list_sqls() -> list:
        try:
            return os.listdir(logger_settings.SQL_DIR)
        except FileNotFoundError:
            logger.error(f"Directory {logger_settings.SQL_DIR} not found.")
        except Exception as e:
            logger.error(f"An error occurred while listing {logger_settings.SQL_DIR}: {e}")
            
    @staticmethod
    def search_sqls(sql_name) -> list:
        # Compile regex pattern to match sql_name anywhere in the name and optionally end with .sql
        pattern = re.compile(rf'.*{re.escape(sql_name)}.*(?:\.sql)?', re.IGNORECASE)
        
        matches = []
        try:
            # Traverse directory recursively
            for root, dirs, files in os.walk(logger_settings.SQL_DIR):
                # Search in directories
                matches.extend([os.path.join(root, dir) for dir in dirs if pattern.match(dir)])
                # Search in files
                matches.extend([os.path.join(root, file) for file in files if pattern.match(file)])
                
        except FileNotFoundError:
            print(f"Directory {logger_settings.SQL_DIR} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        
        return matches
