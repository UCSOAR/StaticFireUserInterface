from pocketbase import PocketBase
from pocketbase.models.collection import Collection

def create_table(client, name, data):
    """
    Creates a collection in PocketBase.

    """
    name : str = name
    data : int = data
    #create a collection
    try:
        collection_data = {
        "name": name,
        "data": data,
        }
        collection = client.collections.create(collection_data)
        print(f"collection '{name}' add something here '{data}'.")
    except Exception as e:
        print(f"error has occured: {e}")
        
def main():    
    client = PocketBase('http://127.0.0.1:8090')
    authData = client.collection("_superusers").auth_with_password(admin_username, admin_password)

    something = [
        {"name": "something", "type":  "something", "required": True},
        {"name": "something", "type": "something", "required": False}
    ]

    create_table(client, "TEST_TABLE", something)


if __name__ == "__main__":
    main()
