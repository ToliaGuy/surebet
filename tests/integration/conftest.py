import os
import sys

import pytest
from pymongo import MongoClient
from starlette.testclient import TestClient

sys.dont_write_bytecode = True

@pytest.fixture
def client():
    os.environ['MONGO_DB'] = 'test'
    os.environ['DEBUG'] = 'false'
    from apiestas.api.app.asgi import app
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope='function')
def collection():
    from apiestas.api.app.core.config import COLLECTION_NAME_MATCHES
    mongo = MongoClient(os.environ['DB_CONNECTION'], tz_aware=True)['test']
    col = mongo[COLLECTION_NAME_MATCHES]
    col.drop()
    yield col
    col.drop()
