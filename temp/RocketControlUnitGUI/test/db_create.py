from pocketbase import Client
from pocketbase.models.collection import collection

def create_table(client, name, data):
    client.collections.create()
    # give it a name
    name : string = name
    data : number = data
    #create a collection
    try:
        collection = client.collections.create(client)
        print(f"collection {string} add something here {number}.")
    except Exception as e:
        print(f"error has occured: {e}")
        #
def main():
    client = client('http://127')
    123 = [
        {"name": "something", "data": "something", "required": True},
        {"name": "something", "data": "something", "required": False}
    ]

    create_table(client, "TEST_TABLE", 123)


if __name__ == "__main__":
    main()