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


class TestUser(TestBase):
    title = 'Test user object'

    @default_test_setup(2)
    async def run(self):
        await self.client0.connect()

        result = await self.client0.query('list users')
        self.assertEqual(result.pop('users'), [['iris', 'full']])

        result = await self.client0.query('create user "sasientje" set password "blabla"')
        self.assertEqual(result.pop('success_msg'), "User 'sasientje' is created successfully.")

        result = await self.client0.query('list users where access < modify')
        self.assertEqual(result.pop('users'), [['sasientje', 'no access']])

        result = await self.client0.query('grant modify to user "sasientje"')
        self.assertEqual(result.pop('success_msg'), "Successfully granted permissions to user 'sasientje'.")

        self.db.add_replica(self.server1, 0, sleep=10)

        await self.client1.connect()

        result = await self.client1.query('list users where access < full')
        self.assertEqual(result.pop('users'), [['sasientje', 'modify']])

        result = await self.client1.query('create user "pee" set password "hihihaha"')
        time.sleep(0.1)
        result = await self.client0.query('list users where user ~ "p"')
        self.assertEqual(result.pop('users'), [['pee', 'no access']])

        self.client0.close()
        result = await self.server0.stop()
        self.assertTrue(result)

        result = await self.client1.query('alter user "sasientje" set password "dagdag"')

        self.server0.start(sleep=12)

        self.client0 = Client(
            self.db,
            self.server0,
            username="sasientje",
            password="dagdag")

        await self.client0.connect()
        result = await self.client0.query("show who_am_i")
        self.assertEqual(result['data'][0]['value'], 'sasientje')

        result = await self.client1.query('drop user "sasientje"')
        self.assertEqual(result.pop('success_msg'), "User 'sasientje' is dropped successfully.")
        time.sleep(0.1)

        result = await self.client0.query('count users')
        self.assertEqual(result.pop('users'), 2, msg='Expecting 2 users (iris and pee)')

        with self.assertRaisesRegexp(
                UserAuthError,
                "Access denied. User 'sasientje' has no 'grant' privileges."):
            result = await self.client0.query('grant full to user "pee"')

        self.client0.close()
        self.client1.close()


if __name__ == '__main__':
    SiriDB.HOLD_TERM = False
    Server.HOLD_TERM = False
    run_test(TestUser())