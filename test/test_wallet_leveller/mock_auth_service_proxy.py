__copyright__ = 'Copyright(c) Gordon Elliott 2014'

from collections import defaultdict
from decimal import Decimal

NO_FEE = Decimal('0.0')

class MockAuthServiceProxy(object):
    def __init__(self, *args, **kwargs):

        self._accounts = defaultdict(Decimal)
        self._accounts[''] = Decimal('1000000.0')
        self._transactions = []
        self._fee = Decimal('0.0')

    def settxfee(self, fee):
        self._fee = fee
        
    def getnewaddress(self, account_name):
        if account_name not in self._accounts:
            self._accounts[account_name] = Decimal('0.0')
        return (self, account_name)

    def listaccounts(self, minimum_confirmations):
        return self._accounts.keys()

    def getbalance(self, account_name, minimum_confirmations):
        return self._accounts[account_name]

    def move(self, source_account, destination_account, amount, minimum_confirmations, comment):
        self._send(source_account, self, destination_account, amount, fee=NO_FEE)

    def validateaddress(self, to_address):
        proxy, name = to_address
        return {'isvalid': True} if name in proxy._accounts else {'isvalid': False}

    def sendfrom(self, source_account, to_address, amount, minimum_confirmations, out_descr, in_descr):
        destination_proxy, destination_account = to_address
        return self._send(source_account, destination_proxy, destination_account, amount, fee=self._fee)

    def gettransaction(self, transaction_id):
        return self._transactions[transaction_id]

    def listtransactions(self):
        return enumerate(self._transactions)

    def _send(self, source_account, destination_proxy, destination_account, amount, fee):
        if amount <= self._accounts[source_account]:
            self._accounts[source_account] -= amount
            self._accounts[source_account] -= fee
            destination_proxy._accounts[destination_account] += amount
            self._transactions.append(
                {
                    u'source': (self, source_account),
                    u'destination': (destination_proxy, destination_account),
                    u'amount': amount,
                    u'fee': -1 * fee
                }
            )
            return len(self._transactions) - 1
        else:
            return None
