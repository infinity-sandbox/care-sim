from typing import Optional
import mysql.connector
from app.scripts.com.arcturustech import transaction_pb2
from app.services.database_service import MySQLDatabaseService
from app.sql.main import SqlQuery
from app.core.config import logger_settings, Settings
logger = logger_settings.get_logger(__name__)
import mysql.connector
import json
import aiomysql
from fastapi import APIRouter, HTTPException, Header, status, Depends
from fastapi import APIRouter, Depends, Query
from app.services.database_service import MySQLDatabaseService

async def fetch_and_decode_trace(query, settings: Optional[Settings] = None):
    """
    Fetches the trace from the database and decodes it using the protobuf.

    Args:
        transaction_id (str): The transaction ID to fetch and decode.

    Returns:
        The decoded protobuf object or None if not found.
    """    
    try:
        connection = await MySQLDatabaseService.connection(settings)
        async with connection.cursor() as cursor:
            await cursor.execute(query)
            row = await cursor.fetchone()
            logger.debug(f"\n\n row: {row} \n\n")
            
            if not row:
                logger.debug("No transaction found with the given ID.")
                return None
            
            blob_data = row[0]
            
            transaction_proto = transaction_pb2.TransactionProto()
            transaction_proto.ParseFromString(blob_data)
            return transaction_proto
            
    except Exception as e:
        logger.error(f"An error occurred while fetching and decoding the trace: {e}")
        return None
    finally:
        connection.close()
                   
def find_highest_time_children(context):
    """
    Recursively finds the child with the highest time in the given context and its children.

    Args:
        context: A protobuf context object containing children.

    Returns:
        dict: The child with the highest time and its details.
    """
    if not context.children:
        return None  # No children to process

    # Find the child with the maximum time
    highest_time_child = max(context.children, key=lambda child: child.time)

    # Recursively process its children
    if highest_time_child.children:
        highest_time_child_info = find_highest_time_children(highest_time_child)
        if highest_time_child_info:
            return {
                "name": highest_time_child.name,
                "time": highest_time_child.time,
                "children": [highest_time_child_info],
            }
    return {
        "name": highest_time_child.name,
        "time": highest_time_child.time,
        "children": [],
    }

def gather_highest_time_children(transaction_proto) -> dict:
    """
    Processes the transaction_proto to find and gather the highest time children
    for each context into a JSON-compatible structure.

    Args:
        transaction_proto: The decoded transaction protobuf object.

    Returns:
        dict: A JSON-compatible structure containing the highest time children for each context.
    """
    highest_time_children = {}

    for context in transaction_proto.contexts:
        highest_child = find_highest_time_children(context)
        if highest_child:
            highest_time_children[context.name] = highest_child

    return highest_time_children

def output_to_json(data):
    """
    Converts the given data to a JSON string.

    Args:
        data: The data to convert to JSON.

    Returns:
        str: The JSON string.
    """
    return json.dumps(data, indent=2)

def process_nested_dict(data, url_key="URL", name_key="name", time_key="time", children_key="children"):
    """
    Processes a nested dictionary and generates a string in the required format.

    Args:
        data (dict): The nested dictionary to process.
        url_key (str): Key representing the URL in the dictionary.
        name_key (str): Key representing the name in the dictionary.
        time_key (str): Key representing the time in the dictionary.
        children_key (str): Key representing the children in the dictionary.

    Returns:
        str: A formatted string representing the delays and their causes.
    """
    result = []

    # Helper function for recursive processing
    def traverse(node, depth=0):
        # Process the current node
        if name_key in node and time_key in node:
            result.append(
                f'{"Sub-method/SQL" if depth > 0 else "Main method:"}\n'
                f'{name_key}: "{node[name_key]}", \n'
                f'Time it took (ms): {node[time_key] / 1_000_000:.2f}'
            )

        # Recursively process children
        if children_key in node and node[children_key]:
            for child in node[children_key]:
                traverse(child, depth + 1)
        else:
            # Handle the last child case
            if depth > 0:
                result.append(
                    "The root cause of the general delays mentioned above is:\n"
                    f'{name_key}: "{node[name_key]}", \n'
                    f'Time it took (ms): {node[time_key] / 1_000_000:.2f}'
                )

    # Start processing
    for key, value in data.items():
        result.append(f"Issue Transaction: {key}")
        traverse(value)

    return "\n\n".join(result)

async def main(query, settings: Optional[Settings] = None):
        # Fetch and decode the transaction
    transaction_proto = await fetch_and_decode_trace(query, settings)

    if transaction_proto:
        # Gather the highest time children in a JSON-compatible structure
        highest_time_children = gather_highest_time_children(transaction_proto)
        logger.debug(f"dict object: \n\n{highest_time_children}")
        data = process_nested_dict(highest_time_children)
        logger.debug(f"cause data: \n\n {data}")
        # Output the data as a JSON string
        # json_output = output_to_json(highest_time_children)
        # logger.debug(json_output)
        
        # data = json.loads(json_output)
        # logger.debug(data["/JPetStore/shop/viewProduct.shtml"]["time"])
        return data
    else:
        return "No causes of slowness were detected at this time."
    
        