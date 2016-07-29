import random
import time
from testing import Client
from testing import default_test_setup
from testing import gen_points
from testing import gen_series
from testing import InsertError
from testing import PoolError
from testing import run_test
from testing import Server
from testing import ServerError
from testing import SiriDB
from testing import TestBase
from testing import UserAuthError

PI = 'ԉ'
Klingon = '     qajunpaQHeylIjmo’ batlh DuSuvqang charghwI’ ‘It.'

class TestSeries(TestBase):
    title = 'Test series object'

    @default_test_setup(1)
    async def run(self):
        await self.client0.connect()

        points = gen_points(n=10)

        self.assertEqual(
            await self.client0.insert({
                PI: points,
                Klingon: points
            }), {'success_msg': 'Inserted 20 point(s) successfully.'})

        self.assertEqual(
            await self.client0.query('select * from "{}"'.format(PI)),
            {PI: points})

        self.assertEqual(
            await self.client0.query('select * from "{}"'.format(Klingon)),
            {Klingon: points})

        self.client0.close()



if __name__ == '__main__':
    SiriDB.HOLD_TERM = False
    Server.HOLD_TERM = False
    run_test(TestSeries())
