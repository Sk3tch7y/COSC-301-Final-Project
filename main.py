from pathlib import Path

from data_cleaning import clean_data
from data_download import download_file
from data_filtering import filter_data
from eda import run_eda
from project_setup import setup_project


def main():
    print("Starting project setup")
    if not setup_project():
        print("Project setup failed")
        return
    print("Attempting data download")
    download_file()
    if (
        Path("data/cards_data.csv").is_file()
        and Path("data/transactions_data.csv").is_file()
        and Path("data/users_data.csv").is_file()
    ):
        print("Download and extraction complete.")
    else:
        print("Download failed")
        return
    print("cleaning data and updating database")
    clean_data()
    print("running EDA")
    run_eda()


main()
