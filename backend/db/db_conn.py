import pymongo
from urllib.parse import quote_plus
import os

class MongoQueries:
    def __init__(self):
        self.host = "localhost"
        self.port = 27017
        self.service_name = 'labdatabase'

        auth_file = os.path.join("backend", "db", "conexion", "passphrase", "authentication.mongo")
        if os.path.exists(auth_file):
            with open(auth_file, "r") as f:
                self.user, self.passwd = f.read().split(',')
        else:
            # Fallback para variáveis de ambiente
            self.user = os.getenv('MONGO_USER', 'labdatabase')
            self.passwd = os.getenv('MONGO_PASS', 'lab@Database2025')

    def __del__(self):
        if hasattr(self, "mongo_client"):
            self.close()

    def connect(self):
        self.mongo_client = pymongo.MongoClient(f"mongodb://{self.user}:{quote_plus(self.passwd)}@{self.host}:{self.port}/")
        self.db = self.mongo_client[self.service_name]
        return self.db

    def close(self):
        if hasattr(self, "mongo_client"):
            self.mongo_client.close()

def get_connection():
    mongo = MongoQueries()
    return mongo.connect()

def release_connection(conn):
    pass

def connect():
    mongo = MongoQueries()
    return mongo.connect()

def close():
    pass