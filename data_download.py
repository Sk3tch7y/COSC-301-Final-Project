import io
import zipfile
from pathlib import Path

import requests


def download_file():
    if (
        Path("data/cards_data.csv").is_file()
        and Path("data/transactions_data.csv").is_file()
        and Path("data/users_data.csv").is_file()
    ):
        return
    # URL of the data
    url = "https://www.kaggle.com/api/v1/datasets/download/computingvictor/transactions-fraud-datasets"

    # Download the zip file
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall("data")
    except:
        print("failed to download files")
    # Unzip the file in memory
