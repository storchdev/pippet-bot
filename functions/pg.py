import asyncio
import asyncpg

lock = asyncio.Lock()


async def connect():
    global db

    with open('./logins/pgpass.txt') as file:
        password = file.read()

    keys = {
        'user': 'postgres',
        'database': 'prodigy',
        'host': 'localhost',
        'port': '5555',
        'password': password
    }

    user, database, host, port, password = \
        keys['user'], keys['database'], keys['host'], keys['port'], keys['password']

    db = await asyncpg.connect(user=user, database=database, host=host, port=port, password=password)


loop = asyncio.get_event_loop()
loop.run_until_complete(connect())


async def execute(query, params: tuple = None):
    global db

    if params is None:
        await db.execute(query)
    else:
        async with lock:
            await db.execute(query, *params)


async def fetchrow(query, params: tuple):
    global db

    async with lock:
        row = await db.fetchrow(query, *params)
        return row


async def fetch(query, params: tuple):
    global db

    async with lock:
        rows = await db.fetch(query, *params)
        return rows
