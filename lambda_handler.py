import csv
import logging
import requests
from config import AIRTABLE_BASE, AIRTABLE_API_KEY


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    airtable_pets = get_airtable_pets()

    csv_file = create_csv_file(airtable_pets)

    upload_to_rescue_groups(csv_file)

    return {}


def get_airtable_pets():
    # get new digs pets from airtable
    url = "https://api.airtable.com/v0/" + AIRTABLE_BASE + "/Pets"
    headers = {"Authorization": "Bearer " + AIRTABLE_API_KEY}

    response = requests.get(url, headers=headers)
    if(response.status_code != requests.codes.ok):
        logger.error("Airtable response: ")
        logger.error(response)
        logger.error("URL: " + url)
        logger.error("Headers: " + str(headers))
        raise

    airtable_response = response.json()

    return airtable_response["records"]


def create_csv_file(airtable_pets):
    with open("newdigs.csv", 'w') as f:
        writer = csv.writer(f)


def upload_to_rescue_groups(csv_file):
    pass


lambda_handler(None, None)
