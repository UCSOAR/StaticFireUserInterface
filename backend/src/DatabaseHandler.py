# General imports =================================================================================
import os
import json
import multiprocessing as mp
from typing import Tuple
from pocketbase import Client
from pocketbase.utils import ClientResponseError
from pocketbase.services.realtime_service import MessageData
from dotenv import load_dotenv

# Project specific imports ========================================================================
from src.support.CommonLogger import logger
from src.ThreadManager import THREAD_MESSAGE_DB_WRITE, THREAD_MESSAGE_KILL, THREAD_MESSAGE_LOAD_CELL_COMMAND, THREAD_MESSAGE_LOAD_CELL_SLOPE, THREAD_MESSAGE_REQUEST_LOAD_CELL_SLOPE, THREAD_MESSAGE_SERIAL_WRITE, THREAD_MESSAGE_STORE_LOAD_CELL_SLOPE, THREAD_MESSAGE_HEARTBEAT, WorkQ_Message
from src.Utils import Utils as utl

# Class Definitions ===============================================================================
class DatabaseHandler():
    def __init__(self, thread_name: str, thread_workq: mp.Queue, message_handler_workq: mp.Queue):
        """
        Thread to handle the pocketbase database communication.
        The Thread is subscribed to the CommandMessage
        collection to wait for commands created in the front end. 
        The handler can also send telemetry data to the database
        to be read by the front end.
        """
        logger.info("DatabaseHandler initializing")
        DatabaseHandler.thread_workq = thread_workq
        DatabaseHandler.send_message_workq = message_handler_workq
        DatabaseHandler.thread_name = thread_name

        load_dotenv()
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')

        #DatabaseHandler.client = Client('http://192.168.0.69:8090')
        DatabaseHandler.client = Client('http://127.0.0.1:8090')
        DatabaseHandler.client.auth_store.clear()
        authData = DatabaseHandler.client.collection("_superusers").auth_with_password('kaileykobar@gmail.com', 'CARtank66$')
        DatabaseHandler.client.collection('Heartbeat').subscribe(DatabaseHandler._handle_heartbeat_callback)
        DatabaseHandler.client.collection('CommandMessage').subscribe(DatabaseHandler._handle_command_callback)
        DatabaseHandler.client.collection('LoadCellCommands').subscribe(DatabaseHandler._handle_load_cell_command_callback)
        logger.success(f"Successfully started {thread_name} thread")

    @staticmethod
    def _handle_heartbeat_callback(document: MessageData):
        """
        Whenever a new entry is created in the Heartbeat
        collection, this function is called to handle the
        command and forward it to the HeartbeatHandler.

        Args:
            document (MessageData): the change notification from the database.
        """
        logger.info("Received new heartbeat from the database")
        logger.debug(f"Record command: {document.record.message}")
        DatabaseHandler.send_message_workq.put(
            WorkQ_Message(
                DatabaseHandler.thread_name,
                'heartbeat', 
                THREAD_MESSAGE_HEARTBEAT, 
                (document.record.message,)
            )
        )
            
    @staticmethod
    def _handle_command_callback(document: MessageData):
        """
        Whenever a new entry is created in the CommandMessage 
        collection, this function is called to handle the
        command and forward it to the serial port.

        Args:
            document (MessageData): the change notification from the database.
        """

        logger.info("Received new command from the database")
        logger.debug(f"Record command: {document.record.command}")
        DatabaseHandler.send_message_workq.put(
            WorkQ_Message(
                DatabaseHandler.thread_name,
                'all_serial', 
                THREAD_MESSAGE_SERIAL_WRITE, 
                (document.record.command,
                 document.record.target,
                 document.record.command_param,
                 document.record.source_sequence_num
                )
            )
        )

    @staticmethod
    def _handle_load_cell_command_callback(document: MessageData):
        """
        Whenever a new entry is created in the LoadCellCommands
        collection, this function is called to handle the command
        and forward it to the load cell handler.

        Args:
            document (MessageData): 
                the change notification from the database.
        """
        logger.info("Received new load cell command from the database")
        logger.debug(f"Record command: {document.record.command}")
        DatabaseHandler.send_message_workq.put(
            WorkQ_Message(
                DatabaseHandler.thread_name,
                'loadcell',
                THREAD_MESSAGE_LOAD_CELL_COMMAND,
                (document.record.target, document.record.command, document.record.weight)
            )
        )

    @staticmethod
    def send_telemetry_message_to_database(json_data: str):
        """
        Send a preserialized JSON message to the database.

        Note: The third key in the JSON data is assumed to be the table name
        """
        # Extract the table name from the JSON data
        json_data = json.loads(json_data)
        if len(list(json_data.keys())) < 3:
            logger.warning(f"Received, poorly formed json: {json_data}")
            return

        table_name = list(json_data.keys())[2]

        logger.info(f"Adding an entry to the {table_name} table")
        logger.info(f"Entry: {json_data[table_name]}")

        # Push the JSON data to PocketBase using the correct schema
        try:
            DatabaseHandler.client.collection(table_name).create(json_data[table_name])
        except Exception as e:
            logger.error(f"Failed to create entry in {table_name}: {json_data}")
            print(e)
            schema = make_schema_from_data(json_data[table_name])
            DatabaseHandler.create_table(table_name, schema)
            DatabaseHandler.client.collection(table_name).create(json_data[table_name])

    @staticmethod
    def make_schema_from_data(json_data):
        # Build schema fields
        schema = []
        for field_name, field_value in json_data.items():
            print(field_name)
            print(field_value)
        #make an if statment if a string it should be text, if a int float etc should be a number if a dictionary print out json data

            field_type = "not known"  

            if type(field_value) == str:
                field_type = "text"
            elif type(field_value) in [int, float]:
                field_type = "number"
            elif type(field_value) == dict:
                field_type = "json"

            #print(field_type)

            field_data = {
                "name": field_name,
                "type": field_type,
                "required": False,
                "options": {}
                }

            # Apply type-specific options
            if field_type == "text":
                field_data["options"] = {"maxSize": 100000}
            elif field_type == "number":
                field_data["options"] = {"min": None, "max": None}
            schema.append(field_data)

        # Include the created and updated timestamps
        schema.append({'name': 'updated', 'onCreate': True, 'onUpdate': True, 'type': 'autodate'})
        schema.append({'name': 'created', 'onCreate': True, 'onUpdate': False, 'type': 'autodate'})
        return schema
        #updated_collection = client.collections.update(created_collection.id, update_data)

    @staticmethod
    def create_table(name, schema):
        """
        Creates a collection in PocketBase.

        """
        #create a collection
        collection_data = {
        "name": name,
        "type": "base",
        "fields": schema
        }
        try:
            DatabaseHandler.client.collections.create(collection_data)
            print(f"Collection '{name}' created with schema: {schema}")
        except ClientResponseError as e:
            print(f"Error creating collection '{name}': {e}")
   
    @staticmethod
    def send_load_cell_cali_to_database(thread_message: Tuple[str, str]):
        """
        Send a preserialized JSON message to the database.
        """

        load_cell_name = thread_message[0]
        json_data = thread_message[1]

        logger.info(f"Updating an entry to the LoadCellCalibrationCurves table")
        logger.info(f"Entry: {json_data}")

        # Push the JSON data to PocketBase using the correct schema
        try:
            record = DatabaseHandler.client.collection('LoadCellCalibrationCurves').get_first_list_item(f'name="{load_cell_name}"')
            entry_exists = True
        except Exception:
            entry_exists = False
            logger.debug(f"No existing slope for {load_cell_name}, creating new entry")

        try:
            if entry_exists:
                DatabaseHandler.client.collection("LoadCellCalibrationCurves").update(record.id, json.loads(json_data))
            else:
                DatabaseHandler.client.collection("LoadCellCalibrationCurves").create(json.loads(json_data))
        except Exception as e:
            if entry_exists:
                logger.error(f"Failed to update entry in LoadCellCalibrationCurves: {json_data}\n{e}")
            else:
                logger.error(f"Failed to create entry in LoadCellCalibrationCurves: {json_data}\n{e}")

    @staticmethod
    def get_load_cell_cali_from_database(load_cell_name: str):
        """
        Get the load cell calibration curve from the database.
        """
        try:
            record = DatabaseHandler.client.collection('LoadCellCalibrationCurves').get_first_list_item(f'name="{load_cell_name}"')
            DatabaseHandler.send_message_workq.put(
                WorkQ_Message(
                    DatabaseHandler.thread_name,
                    'loadcell',
                    THREAD_MESSAGE_LOAD_CELL_SLOPE,
                    (load_cell_name, record.slope, record.intercept)
                )
            )
        except Exception as e:
            logger.error(f"Failed to get {load_cell_name} calibration curve from the database: {e}")

