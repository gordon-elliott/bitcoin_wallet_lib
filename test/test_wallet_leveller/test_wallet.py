__copyright__ = 'Copyright(c) Gordon Elliott 2014'

import logging
import unittest

from decimal import Decimal

from wallet_leveller.wallet import Wallet

from test_wallet_leveller.constants import (
    SOURCE_URI,
    DESTINATION_URI,
    SOURCE_DEFAULT_ACCOUNT,
    DESTINATION_DEFAULT_ACCOUNT,
    FEE,
    ACCOUNT_OPENING_BALANCE
)

SOURCE_TEST_ACCOUNT = 'test'
DESTINATION_TEST_ACCOUNT = 'test'

class WalletTests(unittest.TestCase):

    _multiprocess_shared_ = True

    def setUp(self):
        logging.basicConfig(level=logging.INFO)

        self.source = Wallet(SOURCE_URI, SOURCE_TEST_ACCOUNT, FEE)
        self.destination = Wallet(DESTINATION_URI, DESTINATION_TEST_ACCOUNT, FEE)

        self.source.move_to_account(
            SOURCE_DEFAULT_ACCOUNT, SOURCE_TEST_ACCOUNT, ACCOUNT_OPENING_BALANCE,
            'Priming source test account'
        )
        self.destination.move_to_account(
            DESTINATION_DEFAULT_ACCOUNT, DESTINATION_TEST_ACCOUNT, ACCOUNT_OPENING_BALANCE,
            'Priming destination test account'
        )


    def tearDown(self):
        self.source.move_to_account(
            SOURCE_TEST_ACCOUNT, SOURCE_DEFAULT_ACCOUNT, self.source.balance,
            'Clear down source test account'
        )
        self.destination.move_to_account(
            DESTINATION_TEST_ACCOUNT, DESTINATION_DEFAULT_ACCOUNT, self.destination.balance,
            'Clear down destination test account'
        )


    def assertBalance(self, opening_balance, amount_to_transfer, closing_balance):
        self.assertEqual(
            opening_balance + amount_to_transfer,
            closing_balance,
            '{} + {} != {}'.format(opening_balance, amount_to_transfer, closing_balance)
        )

    def _print_balances(self):
        print('Source: {:.8f}, Destination: {:.8f}'.format(self.source.balance, self.destination.balance))

#    @unittest.skip('wait for it')
    def test_simple(self):

        source_opening_balance = self.source.balance
        destination_opening_balance = self.destination.balance

        amount_to_transfer = Decimal('0.04')

        self._print_balances()
        transaction_id, fee = self.source.transfer_to(self.destination, amount_to_transfer)

        # need to wait for txn to be processed
        self.assertTrue(self.destination.wait_for_transaction(transaction_id))

        self._print_balances()
        self.assertBalance(source_opening_balance, -(amount_to_transfer - fee), self.source.balance)
        self.assertBalance(destination_opening_balance, amount_to_transfer, self.destination.balance)

#    @unittest.skip('wait for it')
    def test_round_trip(self):

        source_opening_balance = self.source.balance
        destination_opening_balance = self.destination.balance

        amount_to_transfer = Decimal('0.04')

        self._print_balances()
        transaction_id0, fee0 = self.source.transfer_to(self.destination, amount_to_transfer)

        # need to wait for txn to be processed
        self.assertTrue(self.destination.wait_for_transaction(transaction_id0))

        self._print_balances()
        self.assertBalance(source_opening_balance, -(amount_to_transfer - fee0), self.source.balance)
        self.assertBalance(destination_opening_balance, amount_to_transfer, self.destination.balance)

        transaction_id1, fee1 = self.destination.transfer_to(self.source, amount_to_transfer)

        # need to wait for txn to be processed
        self.assertTrue(self.source.wait_for_transaction(transaction_id1))

        self._print_balances()
        self.assertBalance(source_opening_balance, fee0, self.source.balance)
        self.assertBalance(destination_opening_balance, fee1, self.destination.balance)
