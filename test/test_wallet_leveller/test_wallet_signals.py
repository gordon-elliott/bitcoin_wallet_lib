__copyright__ = 'Copyright(c) Gordon Elliott 2014'

# TODO integrate notifier into the test, app needs to run in a separate process
# TODO need to find way to have multiple listener ports for running as a nose test

import logging
import traceback
import unittest

from decimal import Decimal

from multiprocessing import Process, Queue

from event_api.push_pull import Listener
from event_api.signals import LISTENER_PORT

from wallet_leveller.wallet import Wallet

SOURCE_URI = "http://admin1:123@127.0.0.1:19001"
DESTINATION_URI = "http://admin2:123@127.0.0.1:19011"

SOURCE_DEFAULT_ACCOUNT = ''
DESTINATION_DEFAULT_ACCOUNT = ''

SOURCE_ACCOUNT_PATTERN = 'src-{}'
DESTINATION_ACCOUNT_PATTERN = 'dst-{}'

FEE = Decimal('0.00001')
ACCOUNT_OPENING_BALANCE = Decimal('0.1')

LOG = logging.getLogger(__name__)


def _register_callbacks(port, result_queue, callback_map):
    listener = Listener(port)
    try:
        for transaction_id, callback in iter(callback_map.items()):
            listener.register(transaction_id, callback, None)

        for result in listener.listen():
            result_queue.put(result)

    except Exception as ex:
        traceback.print_exc()
        result_queue.put(ex)

    # signal end of queue
    result_queue.put(None)

def check_async(callback_map):
    result_queue = Queue()

    client_process = Process(target=_register_callbacks, args=(LISTENER_PORT, result_queue, callback_map))
    client_process.daemon = True
    client_process.start()

    results = []
    result = result_queue.get(block=True, timeout=360)
    while result is not None:
        if isinstance(result, Exception):
            raise result
        else:
            results.append(result)
        result = result_queue.get(block=True, timeout=360)

    return all(results)


class WalletTests(unittest.TestCase):

    _multiprocess_shared_ = True        # used when invoked by Nose

    def setUp(self):
        logging.basicConfig(level=logging.INFO)

        # each test gets a separate account
        self.source_account_name = SOURCE_ACCOUNT_PATTERN.format(self.id())
        self.destination_account_name = DESTINATION_ACCOUNT_PATTERN.format(self.id())

        self.source = Wallet(SOURCE_URI, self.source_account_name, FEE)
        self.destination = Wallet(DESTINATION_URI, self.destination_account_name, FEE)

        # put an opening balance into the test accounts, while clearing any balance from a
        # prior test
        self.source.move_to_account(
            SOURCE_DEFAULT_ACCOUNT, self.source_account_name,
            ACCOUNT_OPENING_BALANCE - self.source.balance,
            'Priming source test account'
        )
        self.destination.move_to_account(
            DESTINATION_DEFAULT_ACCOUNT, self.destination_account_name,
            ACCOUNT_OPENING_BALANCE - self.destination.balance,
            'Priming destination test account'
        )


    def tearDown(self):
        pass
        # don't adjust accounts in the tear down as that will modify the balances before the test
        # callbacks can be called


    def assertBalance(self, opening_balance, amount_to_transfer, closing_balance):
        self.assertEqual(
            opening_balance + amount_to_transfer,
            closing_balance,
            '{} + {} != {}'.format(opening_balance, amount_to_transfer, closing_balance)
        )

    def _print_balances(self):
        LOG.info('Balances - {}: {:.8f}, {}: {:.8f}'.format(
            self.source_account_name, self.source.balance,
            self.destination_account_name, self.destination.balance
        ))

    def _transaction_confirmed(self, transaction_id):
        return self.destination.find_transaction(transaction_id) and self.source.find_transaction(transaction_id)

    def _wrap_with_confirmation(self, test_function):
        def wrapped(cb_transaction_id, cb_message_data, cb_associated_data):
            if self._transaction_confirmed(cb_transaction_id):
                test_function(cb_transaction_id, cb_message_data, cb_associated_data)

                return True, True
            else:
                return False, None

        return wrapped

    def _async_assertions(self, transaction_id, transaction_tests):
        self.assertTrue(
            check_async({
                transaction_id: self._wrap_with_confirmation(transaction_tests),
            })
        )

    def test_simple(self):

        def transaction_tests(cb_transaction_id, cb_message_data, cb_associated_data):
            self.assertBalance(source_opening_balance, -(amount_to_transfer - fee), self.source.balance)
            self.assertBalance(destination_opening_balance, amount_to_transfer, self.destination.balance)

        source_opening_balance = self.source.balance
        destination_opening_balance = self.destination.balance

        amount_to_transfer = Decimal('0.04')

        transaction_id, fee = self.source.transfer_to(self.destination, amount_to_transfer)

        self._async_assertions(transaction_id, transaction_tests)

    def test_round_trip(self):

        def transaction0_tests(cb_transaction_id, cb_message_data, cb_associated_data):
            self.assertBalance(source_opening_balance, -(amount_to_transfer - fee0), self.source.balance)
            self.assertBalance(destination_opening_balance, amount_to_transfer, self.destination.balance)

        def transaction1_tests(cb_transaction_id, cb_message_data, cb_associated_data):
            self.assertBalance(source_opening_balance, fee0, self.source.balance)
            self.assertBalance(destination_opening_balance, fee1, self.destination.balance)

        source_opening_balance = self.source.balance
        destination_opening_balance = self.destination.balance

        amount_to_transfer = Decimal('0.04')

        transaction_id0, fee0 = self.source.transfer_to(self.destination, amount_to_transfer)

        self._async_assertions(transaction_id0, transaction0_tests)

        transaction_id1, fee1 = self.destination.transfer_to(self.source, amount_to_transfer)

        self._async_assertions(transaction_id1, transaction1_tests)
