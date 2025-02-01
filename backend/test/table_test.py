from pocketbase import Client
from pocketbase.utils import ClientResponseError


def check_table_exists(table_name: str) -> bool:

    client = Client('http://127.0.0.1:8090')
    authData = client.collection("_superusers").auth_with_password('kaileykobar@gmail.com', 'CARtank66$');
    #try:
    #print(client.collection(table_name))
    #print(client.record_service)


    #table should pass if the table name exists or not. giving parameters it wants to look for (table name)
    print(client.collections.get_full_list(query_params=table_name))
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