# Procedures ======================================================================================
def database_thread(thread_name: str, db_workq: mp.Queue, message_handler_workq: mp.Queue) -> None:
    """
    The main loop of the database handler. It subscribes to the CommandMessage collection
    """

    DatabaseHandler(thread_name, db_workq, message_handler_workq)

    while 1:
        # If there is any workq messages, process them
        if not process_workq_message(db_workq.get(block=True)):
            return
        
def process_workq_message(message: WorkQ_Message) -> bool:
    """
    Process the message from the workq.

    Args:
        message (WorkQ_Message):
            The message from the workq.
    """
    logger.debug(f"Processing db workq message: {message.message_type}")
    messageID = message.message_type

    if messageID == THREAD_MESSAGE_KILL:
        logger.debug(f"Killing database thread")
        return False
    elif messageID == THREAD_MESSAGE_DB_WRITE:   
        logger.debug(f"Writing {utl.get_message_from_enum(message.message[0])}")
        DatabaseHandler.send_telemetry_message_to_database(message.message[1])
        return True
    elif messageID == THREAD_MESSAGE_STORE_LOAD_CELL_SLOPE:
        logger.debug(f"Writing a new load cell calibration to the database")
        DatabaseHandler.send_load_cell_cali_to_database(message.message)
        return True
    elif messageID == THREAD_MESSAGE_REQUEST_LOAD_CELL_SLOPE:
        logger.debug(f"Requesting the last load cell slope from the database")
        DatabaseHandler.get_load_cell_cali_from_database(message.message[0])
        return True

    return True