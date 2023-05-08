import os
from lib.db.tables import create_data_base_and_tables, get_engine
from lib.client import Client

if __name__=='__main__':

    POSTGRE_PASSWORD = os.getenv('POSTGRE_PASSWORD', '1234')
    POSTGRE_HOST = os.getenv('POSTGRE_HOST', 'localhost')
    POSTGRE_PORT = os.getenv('POSTGRE_PORT', '1349')
    API_TOKEN = os.getenv('EMOTION_BOT_TOKEN', '214139458:AAH8UGU0PW3vUE1lRz-gjXnlB6TroUvpfUk') 
    # just a test bot by default for testing
    
    engine = get_engine(POSTGRE_PASSWORD, POSTGRE_PORT, POSTGRE_HOST)
    create_data_base_and_tables(engine)

    client = Client(API_TOKEN, engine)
    client.build_application()
