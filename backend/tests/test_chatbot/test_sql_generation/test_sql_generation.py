import pytest
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from datetime import datetime
import langchain_core
import pandas as pd
from app.services.langchain_service import LangchainAIService
from app.services.openai_service import OpenAIService
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
import os, sys
from app.core.config import settings
logger = settings.get_logger(__name__)
import tiktoken

@pytest.fixture(scope="module")
def test_db():
    return LangchainAIService.connection()


class TestRAGSQLGeneration:
    @pytest.fixture(autouse=True)
    def setup_class(self, test_db):
        # Set up the necessary chains
        self.sql_chain, self.error_sql_chain, self.response_sql_chain = LangchainAIService.get_chains()
        self.db = test_db

    def generate_sql(self, question):
        # Generate SQL query from the question using Langchain
        return self.sql_chain.invoke({"question": question})

    def run_query_with_retries(self, query, question):
        # Run the generated SQL query with retry mechanism
        return LangchainAIService.run_query_with_retries(query, question)

    # Test Case 1: Simple COUNT Query
    def test_sql_count_query_generation(self):
        question = "How many users faced downtime in the last week?"
        query = self.generate_sql(question)

        # Run the query with retries and check if result is as expected
        response, query = self.run_query_with_retries(query, question)
        expected_query = "SELECT COUNT(*) AS total_users FROM server_details WHERE date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);"
        assert query.strip() == expected_query.strip(), f"Generated query does not match expected.\nGenerated: \n{query}\n\nExpected: \n{expected_query}"
        
    # Test Case 7: Response Quality
    def test_response_quality(self):
        question = "What is the average response time for business transactions?"
        query = self.generate_sql(question)

        # Run the query with retries
        response, query = self.run_query_with_retries(query, question)

        # Generate the natural language response
        natural_language_response = self.response_sql_chain.invoke({
            "question": question,
            "query": query,
            "response": response,
            "username": "test_user"
        })

        expected_response = "Hi test_user, the average response time for business transactions is 350 milliseconds."
        assert natural_language_response.strip() == expected_response.strip(), f"Response does not match expected.\nGenerated: {natural_language_response}\nExpected: {expected_response}"


    # Test Case 2: Average Response Time
    def test_sql_average_query_generation(self):
        question = "What is the average response time for business transactions?"
        query = self.generate_sql(question)

        # Run the query with retries and check if result is as expected
        response, query = self.run_query_with_retries(query, question)
        expected_query = "SELECT AVG(response_time) FROM business_txn_avg;"
        query = " ".join(query.strip().split()).lower()
        expected_query = " ".join(expected_query.strip().split()).lower()
        assert query.strip() == expected_query.strip(), f"Generated query does not match expected.\nGenerated: {query}\nExpected: {expected_query}"

    # Test Case 3: Handling Missing Data
    def test_sql_no_data_found(self):
        question = "How many transactions failed in the last year?"
        query = self.generate_sql(question)

        # Expected SQL to be generated for the question
        expected_query = "SELECT COUNT(*) FROM txn WHERE status = 'failed' AND date >= DATE('now', '-1 year');"
        assert query.strip() == expected_query.strip(), f"Generated query does not match expected.\nGenerated: {query}\nExpected: {expected_query}"

        # Run the query and assert that the result is handled correctly
        response, _ = self.run_query_with_retries(query, question)
        assert response == 0, f"Expected result to be 0 for missing data, but got {response}"

    # Test Case 4: Edge Case for Invalid Inputs
    def test_sql_invalid_column(self):
        question = "What is the value of an invalid column?"
        query = self.generate_sql(question)

        # Expecting an error when running the query
        with pytest.raises(Exception):
            self.db.run(query)

    # Test Case 5: SQL Injection Prevention
    def test_sql_injection(self):
        question = "How many users; DROP TABLE server_details; --"
        query = self.generate_sql(question)

        # Check that query is sanitized to prevent SQL injection
        assert ";" not in query, f"SQL query should not contain semicolons.\nGenerated: {query}"

        # Running the query should raise an error (due to incomplete query or malformed data)
        with pytest.raises(Exception):
            self.db.run(query)

    # Test Case 6: Date Calculation for Recent Week
    def test_sql_recent_week(self):
        question = "Show downtime data for the past week."
        query = self.generate_sql(question)

        # Expected SQL to be generated
        expected_query = "SELECT * FROM server_details WHERE date >= DATE('now', '-7 days');"
        assert query.strip() == expected_query.strip(), f"Generated query does not match expected.\nGenerated: {query}\nExpected: {expected_query}"

    # Test Case 8: Handling No Results Found Gracefully
    def test_no_results_found(self):
        question = "How many servers were down yesterday?"
        query = self.generate_sql(question)

        # Expected SQL to be generated
        expected_query = "SELECT COUNT(*) FROM server_details WHERE downtime > 0 AND date = DATE('now', '-1 day');"
        assert query.strip() == expected_query.strip(), f"Generated query does not match expected.\nGenerated: {query}\nExpected: {expected_query}"

        # Run the query with retries
        response, query = self.run_query_with_retries(query, question)

        # Expected result is 0 because no downtime data for 'yesterday' in test_db
        assert response == 0, f"Expected no servers down but got {response}"

        # Generate natural language response
        natural_language_response = self.response_sql_chain.invoke({
            "question": question,
            "query": query,
            "response": response,
            "username": "test_user"
        })

        expected_response = "Hi test_user, it seems that no servers were down yesterday."
        assert natural_language_response.strip() == expected_response.strip(), f"Response does not match expected.\nGenerated: {natural_language_response}\nExpected: {expected_response}"


