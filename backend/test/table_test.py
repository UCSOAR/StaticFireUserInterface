from pocketbase import Client
from pocketbase.utils import ClientResponseError


def check_table_exists(table_name: str) -> bool:

    client = Client('http://127.0.0.1:8090')

    try:
        client.collection(table_name).create({"something": 'Tel', "tempature": 1})
        table_exists = True
    except ClientResponseError as e:
        print(e)
        print(e.code)
        table_exists = False


    if table_exists:
        print(f"found table {table_name}")
    else:
        print(f"no table {table_name} found")

    return table_exists




check_table_exists("garbage_name")
check_table_exists("TEST_TABLE")






































# def create_table(self, name, schema):
#         """
#         Creates a collection in PocketBase.

#         """
#         #create a collection
#         try:
#             collection_data = {
#             "name": name,
#             "type": "base",
#             "schema": schema
#             }
#             client.collections.create(collection_data)
#             print(f"Collection '{name}' created with schema: {schema}")

#         except Exception as e:
#             print(f"An error occurred: {e}")
