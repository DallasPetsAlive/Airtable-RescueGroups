import csv
import logging
from os import name
import requests
from config import AIRTABLE_BASE, AIRTABLE_API_KEY
from constants import CSV_HEADERS


logger = logging.getLogger()
logger.setLevel(logging.INFO)


# AWS Lambda entry point
def lambda_handler(event, context):
    # get the pets from Airtable
    airtable_pets = get_airtable_pets()

    # create CSV file of available pets
    csv_file = create_csv_file(airtable_pets)

    # upload CSV file to rescuegroups.org
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
    filename = "newdigs.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)

        # headers from rescuegroups.org sample file
        writer.writerow(CSV_HEADERS)

        # figure out where the columns we have data for reside
        id_index = CSV_HEADERS.index("externalID")
        name_index = CSV_HEADERS.index("name")
        status_index = CSV_HEADERS.index("status")
        species_index = CSV_HEADERS.index("type")
        breed_index = CSV_HEADERS.index("priBreed")
        mix_index = CSV_HEADERS.index("mix")
        sex_index = CSV_HEADERS.index("sex")
        ok_dog_index = CSV_HEADERS.index("okwithdogs")
        ok_cat_index = CSV_HEADERS.index("okwithcats")
        ok_kid_index = CSV_HEADERS.index("okwithkids")
        declawed_index = CSV_HEADERS.index("declawed")
        house_index = CSV_HEADERS.index("housebroken")
        age_index = CSV_HEADERS.index("age")
        needs_index = CSV_HEADERS.index("specialNeeds")
        fix_index = CSV_HEADERS.index("altered")
        size_index = CSV_HEADERS.index("size")
        utd_index = CSV_HEADERS.index("uptodate")
        color_index = CSV_HEADERS.index("color")
        length_index = CSV_HEADERS.index("coatLength")
        courtesy_index = CSV_HEADERS.index("courtesy")
        dsc_index = CSV_HEADERS.index("dsc")
        found_index = CSV_HEADERS.index("found")
        photo1_index = CSV_HEADERS.index("photo1")
        photo2_index = CSV_HEADERS.index("photo2")
        photo3_index = CSV_HEADERS.index("photo3")
        photo4_index = CSV_HEADERS.index("photo4")

        for pet in airtable_pets:
            # if pet isn't available or isn't a supported species, bail
            status = pet["fields"].get("Status", "")
            if "Published" not in status:
                continue

            species = pet["fields"].get("Pet Species", "")
            if species not in ("Dog", "Cat"):
                continue

            pet_row = [None for _ in range(len(CSV_HEADERS))]

            pet_row[id_index] = pet["id"]
            pet_row[name_index] = pet["fields"].get("Pet Name")
            pet_row[status_index] = "Available"
            pet_row[species_index] = species
            pet_row[sex_index] = pet["fields"].get("Sex")
            pet_row[age_index] = pet["fields"].get("Pet Age")
            pet_row[needs_index] = pet["fields"].get("Special Needs")
            pet_row[size_index] = pet["fields"].get("Pet Size")
            pet_row[length_index] = pet["fields"].get("Coat Length")
            pet_row[courtesy_index] = "Yes"
            pet_row[found_index] = "No"

            if pet["fields"].get("Mixed Breed") == "No":
                pet_row[mix_index] = "No"
            else:
                pet_row[mix_index] = "Yes"

            if species == "Dog":
                pet_row[breed_index] = pet["fields"].get("Breed - Dog")
                pet_row[color_index] = pet["fields"].get("Color - Dog")
            elif species == "Cat":
                pet_row[breed_index] = pet["fields"].get("Breed - Cat")
                pet_row[color_index] = pet["fields"].get("Color - Cat")

            pet_row[ok_dog_index] = pet["fields"].get("Okay with Dogs")
            pet_row[ok_cat_index] = pet["fields"].get("Okay with Cats")
            pet_row[ok_kid_index] = pet["fields"].get("Okay with Kids")

            if pet_row[ok_dog_index] == "Unknown":
                pet_row[ok_dog_index] = ""
            if pet_row[ok_cat_index] == "Unknown":
                pet_row[ok_cat_index] = ""
            if pet_row[ok_kid_index] == "Unknown":
                pet_row[ok_kid_index] = ""

            pet_row[declawed_index] = pet["fields"].get("Declawed")
            if pet_row[declawed_index] == "Unknown":
                pet_row[declawed_index] = ""

            pet_row[house_index] = pet["fields"].get("Housetrained")
            if pet_row[house_index] == "Unknown":
                pet_row[house_index] = ""

            pet_row[fix_index] = pet["fields"].get("Altered")
            if pet_row[fix_index] == "Unknown":
                pet_row[fix_index] = ""

            pet_row[utd_index] = pet["fields"].get("Up-to-date on Shots etc")
            if pet_row[utd_index] == "Unknown":
                pet_row[utd_index] = ""

            description = pet["fields"].get("Public Description", "")
            description = description.replace("\r", "<br />")
            description = description.replace("\n", "<br />")
            pet_row[dsc_index] = description

            pictures = []
            for picture in pet["fields"].get("Pictures", []):
                pictures.append(picture["url"])

            if pictures:
                pet_row[photo1_index] = pictures.pop(0)
            if pictures:
                pet_row[photo2_index] = pictures.pop(0)
            if pictures:
                pet_row[photo3_index] = pictures.pop(0)
            if pictures:
                pet_row[photo4_index] = pictures.pop(0)

            writer.writerow(pet_row)

        return filename


def upload_to_rescue_groups(csv_file):
    pass


lambda_handler(None, None)
