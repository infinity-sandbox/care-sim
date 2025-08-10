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
from app.services.auth_service import AuthDatabaseService


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

class SimpleWeaviateQueryEngine(WeaviateQueryEngine):
    # Custom methods
    async def retrieve_semantic_cache(
        self, query: str, dist: float = 0.3
    ) -> Optional[List]:    
        """Retrieve results from semantic cache based on query and distance threshold
        @parameter query - str - User query
        @parameter dist - float - Distance threshold
        @returns Optional[dict] - List of results or None
        """
        logger.info("Retrieving data from cache memory ... ")
        # Run the Weaviate query in a separate thread to avoid blocking
        query_results = await asyncio.to_thread(
            WeaviateQueryEngine.client.query.get(
                class_name="Cache",
                properties=["userId", "query", "system", "sql", "messageId", "sessionId", 
                            "timestamp"],
            )
            .with_near_text(content={"concepts": query})
            .with_additional(properties=["distance"])
            .with_limit(10)
            .do
        )

        results = query_results["data"]["Get"]["Cache"]

        if not results:
            return None
        else:
            __cached__ = results

        try:
            reaction_query = f"""
            {{
            Get {{
                Reaction {{
                    userId
                    rating
                    feedbackText
                    messageId
                    sessionId
                    timestamp
                    }}
                }}
            }}
            """

            reaction_response = await asyncio.to_thread(
                WeaviateQueryEngine.client.query.raw, reaction_query
            )
            __reaction__ = reaction_response.get("data", {}).get("Get", {}).get("Reaction", [])

            # Create a dictionary to store reactions by messageId
            reactions_dict = {}
            if __reaction__:
                for reaction in __reaction__:
                    message_id = reaction.get("messageId")
                    if message_id in reactions_dict:
                        reactions_dict[message_id].append(reaction)
                    else:
                        reactions_dict[message_id] = [reaction]

            # Update Cache entries with reactions
            if __cached__:
                for cached_item in __cached__:
                    message_id = cached_item.get("messageId")
                    if message_id in reactions_dict:
                        cached_item["reactions"] = reactions_dict[message_id]
                    else:
                        cached_item["reactions"] = []
            
            # Iterate through the cached items and update __cached__ in place
            if (__cached__ != None or __cached__ != [] or __cached__):
                index = 0
                while index < len(__cached__):
                    reactions = __cached__[index]["reactions"]

                    # Find the latest timestamp reaction for the messageId
                    if ((reactions) or (reactions != [])):
                        latest_reaction = max(reactions, 
                                              key=lambda reaction: reaction["timestamp"])
                        __cached__[index]["reactions"] = [latest_reaction]

                        if latest_reaction["rating"] != "like":
                            del __cached__[index]
                        else:
                            index += 1
                    else:
                        break
            else:
                __cached__ = results

            retrieved_caches = []
        
            if ((__cached__ != []) or (__cached__ != None)):

                for result in __cached__:
                    if query == result["query"] or result["_additional"]["distance"] <= dist:
                        logger.debug(f"Retrieved cache for query {query}...")
                        
                        retrieved_caches.append({"messageId": result["messageId"],
                                                 "query": result["query"],
                                                 "system": result["system"], 
                                                 "sql": result["sql"],
                                                 "distance": result["_additional"]["distance"]})
                    else:
                        retrieved_caches = []
                logger.debug(f'Retrieved cache: {retrieved_caches}')
                return retrieved_caches
            else: 
                logger.debug(f'Retrieved cache: {retrieved_caches}')
                return retrieved_caches
        except Exception as e:
            logger.exception(str(e))
            return []
        
    async def retrieve_cache_history(self, userId: str, sessionId: str) -> Optional[List]:
        """Retrieve cache history based on userId
        @parameter userId - str - User ID
        @returns Optional[dict] - List of results or None
        """
        try:
            where_clauses = [
                {
                    "path": ["userId"],
                    "operator": "Equal",
                    "valueText": userId,
                }
            ]
            if True:
                where_clauses.append(
                    {
                        "path": ["sessionId"],
                        "operator": "Equal",
                        "valueText": sessionId
                    }
                )

            # Combine the where clauses using the OR operator
            where_clauses = {
                "operator": "And",
                "operands": where_clauses
            }

            result = await asyncio.to_thread(
                WeaviateQueryEngine.client.query
                .get("Cache", ["query", "system", "userId", 
                               "messageId", "sessionId", "timestamp", "sql"])
                .with_where(where_clauses)
                .do()
            )
            
            logger.debug(f"Session cache returned for userId={userId} and sessionId={sessionId} " \
                     f"is: {result['data']['Get']['Cache']}")

            if not result["data"]["Get"]["Cache"]:
                return []
            else:
                # Filter the results based on the date range and userId
                filtered_results = result["data"]["Get"]["Cache"]
                filtered_results.sort(key=lambda x: x["timestamp"])
                filtered_results = filtered_results[:]
                return filtered_results
        except Exception as e:
            logger.exception(str(e))
            return None
        
    async def add_semantic_cache(self, query: str, system: str, userId: str,
                           messageId: str, sessionId: str, timestamp: str, sql: str) -> None:
        """Add results to semantic cache
        @parameter query : str - User query
        @parameter results : list[dict] - Results from Weaviate
        @parameter system : str - System message response 
        @returns None
        """
        _userId = str(userId)
        _messageId = str(messageId)
        _sessionId = str(sessionId)
        _timestamp = timestamp
        _query = str(query)
        _system = str(system)
        _sql = str(sql)

        WeaviateQueryEngine.client.batch.configure(
            batch_size=100,  # Specify the batch size for auto batching
            num_workers=10,   # Maximum number of parallel threads used during import
            dynamic=True,   # Weaviate will dynamically adjust the batch size
        )
        await asyncio.to_thread(self._add_to_batch, _userId, _messageId, _sessionId, _timestamp, _query, _system, _sql)
        logger.info(f"Saved to cache for query {query}")

    def _add_to_batch(self, userId: str, messageId: str, sessionId: str, timestamp: str,
                      query: str, system: str, sql: str) -> None:
        """Helper function to perform the actual batch operation in a blocking manner."""
        with WeaviateQueryEngine.client.batch as batch:
            batch.add_data_object(
                data_object={
                    "userId": userId,
                    "messageId": messageId,
                    "sessionId": sessionId,
                    "timestamp": timestamp,
                    "query": query,
                    "system": system,
                    "sql": sql
                },
                uuid=generate_uuid5(messageId),
                class_name="Cache"
            )
            
    async def add_reaction(self, userId: str, sessionId: str, messageId: str, rating: str,
                     feedbackText: str) -> tuple:
        
        # create time_stamp
        datetime_now = datetime.now()
        rfcc = datetime_now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        

        _messageId = str(messageId)
        _sessionId = str(sessionId)
        _timestamp = rfcc
        _userId = str(userId)
        _rating = str(rating)
        _feedbackText = str(feedbackText)
        
        # Perform batch operation asynchronously
        await asyncio.to_thread(self._add_to_batch_reaction, _userId, _messageId, _sessionId, _timestamp, _rating, _feedbackText)

        logger.info(f"Succesfully stored reaction data!")

        return (_userId, _sessionId, _messageId, _timestamp, _rating, _feedbackText)

    def _add_to_batch_reaction(self, userId: str, messageId: str, sessionId: str, timestamp: str,
                                rating: str, feedbackText: str) -> None:
        """Helper function to perform the actual batch operation in a blocking manner."""
        WeaviateQueryEngine.client.batch.configure(
            batch_size=100,  # Specify the batch size for auto batching
            num_workers=10,  # Maximum number of parallel threads used during import
            dynamic=True     # Weaviate will dynamically adjust the batch size
        )

        with WeaviateQueryEngine.client.batch as batch:
            batch.add_data_object(
                data_object={
                    "userId": userId,
                    "rating": rating,
                    "feedbackText": feedbackText,
                    "messageId": messageId,
                    "sessionId": sessionId,
                    "timestamp": timestamp,
                },
                uuid=generate_uuid5(messageId),
                class_name="Reaction"
            )
            
    def get_suggestions(self, query: str) -> list[str]:
        """Retrieve suggestions based on user query
        @parameter query : str - User query
        @returns list[str] - List of possible autocomplete suggestions
        """
        query_results = (
            WeaviateQueryEngine.client.query.get(
                class_name="Suggestion",
                properties=["suggestion"],
            )
            .with_bm25(query=query)
            .with_additional(properties=["score"])
            .with_limit(3)
            .do()
        )

        results = query_results["data"]["Get"]["Suggestion"]

        if not results:
            return []

        suggestions = []

        for result in results:
            if float(result["_additional"]["score"]) > 0.5:
                suggestions.append(result["suggestion"])

        return suggestions
    
