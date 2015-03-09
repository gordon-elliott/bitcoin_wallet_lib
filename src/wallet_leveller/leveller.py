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

from networkx import DiGraph, is_directed_acyclic_graph, bfs_edges, topological_sort


class UnknownWallet(Exception):
    pass


class ConflictingWaterMarks(Exception):
    pass


class DuplicateConnection(Exception):
    pass


class _WalletRegistration(object):

    def __init__(self, wallet, desired_level=None, low_water_mark=None, high_water_mark=None):

        # TODO include desired_level into water mark checks

        if (
            low_water_mark is not None and high_water_mark is not None
            and low_water_mark > high_water_mark
        ):
            raise ConflictingWaterMarks

        self._wallet = wallet
        self._desired_level = desired_level     # when making an adjustment the Leveller will attempt to have
                                                # this balance in this wallet
        self._low_water_mark = low_water_mark   # the Leveller will try to respect the LWM provided
                                                # that there are sufficient funds in the suite of wallets
        self._high_water_mark = high_water_mark # the HWM is more of a guide than a hard limit
                                                # even after levelling a balance may exceed the HWM
        self._adjustments = []                  # list of decimal values tentatively adjusting the wallet balance

    @property
    def funds_required(self):
        if self._low_water_mark is None:
            return False
        else:
            return self.adjusted_balance < self._low_water_mark

    @property
    def funds_surplus(self):
        if self._high_water_mark is None:
            return False
        else:
            return self.adjusted_balance > self._high_water_mark

    @property
    def required_funds(self):
        if self._desired_level is not None and self.funds_required:
            return self._desired_level - self.adjusted_balance
        else:
            return Decimal('0.0')

    @property
    def surplus_funds(self):
        """ For information only - not used in computations
        :return:
        """
        if self._desired_level is not None and self.funds_surplus:
            return self.adjusted_balance - self._desired_level
        else:
            return Decimal('0.0')

    def apply_adjustment(self, amount):
        self._adjustments.append(amount)

    @property
    def adjusted_balance(self):
        return sum(self._adjustments) + self._wallet.balance


class _WalletConnection(object):

    def __init__(self, source, destination, weight):
        self._source = source
        self._destination = destination
        self._weight = weight

    def matches(self, other):
        return self._source == other._source and self._destination == other._destination

    def _get_weight_factor(self, input_weights):
        return Decimal(self._weight) / Decimal(input_weights)

    def transfer_permitted(self, input_weights):
        weight_factor = self._get_weight_factor(input_weights)
        return (
            self._destination.funds_required
            and
            (self._destination.required_funds * weight_factor) <= self._source.adjusted_balance
        ) or (
            self._destination.funds_surplus
        )

    def apply_transfer(self, weighted_amount):
        self._source.apply_adjustment(-1 * weighted_amount)
        self._destination.apply_adjustment(weighted_amount)

    def generate_transfer(self, input_weights):
        weight_factor = self._get_weight_factor(input_weights)
        amount = self._destination.required_funds - self._destination.surplus_funds
        weighted_amount = amount * weight_factor
        return _Transfer(self, weighted_amount)


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

    def apply_transfer(self):
        self._connection.apply_transfer(self._amount)

    def execute(self):
        # TODO use wallet to complete the desired transfer
        pass


class Leveller(object):

    # TODO need a wallet to accumulate surplus funds from the whole network
    # this might be just the wallet with the greatest HWM, a designated default,
    # or the root(s) of the network
    # the other end-state is where the balances in all wallets reach zero

    def __init__(self):
        self._wallets = {}
        self._connections = []

    def add_wallet(self, wallet, desired_level, low_water_mark, high_water_mark):
        wallet_registration = _WalletRegistration(wallet, desired_level, low_water_mark, high_water_mark)
        self._wallets[wallet] = wallet_registration
        return wallet_registration

    def connect(self, source, destination, weight=1):
        if source not in self._wallets:
            raise UnknownWallet('Source wallet not registered')
        if destination not in self._wallets:
            raise UnknownWallet('Destination wallet not registered')

        connection = _WalletConnection(self._wallets[source], self._wallets[destination], weight)
        if any(existing_connection.matches(connection) for existing_connection in self._connections):
            raise DuplicateConnection()

        self._connections.append(connection)

        return connection

    def _get_registration(self, wallet):
        registration = self._wallets.get(wallet)
        if registration is None:
            raise UnknownWallet
        return registration

    def required_funds(self, wallet):
        return (self._get_registration(wallet)).required_funds

    def surplus_funds(self, wallet):
        return Decimal('-1.0') * (self._get_registration(wallet)).surplus_funds

    def adjusted_balance(self, wallet):
        return (self._get_registration(wallet)).adjusted_balance

    def proposed_transfers(self):

        def _get_connection(source, destination):
            edge = graph.edge[source][destination]
            return edge['connection']

        graph = self._connection_graph

        # TODO encapsulate and document this logic
        non_root_nodes = [node for node, degree in graph.in_degree().items() if degree > 0]
        sorted_nodes = [node for node in reversed(topological_sort(graph)) if node in non_root_nodes]

        transfers = []
        for destination in sorted_nodes:
            total_weight = 1
            potential_connections = set(
                _get_connection(source, destination)
                for source in graph.predecessors(destination)
            )
            valid_connections = set()
            while potential_connections != valid_connections:
                total_weight = sum(
                    connection._weight
                    for connection in potential_connections
                )
                for connection in potential_connections:
                    if connection.transfer_permitted(total_weight):
                        valid_connections.add(connection)
                    else:
                        potential_connections.remove(connection)
                        valid_connections = set()
                        break

            destination_transfers = [
                connection.generate_transfer(total_weight)
                for connection in valid_connections
            ]

            for transfer in destination_transfers:
                transfer.apply_transfer()
                transfers.append(transfer)

        return transfers

    @property
    def _connection_graph(self):
        dag = DiGraph()
        for connection in self._connections:
            dag.add_edge(connection._source, connection._destination, connection=connection)
        return dag

    @property
    def is_valid_dag(self):
        return is_directed_acyclic_graph(self._connection_graph)
