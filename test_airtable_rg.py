import csv
import pytest

from config import AIRTABLE_BASE
from constants import CSV_HEADERS
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


def test_csv_file():
    animals = [
        {
            "id": "1",
            "fields": {
                "Status": "Adopted",
            },
        },
        {
            "id": "2",
            "fields": {
                "Status": "Published - ",
                "Pet Species": "Alien",
            },
        },
        {
            "id": "3",
            "fields": {
                "Status": "Published",
                "Pet Species": "Dog",
                "Pet Name": "Fido",
                "Sex": "Male",
                "Pet Age": "Young",
                "Pet Size": "Large",
                "Coat Length": "Short",
                "Mixed Breed": "Unknown",
                "Breed - Dog": "Beagle",
                "Color - Dog": "Tan",
                "Okay with Dogs": "Yes",
                "Okay with Cats": "No",
                "Okay with Kids": "Unknown",
                "Housetrained": "Yes",
                "Altered": "Unknown",
                "Up-to-date on Shots etc": "No",
                "Public Description": "test dog notes\n\r",
                "Pictures": [
                    {
                        "id": "attlWavzYDzYGGBwb",
                        "width": 171,
                        "height": 180,
                        "url": "https://dog.jpg",
                    },
                ],
            },
        },
        {
            "id": "4",
            "fields": {
                "Status": "x Published",
                "Pet Species": "Cat",
                "Pet Name": "Freya",
                "Sex": "Female",
                "Pet Age": "Adult",
                "Special Needs": "Yes",
                "Pet Size": "Small",
                "Coat Length": "Long",
                "Mixed Breed": "No",
                "Breed - Cat": "Calico",
                "Color - Cat": "White",
                "Okay with Dogs": "Unknown",
                "Okay with Cats": "Yes",
                "Okay with Kids": "No",
                "Declawed": "Yes",
                "Housetrained": "No",
                "Altered": "No",
                "Up-to-date on Shots etc": "Unknown",
                "Pictures": [
                    {
                        "url": "https://cat1.jpg",
                    },
                    {
                        "url": "https://cat2.jpg",
                    },
                    {
                        "url": "https://cat3.jpg",
                    },
                    {
                        "url": "https://cat4.jpg",
                    },
                ],
            },
        },
    ]

    filename = create_csv_file(animals)

    with open(filename, "r") as f:
        reader = csv.reader(f)
        header = reader.__next__()

        assert header == CSV_HEADERS

        for row in reader:
            assert row[0] in ("3", "4")

            if row[0] == "3":
                assert row == [
                    "3", "Available", "", "", "Fido",
                    "Dog", "Beagle", "", "Yes", "Male",
                    "Yes", "No", "", "", "Yes",
                    "Young", "", "", "Large", "No",
                    "Tan", "", "Short", "Yes",
                    "test dog notes<br /><br />",
                    "No", "", "", "https://dog.jpg",
                    "", "", "", "",
                ]

            else:
                assert row == [
                    "4", "Available", "", "", "Freya",
                    "Cat", "Calico", "", "No", "Female",
                    "", "Yes", "No", "Yes", "No",
                    "Adult", "Yes", "No", "Small", "",
                    "White", "", "Long", "Yes", "",
                    "No", "", "",
                    "https://cat1.jpg",
                    "https://cat2.jpg",
                    "https://cat3.jpg",
                    "https://cat4.jpg",
                    "",
                ]
