from config import database
import sqlalchemy
from sqlalchemy.orm import sessionmaker

engine = None
def init():

    global engine

    if engine is None:
        engine = sqlalchemy.create_engine('mysql+mysqlconnector://'+database.DB_USERNAME+':'+database.DB_PASSWORD+'@'+database.DB_HOST+':'+database.DB_PORT+'/'+database.DB_NAME+'', echo=True)

    db_session = sessionmaker(bind=engine)

    return db_session()


def bulk_insert(data, cls):
    engine.execute(
        cls.__table__.insert(),data
    )