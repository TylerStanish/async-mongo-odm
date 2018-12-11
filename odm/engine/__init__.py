import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from odm.document import _document_factory
from odm.meta import _init_registrar


class Engine:
    def __init__(self, db_name: str, host: str = 'localhost', port: int = 27017,
                 loop: asyncio.AbstractEventLoop = None):
        self.client = AsyncIOMotorClient(host=host, port=port, io_loop=loop if loop else asyncio.get_event_loop())
        self.db_name = db_name
        self.class_col_mappings = {}
        self._unique_indexes_to_create = []


        class Registrar(type):
            def __init__(cls, name, bases, namespace):
                super().__init__(cls)
                _init_registrar(self, cls)


        self.Document = _document_factory(Registrar, self)

    async def save(self, document):
        doc = await getattr(getattr(self.client, self.db_name), document.__collection_name__)\
            .insert_one(document.as_dict())
        document._id = doc.inserted_id
        # return document.__class__.from_dict({**document.as_dict(), '_id': doc.inserted_id})
