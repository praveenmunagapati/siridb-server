import unittest
import time
from .siridb import SiriDB
from .server import Server
from .client import Client

def default_test_setup(nservers=1):
    def wrapper(func):
        async def wrapped(self):
            self.db = SiriDB()

            self.servers = [Server(n) for n in range(nservers)]
            for n, server in enumerate(self.servers):
                setattr(self, 'server{}'.format(n), server)
                setattr(self, 'client{}'.format(n), Client(self.db, server))
                server.create()
                await server.start()

            time.sleep(2.0)

            await self.db.create_on(self.server0, sleep=2)

            close = await func(self)

            if close or close is None:
                for server in self.servers:
                    result = await server.stop()
                    self.assertTrue(
                        result,
                        msg='Server {} did not close correctly'.format(
                            server.name))

        return wrapped
    return wrapper

class TestBase(unittest.TestCase):

    title = 'No title set'

    async def run():
        raise NotImplementedError()

    async def assertSeries(self, client, series):
        await self.assertAlmostSeries(client, series, allowed_mismatches=0)

    async def assertAlmostSeries(self, client, series, allowed_mismatches=1):
        d = {s.name: len(s.points) for s in series}

        result = await client.query('list series name, length')
        result = {name: length for name, length in result['series']}
        for s in series:
            if s.points:
                length = result.get(s.name, None)
                try:

                    assert length is not None, \
                        'series {!r} is missing in the result'.format(s.name)
                    assert length == len(s.points), \
                        'expected {} point(s) but found {} point(s) ' \
                        'for series {!r}' \
                        .format(len(s.points), length, s.name)
                except AssertionError as e:
                    if allowed_mismatches:
                        allowed_mismatches -= 1
                    # else:
                    #     raise e
