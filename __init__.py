import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

# This seems to get imported before sanic is run, so we need to call the below function to update it AFTER sanic
# gets its event loop set up
client = AsyncIOMotorClient(io_loop=asyncio.get_event_loop())
db_name = None


def initialize_asyncio_motor_client(loop, db, host='localhost', port=27017):
    global client  # changed this to global to fix our 'RuntimeError: Task not running in same loop'
    global db_name
    client = AsyncIOMotorClient(host=host, port=port, io_loop=loop)
    db_name = db
