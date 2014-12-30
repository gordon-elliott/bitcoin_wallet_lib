__copyright__ = 'Copyright(c) Gordon Elliott 2014'

import parse
import random

from behave import register_type
from decimal import Decimal
from mock import patch

from wallet_leveller.wallet import Wallet

from test_wallet_leveller.mock_auth_service_proxy import MockAuthServiceProxy
from test_wallet_leveller.constants import (
    FEE, ACCOUNT_PATTERN, URI_PATTERN
)


@parse.with_pattern(r"-?\d*\.?\d*")
def parse_decimal(text):
    return Decimal(text)

register_type(Decimal=parse_decimal)


def configure_context(context):
    """ Configure the Behave context for the tests
    :param context: Behave context
    """
    context.feature_uid = random.randint(1, 1000000)

    context.account_names = dict()
    context.wallets = dict()


@patch('wallet_leveller.wallet.AuthServiceProxy', new=MockAuthServiceProxy)
def create_wallet(context, wallet_name):
    """ Create a new wallet with a given name
    :param context: Behave context
    :param wallet_name: Unique wallet name
    :return: newly constructed wallet
    """
    account_name = ACCOUNT_PATTERN.format(wallet_name, context.feature_uid)
    context.account_names[wallet_name] = account_name
    uri = URI_PATTERN.format(random.randint(19001, 19999))
    wallet = Wallet(uri, account_name, FEE)
    context.wallets[wallet_name] = wallet
    return wallet


def wallet_from_name(context, wallet_name):
    """ Find a wallet in the context by name
    :param context: Behave context
    :param wallet_name: Unique wallet name
    :return: wallet from context
    """
    if wallet_name in context.wallets:
        return context.wallets[wallet_name]
    else:
        raise ValueError('Unknown wallet {}'.format(wallet_name))
