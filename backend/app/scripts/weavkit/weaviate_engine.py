import hashlib
import ssl
import sys, os
import time
import weaviate
from weaviate import Client
from typing import Optional, List, Tuple
from weaviate.embedded import EmbeddedOptions
import json
from pathlib import Path
from app.core.config import logger_settings, Settings
logger = logger_settings.get_logger(__name__)
from datetime import datetime
from utils.vapor.engine.scheduler import start_scheduler
from weaviate.util import generate_uuid5
from app.services.langchain_service import LangchainAIService
from app.services.openai_service import OpenAIService
from openai import OpenAI
from utils.docker.util import is_docker
from app.prompts.main import Prompt
from app.scripts.com.arcturustech.trace_compiler import main
from app.sql.main import SqlQuery
import ast
import re
import asyncio

class WeaviateService:
    @staticmethod
    async def setup_client() -> Optional[Client]:
        """
        Setup the Weaviate Client
        @returns Optional[Client] - The Weaviate Client
        """
        logger.info("Setting up weaviate client!")

        openai_key = logger_settings.OPENAI_API_KEY
        weaviate_url = logger_settings.WEAVIATE_URL
        weaviate_key = logger_settings.WEAVIATE_API_KEY

        if openai_key == "":
            logger.warning("OPENAI_API_KEY environment variable not set")
            return None

        # Weaviate Embedded
        elif weaviate_url == "":
            try:
                _create_unverified_https_context = ssl._create_unverified_context
                logger.debug("Set _create_unverified_https_context")
            except AttributeError as e:
                logger.exception(f"AttributeError Occurred: {str(e)}")
            else:
                ssl._create_default_https_context = _create_unverified_https_context

            logger.warning("WEAVIATE_URL environment variable not set. Using Weaviate Embedded!")
            client = weaviate.Client(
                additional_headers={"X-OpenAI-Api-Key": openai_key},
                embedded_options=EmbeddedOptions(
                    persistence_data_path="./.applicare-ai/local/share/",
                    binary_path="./.applicare-ai/cache/weaviate-embedded",
                ),
            )
            logger.debug("Client connected to local Weaviate server!")
            return client

        elif weaviate_key == "":
            logger.warning("WEAVIATE_API_KEY environment variable not set!")
        
        url = weaviate_url
        auth_config = weaviate.AuthApiKey(api_key=weaviate_key)

        client = await asyncio.to_thread(
            weaviate.Client,
            url=url,
            additional_headers={"X-OpenAI-Api-Key": openai_key},
            auth_client_secret=auth_config,
        )
        
        # client = weaviate.Client(
        #     url=url,
        #     additional_headers={"X-OpenAI-Api-Key": openai_key},
        #     auth_client_secret=auth_config,
        # )

        wait_time_limit = 300
        while not await asyncio.to_thread(client.is_ready):
            if not wait_time_limit:
                logger.critical("TIMEOUT: Weaviate not ready. " \
                                "Try again or check if weaviate is running.")
                sys.stderr.write("\rTIMEOUT: Weaviate not ready. "
                                "Try again or check if weaviate is running.\n")
                sys.exit(1)
            sys.stdout.write(
                f"\rWait for weaviate to get ready. {wait_time_limit:02d} seconds left.")
            sys.stdout.flush()
            wait_time_limit -= 2
            await asyncio.sleep(2.0)
        
        logger.info("Client connected to Weaviate Instance!")
        return client

    @staticmethod
    def hash_string(text: str) -> str:
        """Hash a string
        @parameter text : str - The string to hash
        @returns str - Hashed string
        """
        # Create a new sha256 hash object
        sha256 = hashlib.sha256()

        # Update the hash object with the bytes-like object (filepath)
        sha256.update(text.encode())

        logger.debug(f"Hashed string {text} to {sha256.hexdigest()}")
        # Return the hexadecimal representation of the hash
        return str(sha256.hexdigest())

    @staticmethod
    def import_suggestions(client: Client, suggestions: list[str]) -> None:
        """Imports a list of strings as suggestions to the Weaviate Client
        @parameter client : Client - Weaviate Client
        @parameter suggestions : list[str] - List of strings
        @returns None
        """
        with client.batch as batch:
            batch.batch_size = 100
            for i, d in enumerate(suggestions):
                logger.info(f"({i+1}/{len(suggestions)}) Importing suggestion")
                properties = {
                    "suggestion": d,
                }

                client.batch.add_data_object(properties, "Suggestion")

        logger.info("Imported all suggestions")

    @staticmethod
    def import_weaviate_suggestions(client: Client) -> None:
        """Imports a list of strings as suggestions to the Weaviate Client
        @parameter client : Client - Weaviate Client
        @returns None
        """
        # TODO: convert this suggestion_list into a json file
        # TODO: instead of json the list must came from the database (short distance)
        suggestion_list = [
            "who are applicare?",
            "what is there technology",
        ]
        WeaviateService.import_suggestions(client, suggestion_list)
        logger.info("Imported suggestions")

    @staticmethod
    async def init_schema(model: str):
        logger.info("Creating Main Schema (Cache, Reaction and Suggestion Schema)")
        model = logger_settings.MODEL
        client = await WeaviateService.setup_client()

        cache_schema = {
            "classes": [    
                #--------------------------Cache Schema---------------------------
                {
                    "class": "Cache",
                    "description": "Cache of Documentations and their queries",
                    "vectorizer": "text2vec-openai",
                    "properties": [
                        {
                            "name": "userId",
                            "dataType": ["text"],
                            "description": "User email/id Identifier",
                            "moduleConfig": {
                                "text2vec-openai": {
                                    "skip": True,
                                    "vectorizePropertyName": False,
                                }
                            },
                        },
                        {
                            "name": "query",
                            "dataType": ["text"],
                            "description": "Query",
                            "moduleConfig": {
                                "text2vec-openai": {
                                    "skip": False,
                                    "vectorizePropertyName": True,
                                }
                            },
                        },
                        {
                            "name": "system",
                            "dataType": ["text"],
                            "description": "System message",
                            "moduleConfig": {
                                "text2vec-openai": {
                                    "skip": True,
                                    "vectorizePropertyName": False,
                                }
                            },
                        },
                        {
                            "name": "sql",
                            "dataType": ["text"],
                            "description": "sql query",
                            "moduleConfig": {
                                "text2vec-openai": {
                                    "skip": True,
                                    "vectorizePropertyName": False,
                                }
                            },
                        },
                        {
                            "name": "messageId",
                            "dataType": ["text"],
                            "description": "Identifier of the message or interaction to " \
                                "which the reaction is related",
                            "moduleConfig": {
                                "text2vec-openai": {
                                    "skip": True,
                                    "vectorizePropertyName": False,
                                }
                            },
                        },
                        {
                            "name": "sessionId",
                            "dataType": ["text"],
                            "description": "Session Identifier",
                            "moduleConfig": {
                                "text2vec-openai": {
                                    "skip": True,
                                    "vectorizePropertyName": False,
                                }
                            },
                        },
                        {
                            "name": "timestamp",
                            "dataType": ["date"],
                            "description": "Timestamp of the cached input"
                        },
                        {
                            "name": "reactions",
                            "dataType": ["Reaction"],
                            "description": "Reference to reactions"                   
                        },
                    ],
                    "moduleConfig": {"generative-openai": {"model": model}},
                    "vectorizer": "text2vec-openai",
                },
                #--------------------------Reaction Schema---------------------------
                {
                    "class": "Reaction",
                    "description": "Represents user reactions for a chatbot",
                    "properties": [
                        {
                            "name": "userId",
                            "dataType": ["text"],
                            "description": "Identifier of the user who reacted",
                            "moduleConfig": {
                                "text2vec-openai": {
                                    "skip": True,
                                    "vectorizePropertyName": False,
                                }
                            },
                        },
                        {
                            "name": "rating",
                            "dataType": ["text"],
                            "description": "String rating or score (e.g., 0 & 1)",
                            "moduleConfig": {
                                "text2vec-openai": {
                                    "skip": True,
                                    "vectorizePropertyName": False,
                                }
                            },
                        },
                        {
                            "name": "feedbackText",
                            "dataType": ["text"],
                            "description": "Textual feedback or review",
                            "moduleConfig": {
                                "text2vec-openai": {
                                    "skip": True,
                                    "vectorizePropertyName": False,
                                }
                            },
                        },
                        {
                            "name": "messageId",
                            "dataType": ["text"],
                            "description": "Identifier of the message or interaction to " \
                                "which the reaction is related",
                            "moduleConfig": {
                                "text2vec-openai": {
                                    "skip": True,
                                    "vectorizePropertyName": False,
                                }
                            },
                        },
                        {
                            "name": "sessionId",
                            "dataType": ["text"],
                            "description": "Session Identifier",
                            "moduleConfig": {
                                "text2vec-openai": {
                                    "skip": True,
                                    "vectorizePropertyName": False,
                                }
                            },
                        },
                        {
                            "name": "timestamp",
                            "dataType": ["date"],
                            "description": "Timestamp of the reaction"
                        },
                        {
                            "name": "cache",
                            "dataType": ["Cache"],
                            "description": "Reference to reactions"              
                        },
                    ],
                    "moduleConfig": {"generative-openai": {"model": model}},
                    "vectorizer": "text2vec-openai",
                },
                #--------------------------Suggestion Schema---------------------------
                {
                    "class": "Suggestion",
                    "description": "List of possible prompts",
                    "properties": [
                        {
                            "name": "suggestion",
                            "dataType": ["text"],
                            "description": "Query",
                            "moduleConfig": {
                                "text2vec-openai": {
                                    "skip": False,
                                    "vectorizePropertyName": True,
                                }
                            },
                        },
                    ],
                    "moduleConfig": {"generative-openai": {"model": model}},
                    "vectorizer": "text2vec-openai",
                }
            ]
        }
        
        #---------------------------------document schema created----------------------------------
        cache_exists = await asyncio.to_thread(client.schema.exists, "Cache")
        if cache_exists:
            user_input = input(
                "Cache class already exists, do you want to overwrite it? (y/n): "
            )
            if user_input.strip().lower() == "y":
                # Delete existing schemas
                await asyncio.to_thread(client.schema.delete_class, "Cache")
                await asyncio.to_thread(client.schema.delete_class, "Reaction")
                await asyncio.to_thread(client.schema.delete_class, "Suggestion")

                # Create the new schema
                await asyncio.to_thread(client.schema.create, cache_schema)
                logger.warning("All schemas deleted! Cache, Reaction & Suggestion schema created")
            else:
                logger.warning("Skipped deleting All schemas, nothing changed")
        else:
            # Create the schema if it doesn't exist
            await asyncio.to_thread(client.schema.create, cache_schema)
            logger.info("All schema created")

        if client._connection.embedded_db:
            logger.info("Stopping Weaviate Embedded")
            # client._connection.embedded_db.stop()
            await asyncio.to_thread(client._connection.embedded_db.stop)
         
    # Loading Files from Directory
    @staticmethod
    def load_suggestions(file_path: Path) -> dict:
        """Loads json file with suggestions
        @param dir_path : Path - Path to directory
        @returns dict - Dictionary of filename (key) and their content (value)
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check if data is a list
        if not isinstance(data, list):
            logger.warning(f"{file_path} is not a list.")
            return []

        # Check if every item in the list is a string
        if not all(isinstance(item, str) for item in data):
            logger.warning(f"{file_path} is not a list of strings.")
            return []

        return data

class WeaviateQueryEngine:
    """
    An interface for applicare query engine.
    """
    client: Client = None  # Class attribute for the client

    def __init__(self):
        """
        Constructor for WeaviateQueryEngine.
        """
        logger.info("WeaviateQueryEngine initialized")

    @classmethod
    async def initialize(cls):
        """
        Asynchronous method to initialize the Weaviate client.
        This will be called to set up the client asynchronously.
        """
        if cls.client is None:
            cls.client = await WeaviateService.setup_client()  # Asynchronous initialization of the client
            logger.info("WeaviateQueryEngine client initialized")

    def get_client(self) -> Client:
        """
        Get the Weaviate client.
        """
        return WeaviateQueryEngine.client
