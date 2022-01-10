import pytest
import requests

from config import AIRTABLE_BASE
from lambda_handler import (
    lambda_handler,
    get_airtable_pets,
    create_csv_file,
    upload_to_rescue_groups,
)


def test_get_pets(requests_mock):
    records = {
        "records": [{"a thing": "a pet"}],
    }
    url = "https://api.airtable.com/v0/" + AIRTABLE_BASE + "/Pets"
    requests_mock.get(url, json=records, status_code=200)

    pets = get_airtable_pets()
    assert len(pets) == 1
    assert pets[0]["a thing"] == "a pet"


def test_get_pets_error(requests_mock):
    records = {
        "records": [{"a thing": "a pet"}],
    }
    url = "https://api.airtable.com/v0/" + AIRTABLE_BASE + "/Pets"
    requests_mock.get(url, json=records, status_code=400)

    with pytest.raises(Exception):
        get_airtable_pets()


def test_get_pets_bad_data(requests_mock):
    records = {
        "this is wrong": "nope",
    }
    url = "https://api.airtable.com/v0/" + AIRTABLE_BASE + "/Pets"
    requests_mock.get(url, json=records, status_code=200)

    with pytest.raises(KeyError):
        get_airtable_pets()
