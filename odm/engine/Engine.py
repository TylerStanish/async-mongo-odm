import asyncio
from contextlib import asynccontextmanager

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from odm.document import _document_factory
from odm.meta import _init_registrar


class Engine:

    def __init__(self, loop, client, db_name: str, host: str = 'localhost', port: int = 27017):
        self.db_name = db_name
        self.host = host
        self.port = port
        self.loop = loop
        self.client = client

        class Registrar(type):
            def __init__(cls, name, bases, namespace):
                super().__init__(cls)
                _init_registrar(engine=self, registrar_cls=cls)

        self.Document = _document_factory(engine=self, Registrar=Registrar)

    @classmethod
    def new_asyncio_engine(cls, db_name: str, host: str = 'localhost', port: int = 27017,
                 loop=None):
        if not loop:
            loop = asyncio.get_event_loop()
        client = AsyncIOMotorClient(host=host, port=port, io_loop=loop)
        return cls(loop, client, db_name, host, port)

    @classmethod
    def new_tornado_engine(cls, db_name: str, loop, host: str = 'localhost', port: int = 27017):
        from motor.motor_tornado import MotorClient
        client = MotorClient(host=host, port=port, io_loop=loop)
        return cls(loop, client, db_name, host, port)

    async def save(self, document, session=None) -> None:
        d = document.as_dict()
        if not document._id:
            d.pop('_id')
        else:
            d['_id'] = ObjectId(document._id)
        doc = await getattr(getattr(self.client, self.db_name), document.__collection_name__) \
            .insert_one(d, session=session)
        document._id = str(doc.inserted_id)
        # return document.__class__.from_dict({**document.as_dict(), '_id': doc.inserted_id})

    @asynccontextmanager
    async def start_transaction(self):
        """
        This context manager is meant for single-transactions only. Do not nest these transactions because it
        has not been tested
        :return:
        """
        async with await self.client.start_session() as session:
            async with session.start_transaction():
                yield session
