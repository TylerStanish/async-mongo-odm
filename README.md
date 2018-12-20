#### This is in Alpha, more documentation to come

This is basically a light layer over Motor with an emphasis on easy serialization

## Basic Usage with AsyncIO
```python
import asyncio
from typing import List

from odm.engine import Engine
from odm.type import MongoId, MongoString, MongoList, MongoForeignKey

engine = Engine.new_asyncio_engine(db_name='my_app')

# or create an engine with any event loop
engine = Engine.new_asyncio_engine(db_name='my_app', loop=asyncio.get_event_loop())

# or create an engine with a Tornado event loop
import tornado.ioloop
loop = tornado.ioloop.IOLoop.current()
engine = Engine.new_tornado_engine(db_name='my_app', loop=loop)

class User(engine.Document):
    __collection_name__ = 'users'
    
    _id = MongoId()
    email = MongoString(unique=True, nullable=False)
    password = MongoString(nullable=False, serialize=False)
    user_friends: List[MongoForeignKey] = MongoList(containing_type=MongoForeignKey)

user = User(email='email@random.com', password='some hashed password')
user.user_friends = ['some user id', 'some other user id']

engine.save(user)

print(user.as_json())
"""
{
    "_id": "f$8skcj3ksxssjekjsjksks",
    "email": "email@random.com",
    "userFriends": [
        "some user id",
        "some other user id"
    ]
}
"""
# will automatically convert snake to camel case and vice versa


```
