from pocketbase import Client
from pocketbase.models.collection import collection

def create_table(client, name, data):
    client.collections.create()
    # give it a name
    name : string = name
    data : number = data
    #create a collection

def main():
    client = client('http://127')
    create_table(client, "TEST_TABLE", 123)
    
if __name__ == "__main__":
    