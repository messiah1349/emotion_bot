from lib.db.tables import create_data_base_and_tables, get_engine
from lib.client import Client
from configs.constants import API_TOKEN

if __name__=='__main__':

    engine = get_engine()
    create_data_base_and_tables(engine)

    client = Client(API_TOKEN, engine)
    client.build_application()

