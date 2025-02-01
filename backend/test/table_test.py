from pocketbase import Client
from pocketbase.utils import ClientResponseError

client = Client('http://127.0.0.1:8090')

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
json_data = {
    "table_tc_data": 
    {"Tc_1": 3,
    "Tc_2": 4}
    }


schema = send_telemetry_message_to_database(json_data)
schema = json_data[0]

def create_table(name, schema):
    #create a collection
    collection_data = {
    "name": name,
    "type": "base",
    "schema": schema
    }
    client.collections.create(collection_data)
    print(f"Collection '{name}' created with schema: {schema}")

def check_table_exists(table_name: str) -> bool:

    authData = client.collection("_superusers").auth_with_password('kaileykobar@gmail.com', 'CARtank66$');
    #try:
    #print(client.collection(table_name))
    #print(client.record_service)


    #table should pass if the table name exists or not. giving parameters it wants to look for (table name)
    try:
        client.collections.get_one(table_name)
        client.collection(table_name).create([table_name])
    except:
        create_table(table_name)  

    if table_name in client.collections.get_full_list():
        print("true")
    else:
        print("false")

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



check_table_exists("TEST_TABLE") #if something is garabage name it should false
#check_table_exists("TEST_TABLE") #if something is test_table it should be true



