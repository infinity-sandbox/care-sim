import os, re
from app.core.config import logger_settings, Settings
from typing import Optional
logger = logger_settings.get_logger(__name__)
import aiofiles

class Prompt:
    @staticmethod
    async def read_prompt(prompt_name) -> str:
        try:
            PROMPT_PATH = os.path.join(logger_settings.PROMPT_DIR, f'{prompt_name}.txt')
            async with aiofiles.open(PROMPT_PATH, 'r', encoding='utf-8') as file:
                return await file.read()
        except FileNotFoundError:
            logger.error(f"File {PROMPT_PATH} not found.")
            return ""
        except Exception as e:
            logger.error(f"An error occurred while reading {PROMPT_PATH}: {e}")
            return ""
    
    @staticmethod
    async def read_prompt_full(prompt_name: str, **kwargs) -> str:
        prompt_text = await Prompt.read_prompt(prompt_name)
        if prompt_text:  # Proceed only if the prompt was successfully read
            try:
                return prompt_text.format(**kwargs)
            except KeyError as e:
                logger.error(f"Error: Missing key {e} in formatting arguments.")
                return ""
            except Exception as e:
                logger.error(f"An error occurred during formatting: {e}")
                return ""
        return ""
    
    @staticmethod
    async def update_prompt(prompt_name, prompt_text) -> None:
        try:
            PROMPT_PATH = os.path.join(logger_settings.PROMPT_DIR, f'{prompt_name}.txt')
            async with aiofiles.open(PROMPT_PATH, 'w', encoding='utf-8') as file:
                await file.write(prompt_text)
        except FileNotFoundError:
            logger.error(f"File {PROMPT_PATH} not found.")
        except Exception as e:
            logger.error(f"An error occurred while updating {PROMPT_PATH}: {e}")
    
    @staticmethod
    async def save_prompt(prompt_name, prompt_text) -> None:
        try:
            PROMPT_PATH = os.path.join(logger_settings.PROMPT_DIR, f'{prompt_name}.txt')
            async with aiofiles.open(PROMPT_PATH, 'w', encoding='utf-8') as file:
                await file.write(prompt_text)
        except FileNotFoundError:
            logger.error(f"File {PROMPT_PATH} not found.")
        except Exception as e:
            logger.error(f"An error occurred while saving {PROMPT_PATH}: {e}")
            
    @staticmethod
    def get_prompt(prompt_name) -> str:
        try:
            PROMPT_PATH = os.path.join(logger_settings.PROMPT_DIR, f'{prompt_name}.txt')
            return PROMPT_PATH
        except Exception as e:
            logger.error(f"An error occurred while getting {PROMPT_PATH} path: {e}")
    
    @staticmethod
    def delete_prompt(prompt_name) -> None:
        try:
            PROMPT_PATH = os.path.join(logger_settings.PROMPT_DIR, f'{prompt_name}.txt')
            os.remove(PROMPT_PATH)
        except FileNotFoundError:
            logger.error(f"File {PROMPT_PATH} not found.")
        except Exception as e:
            logger.error(f"An error occurred while deleting {PROMPT_PATH}: {e}")
            
    @staticmethod
    async def create_prompt(prompt_name, prompt_text) -> None:
        try:
            PROMPT_PATH = os.path.join(logger_settings.PROMPT_DIR, f'{prompt_name}.txt')
            # Create the directory path if it doesn't exist
            os.makedirs(os.path.dirname(PROMPT_PATH), exist_ok=True)
            async with aiofiles.open(PROMPT_PATH, 'w', encoding='utf-8') as file:
                await file.write(prompt_text)
        except FileNotFoundError:
            logger.error(f"File {PROMPT_PATH} not found.")
        except Exception as e:
            logger.error(f"An error occurred while creating and writting {PROMPT_PATH}: {e}")
            
    @staticmethod
    def list_prompts() -> list:
        try:
            return os.listdir(logger_settings.PROMPT_DIR)
        except FileNotFoundError:
            logger.error(f"Directory {logger_settings.PROMPT_DIR} not found.")
        except Exception as e:
            logger.error(f"An error occurred while listing {logger_settings.PROMPT_DIR}: {e}")
            
    @staticmethod
    def search_prompts(prompt_name) -> list:
        # Compile regex pattern to match prompt_name anywhere in the name and optionally end with .txt
        pattern = re.compile(rf'.*{re.escape(prompt_name)}.*(?:\.txt)?', re.IGNORECASE)
        
        matches = []
        try:
            # Traverse directory recursively
            for root, dirs, files in os.walk(logger_settings.PROMPT_DIR):
                # Search in directories
                matches.extend([os.path.join(root, dir) for dir in dirs if pattern.match(dir)])
                # Search in files
                matches.extend([os.path.join(root, file) for file in files if pattern.match(file)])
                
        except FileNotFoundError:
            print(f"Directory {logger_settings.PROMPT_DIR} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        return matches
