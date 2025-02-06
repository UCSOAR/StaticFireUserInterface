from pocketbase import Client
from pocketbase.utils import ClientResponseError
import json


client = Client('http://127.0.0.1:8090')

EXPECTED_SCHEMA_JSON = "DatabaseSchema.json"
token = "None"
collections = "None"

def tokenfunc():
  global token

def updated_collections():
    global collections

def send_telemetry_message_to_database(json_data: str):
    """
    Send a preserialized JSON message to the database.

    Note: The third key in the JSON data is assumed to be the table name
    """
    # Extract the table name from the JSON data
    json_data = (json_data)
    if len(list(json_data.keys())) < 3:
        (f"Received, poorly formed json: {json_data}")
        return

    table_name = list(json_data.keys())[2]

    (f"Adding an entry to the {table_name} table")
    (f"Entry: {json_data[table_name]}")

    # Push the JSON data to PocketBase using the correct schema
    try:
        client.collection(table_name).create(json_data[table_name])
    except Exception:
        (f"Failed to create entry in {table_name}: {json_data}")
        create_table()
        client.collection(table_name).create(json_data[table_name])

def create_table(name, schema):
    #create a collection
    collection_data = {
    "name": name,
    "type": "base",
    "schema": schema
    }
    try:
        client.collections.create(collection_data)
        print(f"Collection '{name}' created with schema: {schema}")
    except ClientResponseError as e:
        print(f"Error creating collection '{name}': {e}")

def delete_table(table_name):
        for record in client.collection(table_name).get_full_list():
            client.collection(table_name).delete(record.id)

        # Update the collection with the new schema.
        collection_to_update = client.collections.get_one(table_name)

        # Delete the existing collection
        client.collections.delete(collection_to_update.id)

def check_table_exists(table_name: str) -> bool:

    admin_email = "kaileykobar@gmail.com"
    admin_password = "CARtank66$"

    if not admin_email or not admin_password:
        print("DB - Admin credentials not found in environment variables.")
        return

    auth_data = client.collection("_superusers").auth_with_password("kaileykobar@gmail.com", "CARtank66$")
    token = auth_data.token
    if token is None:
        print("DB - Failed to authenticate as admin.")
        return
    #try:
    #print(client.collection(table_name))
    #print(client.record_service)


    #table should pass if the table name exists or not. giving parameters it wants to look for (table name)
    try:
        client.collections.get_one(table_name)
        return True
        #client.collection(table_name).create([table_name])
    except ClientResponseError:
        create_table(table_name, {})
        return False
def updated_collections() -> bool:
        if not token:
            print("DB - No auth token to update collections")
            return False

        # Get the current collections and their schemas from pocket base
        # Pass the token in the Authorization header
        headers = {"Authorization": f"Bearer {token}"}
        # Assuming client is set to a proper instance, request collections
        collections_url = client + "/api/collections"
        response = client.get_one(collections_url, headers=headers)

        if response.status_code != 200:
            print(f"DB - Could not retrieve collection list, err{response.status_code}: {response.text}")
            return False

        current_schema = {}
        expected_schema = {}

        # Format the current schema for comparison to the expected schema
        collections_data = response.json()
        for collection in collections_data["items"]:
            if collection["system"]: # Skip system collections
                continue

            current_collection_schema = {}

            for field in collection["fields"]:
                if field['system']: # Skip system collections
                    continue
                current_collection_schema[field["name"]] = field["type"]

            current_schema[collection["name"]] = current_collection_schema

        # Load the expected database schema from the json file
        # and format to match current schema format for comparison.
        try:
            with open(EXPECTED_SCHEMA_JSON, "r") as file:
                expected_data = json.load(file)

                for collection in expected_data["collections"]:
                    collection_name = collection["name"]
                    collection_schema = collection["schema"]

                    expected_collection_schema = {}
                    for field in collection_schema:
                        expected_collection_schema[field["name"]] = field["type"]

                    # Include the created and updated fields for what is expected
                    expected_collection_schema["created"] = "autodate"
                    expected_collection_schema["updated"] = "autodate"

                    expected_schema[collection_name] = expected_collection_schema
        except Exception as e:
            print(f"DB - Could not load expected schema: {e}")
            return False

        # Update and create collections as needed
        for expected_collection in expected_schema:
            # If no collection matches expected collection, create it
            if expected_collection not in current_schema:
                print(f"DB - Creating collection {expected_collection}")
                create_table(expected_collection, expected_schema[expected_collection])
                continue

            if expected_schema[expected_collection] != current_schema[expected_collection]:
                print(f"DB - Clearing and updating collection {expected_collection}")
                # Drop the collection and recreate it with the new schema.
                delete_table(expected_collection)
                # Create the new schema by combining the default schema with the expected schema.
                create_table(expected_collection, expected_schema[expected_collection])
                continue

        # Remove any collections that are not in the expected schema
        for current_collection in current_schema:
            if current_collection not in expected_schema:
                print(f"DB - Removing deprecated collection {current_collection}")
                delete_table(current_collection)
json_data = {
    "table_tc_data": 
    {"Tc_1": 3,
    "Tc_2": 4}
    }

send_telemetry_message_to_database(json_data)
    # if table_name in client.collections.get_full_list():
    #     print("true")
    # else:
    #     print("false")

        #table_exists = True
    # except ClientResponseError as e:
    #     print(e)
    #     print(e.status)
    #     table_exists = False


    # if table_exists:
    #     print(f"found table {table_name}")
    # else:
    #     print(f"no table {table_name} found")

    # return table_exists



#check_table_exists("TEST_TABLE") #if something is garabage name it should false
#check_table_exists("TEST_TABLE") #if something is test_table it should be true



