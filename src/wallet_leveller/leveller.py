__copyright__ = 'Copyright(c) Gordon Elliott 2014'

"""
    Applies defined rules to maintain wallets at certain levels.
    There are two operations the leveller can carry out:
        top up: increases the level of funds in a wallet to meet the specified
                threshold
        clear down: reduce the level of funds in a wallet to meet the
                specified threshold

    Consider a small change wallet on mobile device. In the event that the
    mobile device is lost it is desirable that there are not too many funds
    on it. On the other hand it is tedious to constantly keep topping up a
    wallet that is being used regularly.

    Secondly consider a current account and a savings account. It is desirable
    to keep most funds in the savings account provided that there are sufficient
    funds in the current account to deal with day-to-day expenditure.
"""
from decimal import Decimal


class UnknownWallet(Exception):
    pass


class _WalletRegistration(object):

    def __init__(self, wallet, low_water_mark):
        self._wallet = wallet
        self._low_water_mark = low_water_mark

    @property
    def funds_required(self):
        return self._wallet.balance < self._low_water_mark

    @property
    def required_funds(self):
        if self.funds_required:
            return self._low_water_mark - self._wallet.balance
        else:
            return Decimal('0.0')

    @property
    def funds_available(self):
        return self._wallet.balance


class _WalletConnection(object):

    def __init__(self, source, destination, weight):
        self._source = source
        self._destination = destination
        self._weight = weight

    @property
    def transfer_permitted(self):
        return (
            self._destination.funds_required
            and
            self._destination.required_funds <= self._source.funds_available
        )

    def generate_transfer(self):
        amount = self._destination.required_funds
        return _Transfer(self, amount)


class _Transfer(object):

    def __init__(self, connection, amount):
        self._connection = connection
        self._amount = amount

    @property
    def source(self):
        return self._connection._source._wallet

    @property
    def destination(self):
        return self._connection._destination._wallet

    @property
    def amount(self):
        return self._amount


class Leveller(object):

    def __init__(self):
        self._wallets = {}
        self._connections = []

    def add_wallet(self, wallet, low_water_mark):
        wallet_registration = _WalletRegistration(wallet, low_water_mark)
        self._wallets[wallet] = wallet_registration
        return wallet_registration

    def connect(self, source, destination, weight=1):
        if source not in self._wallets:
            raise UnknownWallet('Source wallet not registered')
        if destination not in self._wallets:
            raise UnknownWallet('Destination wallet not registered')

        connection = _WalletConnection(self._wallets[source], self._wallets[destination], weight)
        self._connections.append(connection)

        return connection

    def required_funds(self, wallet):
        registration = self._wallets.get(wallet)
        if registration is None:
            raise UnknownWallet
        return registration.required_funds

    def proposed_transfers(self):
        return [
            connection.generate_transfer()
            for connection in self._connections
            if connection.transfer_permitted
        ]