class AdvancedWeaviateQueryEngine(SimpleWeaviateQueryEngine):
    async def query(self, user_q: str, userId: str, sessionId: str, url: str, settings: Optional[Settings] = None) -> tuple:
        """Execute a query to a receive specific chunks from Weaviate
        @parameter query_string : str - Search query
        @returns tuple - (system message, iterable list of results)
        """
        # english = await OpenAIService.language_detector(user_q, settings=settings)
        # if english == "true":
        #     logger.info(f"Non-English word detected. Translating to english...")
        #     out = await OpenAIService.in_translation(user_q, settings=settings)
        #     question = str(out)
        #     logger.info(f"Translated question: {question}")
        # else:
        #     question = str(user_q)
        #     logger.info(f"English word detected. No translation needed.")
        
        question = str(user_q)
        _sessionId = str(sessionId)
        _userId = str(userId)
        _messageId, _timestamp = get_session_params(question)
        
        # await start_scheduler()
        
        try: 
            classiffication_applicare_recommendation = await OpenAIService.classify_applicare_recommendation(question, settings=settings)
            if classiffication_applicare_recommendation == "true":
                schema = await LangchainAIService.get_schema(settings=settings)
                formated_prompt = await Prompt.read_prompt_full(
                    "com/arcturustech/question_recommendation_response",
                    schema=schema,
                    question=question
                )
                API_RESPONSE = await OpenAIService.get_completion(
                    [{"role": "system", "content": formated_prompt}],
                    model=logger_settings.MODEL,
                    settings=settings
                )
                response = API_RESPONSE.choices[0].message.content.strip().strip('"')
                system_msg = str(response)
                return (system_msg, _userId, _messageId, _sessionId, _timestamp)
            else: 
                logger.warning(f"Not a applicare recommendation classification!")
                
        except Exception as e:
            logger.error(f"Error responding recommended questions: {e}")
        
        # results = self.retrieve_semantic_cache(question)
        # def cache_results(results) -> str:
        #     formatted_string = ""
        #     if results:
        #         for i, d in enumerate(results):
        #             previous_question = d["query"]
        #             previous_answer = d["sql"]
                    
        #             # Concatenating into a formatted string
        #             formatted_string += f'question: "{previous_question}"\n'
        #             formatted_string += f'sql query: "{previous_answer}"\n\n'
            
        #     return formatted_string.strip()  # Remove the trailing newline
    
        # cache = cache_results(results)
        # logger.debug(f'CACHE:\n{cache}')
        classificatioin_applicare = await OpenAIService.classify_applicare(question, settings=settings)
        
        if classificatioin_applicare == "true":
            pass
        else:
            (sql_chain, 
            _, 
            response_sql_chain, 
            _, 
            _) = await LangchainAIService.get_chains(settings=settings)

            # TODO: uncomment when we need akhil classification
            # if OpenAIService.classify_akhil(question, settings=settings) == 'true':
            #     query = OpenAIService.classify_akhil_lab(question, settings=settings)
        
        
            
        try:
            if classificatioin_applicare == 'true':
                query = await OpenAIService.classify_parameter(question, settings=settings)
            else:
                # Generate the SQL query from the question
                query = await sql_chain.ainvoke({
                                            "question": question,
                                        })
        except Exception as e:
            logger.error(f"Error generating SQL query: {e}")
            query = await sql_chain.ainvoke({
                                        "question": question,
                                    })
            
        # Run the generated SQL query with retries
        try:
            #query, question, max_retries = 7, settings
            if classificatioin_applicare == 'true':
                response_cause = await main(query, settings=settings)
                response, query = await LangchainAIService.run_query_with_retries(query=query, 
                                                                            question=question, 
                                                                            max_retries=7, 
                                                                            settings=settings)
                logger.debug(f"\nQuery: {query}\nSQL Response: {response_cause}\n{response}\nResponse Type: {type(response)}\n")
            else:
                response, query = await LangchainAIService.run_query_with_retries(query=query, 
                                                                            question=question, 
                                                                            max_retries=7, 
                                                                            settings=settings)
                
                logger.debug(f"\nQuery: {query}\nSQL Response: {response}\nResponse Type: {type(response)}\n")
            
            if response and isinstance(response, str):
                response = await LangchainAIService.truncate_response(response)
            else:
                response = await LangchainAIService.truncate_response(str(response))
            
            # retrive memory cache
            # TODO: change this to mysql storage, of course localhost 
            # memory = await self.retrieve_cache_history(_userId, _sessionId)
            memory = await AuthDatabaseService.retrieve_cache_history(_userId, _sessionId)
            
            def cache_results_with_roles(memory, question) -> str:
                formatted_string = ""
                
                if memory:
                    for i, d in enumerate(memory):
                        previous_question = d["query"]
                        previous_answer = d["system"]

                        # Concatenating into a formatted string with roles
                        formatted_string += f'role: user\ncontent: "{previous_question}"\n\n'
                        formatted_string += f'role: assistant\ncontent: "{previous_answer}"\n\n'
                
                # Adding the latest user question at the end
                formatted_string += f'role: user\ncontent: "{question}"\n'
                
                return formatted_string.strip()  # Remove the trailing newline
            
            logger.debug(f'MEMORY:\n{cache_results_with_roles(memory, question)}')

            if classificatioin_applicare == 'true':
                def fun(data, columns):
                    result = []  # Initialize a list to hold the result strings
                    
                    # Check if data is empty
                    if not data:
                        return "No slowness was detected at this time."
                    
                    result.append("These are the slow transaction details:\n")
                    
                    for row in data:
                        logger.debug(f"debugging row: {row}")                            
                        row_dict = dict(zip(columns, row))

                        # Convert datetime string to datetime object and format it if the "started" column exists
                        if "started" in row_dict:
                            # Check if the "started" value is a string that needs conversion
                            if isinstance(row_dict["started"], str):
                                started_str = row_dict["started"]

                            if len(started_str.split()) == 6:  # Has seconds
                                dt = datetime.strptime(started_str, "%Y %m %d %H %M %S")
                            else:  # No seconds
                                dt = datetime.strptime(started_str, "%Y %m %d %H %M")

                            row_dict["started"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                            
                            # row_dict["started"] = datetime.strptime(row_dict["started"], "%Y %m %d %H %M %S").strftime("%Y-%m-%d %H:%M:%S")

                        # Convert duration to milliseconds if the column exists
                        if "duration" in row_dict:
                            row_dict["duration_ms"] = row_dict["duration"] / 1_000_000  # Convert ns to ms

                        # Add formatted rows to result list
                        # result.append("\n".join(f"{col}: {row_dict[col]}" for col in columns))
                        # Add formatted rows to result list, but exclude the "duration" column
                        for col in columns:
                            if (col != "duration") and (col != "trace"):  # Exclude "duration" from the display
                                result.append(f"{col}: {row_dict.get(col, 'N/A')}")  # Safely handle missing keys
                        
                        if "duration_ms" in row_dict:
                            result.append(f"duration (ms): {row_dict['duration_ms']}")  # Include converted value in output
                    
                    return "\n".join(result)  # Join and return the result as a single string
                
                # If response_sl is empty, return a message early
                if not response.strip():
                    system_msg = "No slowness was detected at this time."
                else:
                    # Step 1: Use regex to replace datetime.datetime with the actual datetime string
                    response = re.sub(r'datetime\.datetime\((.*?)\)', lambda m: '"' + m.group(1).replace(', ', ' ') + '"', response)

                    # Step 2: Now evaluate the modified string to convert it to a list of tuples
                    data = ast.literal_eval(response)

                    # Assuming the columns are like this:
                    columns = ["trace", "client_id", "server_name", "name", "started", "duration"]
                    system_msg = fun(data, columns)
                    
                    #TODO: change this demo_beta and demo a variable that came from the user
                    link = f"For more details, please visit this link.\n" \
                        f"{url}/applicare/console/home.do#/dashboard/userExperience/realTimeTransactions"
                    
                    system_msg = "\n\n".join([system_msg, response_cause, link])
            else:
                system_msg = await response_sql_chain.ainvoke(
                        {
                            "question": question, 
                            "query": query, 
                            "response": response, 
                            "username": userId,
                            "memory": cache_results_with_roles(memory, question)
                        }
                    )
            
            # system_msg = LangchainAIService.remove_symbols_from_response(system_msg)
            
            logger.debug(f'Calling OpenAI API with model={settings.MODEL}\n\n' \
                         f'query={question}\nanswer={system_msg}')
            
            # if english == "true":
            #     system_msg = await OpenAIService.out_translation(user_q, system_msg, settings=settings)
            #     logger.debug(f"\n\nTranslated Answer: {system_msg}")
                
            logger.info("User Question Executed!")
            
            await AuthDatabaseService.add_semantic_cache(
                                    question, 
                                    system_msg, 
                                    _userId, 
                                    _messageId, 
                                    _sessionId, 
                                    _timestamp,
                                    query
                                    )
                
            return (system_msg, _userId, _messageId, _sessionId, _timestamp)
        except Exception as e:
            logger.error(f"Error getting response: {e}")
            return None, None, None, None, None
   
    
    async def query_regenerator(self, 
                          question: str, 
                          userId: str, 
                          sessionId: str, 
                          messageId: str,
                          settings: Optional[Settings] = None) -> tuple:
        """Execute a query to a receive specific chunks from Weaviate
        @parameter query_string : str - Search query
        @returns tuple - (system message, iterable list of results)
        """
        logger.info(f"Using model: {logger_settings.MODEL}")

        # Get the session and user IDs from parameters
        _sessionId = str(sessionId)
        _userId = str(userId)
        mI, _timestamp = get_session_params(question)
        _messageId = str(messageId)

        # def fetch_system_and_feedbackText() -> Optional[Tuple[str, str, str]]:
        #     try:
        #         # Define the GraphQL queries for Cache and Reaction using messageId
        #         cache_query = f"""
        #         {{
        #             Get {{
        #                 Cache {{
        #                     system
        #                     messageId
        #                     sql
        #                 }}
        #             }}
        #         }}
        #         """
                
        #         reaction_query = f"""
        #         {{
        #             Get {{
        #                 Reaction {{
        #                     feedbackText
        #                     messageId
        #                 }}
        #             }}
        #         }}
        #         """

        #         # Execute the queries for Cache and Reaction
        #         cache_response = SimpleWeaviateQueryEngine.client.query.raw(cache_query)
        #         reaction_response = SimpleWeaviateQueryEngine.client.query.raw(reaction_query)

        #         # Extract Cache and Reaction data
        #         cache_data = cache_response.get("data", {}).get("Get", {}).get("Cache", [])
        #         reaction_data = (reaction_response.get("data", {})
        #                                         .get("Get", {})
        #                                         .get("Reaction", [])
        #                                         )
        #         # Find the system response and feedback text based on messageId
        #         if cache_data:
        #             system_response = next(
        #                 (
        #                     item["system"] 
        #                     for item in cache_data 
        #                     if item["messageId"] == _messageId
        #                 ), 
        #                 None
        #                 )
        #             sql = next(
        #                 (
        #                     item["sql"] 
        #                     for item in cache_data 
        #                     if item["messageId"] == _messageId
        #                 ), 
        #                 None
        #                 )
        #         else:
        #             system_response = ""
        #             sql = ""
                    
        #         if reaction_data:
        #             feedback_text = next(
        #                 (
        #                     item["feedbackText"] 
        #                     for item in reaction_data 
        #                     if item["messageId"] == _messageId
        #                 ), 
        #                 None
        #                 )
        #         else:
        #             feedback_text = ""
                    
        #         # Return both system response and feedback text
        #         if system_response or feedback_text or sql:
        #             return system_response, feedback_text, sql
        #         else:
        #             return None, None, None

        #     except Exception as e:
        #         logger.exception(f"Failed to fetch system and feedback text: {str(e)}")
        #         return None, None, None
        
        _system_output, _feedbackText, sql = await AuthDatabaseService.fetch_system_and_feedback_text(_messageId)
        
        # check semantic cache
        # results = self.retrieve_semantic_cache(question)
        
        # def cache_results(results) -> str:
        #     formatted_string = ""
        #     if results:
        #         for i, d in enumerate(results):
        #             previous_question = d["query"]
        #             previous_answer = d["sql"]
                    
        #             # Concatenating into a formatted string
        #             formatted_string += f'question: "{previous_question}"\n'
        #             formatted_string += f'sql query: "{previous_answer}"\n\n'
            
        #     return formatted_string.strip()  # Remove the trailing newline
    
        # cache = cache_results(results)
        # logger.debug(f'CACHE:\n{cache_results(results)}')
        
        (_, 
         _, 
         _, 
         regenerator_sql_chain, 
         regenerate_sql_sql_chain) = await LangchainAIService.get_chains(settings=settings)
        
        # Generate the SQL query from the question
        query = await regenerate_sql_sql_chain.ainvoke({
                                    "question": question,
                                    "sql": sql,
                                    "_feedbackText": _feedbackText
                                 })
        # Run the generated SQL query with retries
        try:
            response, query = await LangchainAIService.run_query_with_retries(query=query, 
                                                                              question=question, 
                                                                              max_retries=7, 
                                                                              settings=settings)
            logger.debug(f"\nSQL Response: {response}\nNew Query: {query}")
                        
            if response and isinstance(response, str):
                response = await LangchainAIService.truncate_response(response)
            else:
                response = await LangchainAIService.truncate_response(str(response))
                
            # retrive memory cache
            memory = await AuthDatabaseService.retrieve_cache_history(_userId, _sessionId)
            logger.debug(f"Memory cache: {memory}")
            def cache_results_with_roles(memory, question) -> str:
                formatted_string = ""
                
                if memory:
                    for i, d in enumerate(memory):
                        previous_question = d["query"]
                        previous_answer = d["system"]

                        # Concatenating into a formatted string with roles
                        formatted_string += f'role: user\ncontent: "{previous_question}"\n\n'
                        formatted_string += f'role: assistant\ncontent: "{previous_answer}"\n\n'
                
                # Adding the latest user question at the end
                formatted_string += f'role: user\ncontent: "{question}"\n'
                
                return formatted_string.strip()  # Remove the trailing newline
            
            logger.debug(f'MEMORY:\n{cache_results_with_roles(memory, question)}')
                    
            system_msg = await regenerator_sql_chain.ainvoke({
                                                        "_system_output": _system_output,
                                                        "_feedbackText": _feedbackText,
                                                        "question": question, 
                                                        "response": response, 
                                                        "username": userId,
                                                        "query": query,
                                                        "memory": cache_results_with_roles(
                                                            memory, 
                                                            question
                                                            )
                                                      })
            # system_msg = LangchainAIService.remove_symbols_from_response(system_msg)
            
            logger.debug(f'Calling OpenAI API with model={settings.MODEL}\n\n' \
                         f'query={question}\nanswer={system_msg}')
            logger.info("User Question Executed!")
            
            await AuthDatabaseService.add_semantic_cache(
                                    question, 
                                    system_msg, 
                                    _userId, 
                                    mI, 
                                    _sessionId, 
                                    _timestamp, 
                                    query
                                    )
            return (system_msg, _userId, mI, _sessionId, _timestamp, _system_output, _feedbackText)
        except Exception as e:
            logger.error(f"Error getting response: {e}")
            return None, None, None, None, None, None, None


# Useful functions
def get_session_params(query: str):
    # create messege_id
    def generate_message_id(timestamp: str):
        # Combine user query with a timestamp to ensure uniqueness
        unique_string = f"{query}_{timestamp}"

        # Calculate a hash of the unique string
        message_id = hashlib.sha256(unique_string.encode()).hexdigest()
        return message_id
    
    # create time_stamp
    def generate_time_stamp():
        datetime_now = datetime.now()
        # rfcc = datetime_now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        rfcc = datetime_now.strftime("%Y-%m-%d %H:%M:%S")
        return rfcc

    # Generate a unique message ID
    _timestamp = generate_time_stamp()
    _messageId = generate_message_id(_timestamp)
    logger.info("Message id and timestamps are generated")
    return _messageId, _timestamp
