import os, sys
import re
from datetime import datetime
from typing import Optional
from langchain_community.utilities import SQLDatabase
from app.services.openai_service import OpenAIService
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from fastapi import HTTPException
from app.core.config import logger_settings, Settings
from app.prompts.main import Prompt
logger = logger_settings.get_logger(__name__)
import tiktoken
from app.services.database_service import (MySQLDatabaseService, 
                                           MariaDbDatabaseService, 
                                           MSSQLDatabaseService,
                                           OracleDatabaseService)

class LangchainAIService(OpenAIService):
    @staticmethod
    async def connection(settings: Optional[Settings] = None):
        if settings.DB_MS == 'mysql':
            logger.info(f"{settings.DB_MS} DB detected!")
            return await MySQLDatabaseService.connection(settings=settings)
        elif settings.DB_MS == 'mariadb':
            logger.info(f"{settings.DB_MS} DB detected!")
            return await MariaDbDatabaseService.connection(settings=settings)
        elif settings.DB_MS == 'mssql':
            logger.info(f"{settings.DB_MS} DB detected!")
            return await MSSQLDatabaseService.connection(settings=settings)
        elif settings.DB_MS == 'oracle':
            logger.info(f"{settings.DB_MS} DB detected!")
            return await OracleDatabaseService.connection(settings=settings)
        else:
            raise HTTPException(
                    status_code=404, 
                    detail=f"Database not found!"
                )
            
    @staticmethod
    async def get_schema(settings: Optional[Settings] = None):
        if settings.DB_MS == 'mysql':
            schema = await MySQLDatabaseService.get_schema(settings=settings)
        elif settings.DB_MS == 'mariadb':
            schema = await MariaDbDatabaseService.get_schema(settings=settings)
        elif settings.DB_MS == 'mssql':
            schema = await MSSQLDatabaseService.get_schema(settings=settings)
        elif settings.DB_MS == 'oracle':
            schema = await OracleDatabaseService.get_schema(settings=settings)
        else: 
            raise HTTPException(
                    status_code=404, 
                    detail=f"Database not found!"
                )
        logger.debug(f"Schema: \n{schema}")
        schema = await LangchainAIService.truncate_response(schema, 1000)
        
        return schema
    
    # @staticmethod
    # async def problem_detection():
    #     logger.info("Detecting problems...")
    #     from app.services.multivariate_timeseries import MultivariateTimeSeries
    #     df = MultivariateTimeSeries.connect_db()
    #     # Sort the DataFrame by the 'rl' column in descending order
    #     sorted_df = df.sort_values(by='rl', ascending=False)
        
    #     # Get the last 3 rows of the sorted DataFrame
    #     last_three_rows = sorted_df.head(3)
    #     issues = await MultivariateTimeSeries.send_signal(last_three_rows)
    #     logger.info(f"Issues detected: {issues}")
    #     return issues
    
    # @staticmethod
    # async def if_anomaly():
    #     # Check if the dictionary itself is empty
    #     data_dict = await LangchainAIService.problem_detection()
    #     if not data_dict:
    #         logger.debug("The dictionary is empty.")
    #         return False, data_dict

    #     # Check if all the lists inside the dictionary are empty
    #     all_lists_empty = all(not value for value in data_dict.values())

    #     if all_lists_empty:
    #         logger.warning("All lists in the dictionary are empty. (no issues detected)")
    #         return False, data_dict
    #     else:
    #         logger.warning("The dictionary is not empty and not all lists are empty. " \
    #                        "(Problem detected)")
    #         return True, data_dict
        
    # @staticmethod
    # async def if_cause():
    #     # Check if the dictionary itself is empty
    #     data_dict = await LangchainAIService.problem_detection()
    #     if not data_dict:
    #         logger.debug("The dictionary is empty.")
    #         return False, data_dict

    #     # Check if all the lists inside the dictionary are empty
    #     all_lists_empty = all(not value for value in data_dict.values())

    #     if all_lists_empty:
    #         logger.warning("All lists in the dictionary are empty. (no issues detected)")
    #         return False, data_dict
    #     else:
    #         logger.warning("The dictionary is not empty and not all lists are empty. " \
    #                        "(Problem detected)")
    #         return True, data_dict
        
    @staticmethod
    async def get_prompts_chain(query_template, error_query_template, response_template, 
                          regenerator_template, regenerate_sql_template, settings: Optional[Settings] = None):
        logger.debug('Getting prompts chain')
        llm = ChatOpenAI(openai_api_key=logger_settings.OPENAI_API_KEY)
        
        query_prompt = ChatPromptTemplate.from_template(query_template)
        error_prompt = ChatPromptTemplate.from_template(error_query_template)
        response_prompt = ChatPromptTemplate.from_template(response_template)
        regenerator_prompt = ChatPromptTemplate.from_template(regenerator_template)
        regenerate_sql_prompt = ChatPromptTemplate.from_template(regenerate_sql_template)
        
        logger.debug('Reading templates...')
        
        # Create the SQL chain
        schema = await LangchainAIService.get_schema(settings=settings)
        logger.debug('Getting prompts chain...')
        
        sql_chain = (
            RunnablePassthrough.assign(schema=lambda _: schema)
            | query_prompt
            | llm.bind(stop=["\nSQLResult:"])
            | StrOutputParser()
        )

        # Create the SQL chain
        error_sql_chain = (
            RunnablePassthrough.assign(schema=lambda _: schema)
            | error_prompt
            | llm.bind(stop=["\nSQLResult:"])
            | StrOutputParser()
        )

        # Create the SQL chain
        response_sql_chain = (
            RunnablePassthrough.assign(schema=lambda _: schema)
            | response_prompt
            | llm.bind(stop=["\nSQLResult:"])
            | StrOutputParser()
        )
        
        # Create the SQL chain
        regenerator_sql_chain = (
            RunnablePassthrough.assign(schema=lambda _: schema)
            | regenerator_prompt
            | llm.bind(stop=["\nSQLResult:"])
            | StrOutputParser()
        )
        
        # Create the SQL chain
        regenerator_sql_sql_chain = (
            RunnablePassthrough.assign(schema=lambda _: schema)
            | regenerate_sql_prompt
            | llm.bind(stop=["\nSQLResult:"])
            | StrOutputParser()
        )
        
        return (sql_chain, error_sql_chain, response_sql_chain, 
                regenerator_sql_chain, regenerator_sql_sql_chain)
        
    @staticmethod
    async def get_chains(settings: Optional[Settings] = None):
        query_template = await Prompt.read_prompt('query_template')
        response_template = await Prompt.read_prompt('response_template')
        error_query_template = await Prompt.read_prompt('error_query_template')
        regenerate_template = await Prompt.read_prompt('regenerator_template')
        regenerate_sql_template = await Prompt.read_prompt('regenerator_sql_template')
        #
        (sql_chain, 
         error_sql_chain, 
         response_sql_chain,
         regenerator_sql_chain,
         regenerate_sql_sql_chain) = await LangchainAIService.get_prompts_chain(
                                        query_template=query_template,
                                        error_query_template=error_query_template,
                                        response_template=response_template,
                                        regenerator_template=regenerate_template,
                                        regenerate_sql_template=regenerate_sql_template,
                                        settings=settings
                                    )
        #
        return (sql_chain, 
                error_sql_chain, 
                response_sql_chain, 
                regenerator_sql_chain, 
                regenerate_sql_sql_chain)

    @staticmethod
    async def run_query_with_retries(query, question, max_retries = 7, settings: Optional[Settings] = None):
        attempt = 0
        logger.debug('running query with retries...')
        while attempt < max_retries:
            try:
                if settings.DB_MS == 'mysql':
                    response = await MySQLDatabaseService.run_query(query, settings=settings)
                elif settings.DB_MS == 'mariadb':
                    response = await MariaDbDatabaseService.run_query(query, settings=settings)
                elif settings.DB_MS == 'mssql':
                    response = await MSSQLDatabaseService.run_query(query, settings=settings)
                elif settings.DB_MS == 'oracle':
                    response = await OracleDatabaseService.run_query(query, settings=settings)
                else:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Database not found!"
                    )
                    
                return response, query # Exit the loop if the query succeeds
            except Exception as e:
                logger.error(f"Error running query: {e}")
    
                (_, 
                 error_sql_chain, 
                 _, 
                 _, 
                 _) = await LangchainAIService.get_chains(settings=settings)
                
                if attempt >= max_retries - 1:
                    raise  # Raise the exception if the maximum retries have been reached
                attempt += 1
                if attempt == max_retries - 2:
                    logger.error(f"Maximum retries reached. Exiting...")
                    return "None", "None"
                # Generate a new query based on the error
                query = await error_sql_chain.ainvoke({"question": question, 
                                                "response": query, 
                                                "error": str(e)})
                logger.warning(f"Retrying query... Attempt {attempt + 1} of {max_retries}")
                
    @staticmethod
    async def truncate_response(response: str, max_tokens: int = 9000) -> str:
        # Initialize the tokenizer
        tokenizer = tiktoken.get_encoding("cl100k_base")

        # Tokenize the response
        tokens = tokenizer.encode(response)

        # Truncate tokens if necessary
        if len(tokens) > max_tokens:
            logger.warning(f"Truncating response from {len(tokens)} tokens to {max_tokens} tokens.")
            tokens = tokens[:max_tokens]
            # Decode tokens back to a string
            response = tokenizer.decode(tokens)
        return response
    
    @staticmethod
    def remove_symbols_from_response(response: str) -> str:
        # Define currency symbols to be replaced
        currency_symbols = r'[$€£¥₹¢₩₽]'
        # Check if any currency symbol exists in the input string
        if not re.search(currency_symbols, response):
            logger.debug("No currency symbol inside the response.")
            return response
        # Replace currency symbols before numbers, ensuring a space before 'currency'
        result = re.sub(rf'({currency_symbols})(\d[\d,]*)', r'\2 currency', response)
        # Replace standalone currency symbols with 'currency'
        result = re.sub(rf'\b{currency_symbols}\b', 'currency', result)
        # Ensure a space between numbers and 'currency'
        result = re.sub(r'(\d)(currency)', r'\1 \2', result)
        # Move 'currency' before punctuation if present
        result = re.sub(r'(currency)\s*([.,!?])', r'\1\2', result)

        return result
    
    # @staticmethod
    # async def full_chain(question: str, username: str, settings: Optional[Settings] = None) -> str:
    #     logger.debug('calling full chain...')
    #     (sql_chain, 
    #      _, 
    #      response_sql_chain, 
    #      _, 
    #      _) = await LangchainAIService.get_chains(settings=settings)
        
    #     # Generate the SQL query from the question
    #     query = await sql_chain.ainvoke({"question": question})
        
    #     # Run the generated SQL query with retries
    #     try:
    #         response, query = await LangchainAIService.run_query_with_retries(query, question, 7, settings=settings)
    #         logger.info(f"SQL response: {response}\nNew Query: {query}")

    #         response = LangchainAIService.truncate_response(response)
    #         result = response_sql_chain.invoke({"question": question, "query": query, 
    #                                             "response": response, "username": username})
    #         logger.debug(f"Natural Language Response: {result}")
    #         return result
    #     # Generate the natural language response using the response_prompt
    #     except Exception as e:
    #         logger.error(f"Error getting response: {e}")
    #         return f"Error getting response: {e}"
            
