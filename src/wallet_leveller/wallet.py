__copyright__ = 'Copyright(c) Gordon Elliott 2014'

"""
    The Wallet class takes care of identifying a wallet and moving funds
    to another wallet.
"""
import logging

from decimal import Decimal
from time import time, sleep

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

LOG = logging.getLogger(__name__)
MINIMUM_CONFIRMATIONS = 1

class Wallet(object):
    """ Wallet with one account
    """

    def __init__(self, uri, account_name, fee):
        self._connection = AuthServiceProxy(uri)
        self._account_name = account_name

        self._connection.settxfee(fee)

    @property
    def account_name(self):
        return self._account_name

    def get_address(self):
        return self._connection.getnewaddress(self._account_name)

    def get_accounts(self):
        return self._connection.listaccounts(MINIMUM_CONFIRMATIONS)

    @property
    def balance(self):
        return self._connection.getbalance(self._account_name, MINIMUM_CONFIRMATIONS)

    def move_to_account(self, source_account, destination_account, amount, comment=None):
        if amount > Decimal('0.0'):
            self._connection.move(source_account, destination_account, amount, MINIMUM_CONFIRMATIONS, comment)
        elif amount < Decimal('0.0'):
            self._connection.move(destination_account, source_account, -amount, MINIMUM_CONFIRMATIONS, comment)
        # just fall through if amount == 0.0 as there is nothing to do

    def transfer_to(self, destination, amount):
        """ Create an address for each wallet and transfer the funds between them
        """
        to_address = destination.get_address()

        validation = self._connection.validateaddress(to_address)
        if validation['isvalid']:
            try:
                transaction_id = self._connection.sendfrom(self._account_name, to_address, amount, MINIMUM_CONFIRMATIONS, 'out', 'in')
                if transaction_id is not None:
                    transaction_details = self._connection.gettransaction(transaction_id)
                    fee = transaction_details.get(u'fee')
                    # LOG.info('transaction_id %r, fee %r', transaction_id, fee)
                    return transaction_id, fee
                else:
                    return None, None
            except JSONRPCException as json_ex:
                LOG.exception('JSON Exception calling sendfrom(%s,_,%d) %r' % (self._account_name, amount, json_ex.error))
                raise
        else:
            return None, None

    def find_transaction(self, including_transaction, confirmations=MINIMUM_CONFIRMATIONS):
        for transaction in self._connection.listtransactions():
            if transaction.get(u'txid') == including_transaction:
                if transaction[u'confirmations'] >= confirmations:
                    return True
        return False

    def wait_for_transaction(
        self, including_transaction, confirmations=MINIMUM_CONFIRMATIONS, max_wait=60, secs_between_checks=0.1
    ):
        current = time()
        timeout = current + max_wait
        while current < timeout and not self.find_transaction(including_transaction, confirmations):
            sleep(secs_between_checks)
            current = time()
        return current < timeout

    def __repr__(self):
        """ Provide a string representation
        """
        return "{}('{}')".format(self.__class__.__name__, self._account_name)

"""
>>> bitcoinrpc.connect_to_remote('admin1', '123', host='localhost', port=19001)
>>> conn = bitcoinrpc.connect_to_remote('admin1', '123', host='localhost', port=19001)
>>> conn.getbalance()
>>> pay_to = conn.getnewaddress()
>>> pay_to
>>> rv = conn.validateaddress(pay_to)
>>> rv
>>> conn.getinfo()
>>> conn.move('test0', 'test1', 10.0)
>>> conn.getinfo()
>>> rv = conn.validateaddress(pay_to)
>>> altconn = bitcoinrpc.connect_to_local('2/bitcoin.conf')
"""