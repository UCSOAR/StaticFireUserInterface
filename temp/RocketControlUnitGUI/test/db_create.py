from pocketbase import PocketBase
from pocketbase.models.collection import Collection

def create_table(client, name, schema):
    """
    Creates a collection in PocketBase.

    """
    #create a collection
    try:
        collection_data = {
        "name": name,
        "type": "base",
        "fields": schema
        }
        collection = client.collections.create(collection_data)
        print(f"collection '{name}' add something here '{schema}'.")
    except Exception as e:
        print(f"error has occured: {e}")


def main():    
    client = PocketBase('http://127.0.0.1:8090')

    try:
        authData = client.collection("_superusers").auth_with_password('kaileykobar@gmail.com', 'CARtank66$')
        print("Authentication successful.")
    except:
        print(f"Authentication failed.")
        return

    schema = [
        {"name": "something", "type":  "text", "required": True, "unique": False},
        {"name": "tempature", "type":  "number", "required": True, "unique": False}
    ]

    create_table(client, "TEST_TABLE", schema)


if __name__ == "__main__":
    main()
