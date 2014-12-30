__copyright__ = 'Copyright(c) Gordon Elliott 2014'

#
# To execute
#
# PYTHONPATH=/projects/bitcoin/src:/projects/bitcoin/test:/projects/bitcoin/python-bitcoinrpc-master behave async_wallet_leveller
#
import parse

from behave import register_type, given, when, then
from hamcrest import assert_that, equal_to

from decimal import Decimal

from test_wallet_leveller.constants import (
    SOURCE_DEFAULT_ACCOUNT,
    DESTINATION_DEFAULT_ACCOUNT
)
from test_wallet_leveller.test_wallet_signals import (
    check_async
)


@parse.with_pattern(r"\d*\.?\d*")
def parse_decimal(text):
    return Decimal(text)

register_type(Decimal=parse_decimal)

def wallet_from_name(context, wallet_name):
    if wallet_name == 'source':
        wallet = context.source
    elif wallet_name == 'destination':
        wallet = context.destination
    else:
        raise ValueError('Unknown wallet {}'.format(wallet_name))
    return wallet

def _transaction_confirmed(context, transaction_id):
    return context.destination.find_transaction(transaction_id) and context.source.find_transaction(transaction_id)

def _wrap_with_confirmation(context, test_function):
    def wrapped(cb_transaction_id, cb_message_data, cb_associated_data):
        if _transaction_confirmed(context, cb_transaction_id):
            test_function(cb_transaction_id, cb_message_data, cb_associated_data)

            return True, True
        else:
            return False, None

    return wrapped

def no_op(cb_transaction_id, cb_message_data, cb_associated_data):
    pass

@given('we have a source wallet with a balance of {balance_amount:Decimal} BTC')
def set_source_balance(context, balance_amount):
    context.source.move_to_account(
        SOURCE_DEFAULT_ACCOUNT, context.source_account_name,
        balance_amount - context.source.balance,
        'Priming source test account'
    )
    assert_that(context.source.balance, equal_to(balance_amount))

@given('we have a destination wallet with a balance of {balance_amount:Decimal} BTC')
def set_destination_balance(context, balance_amount):
    context.destination.move_to_account(
        DESTINATION_DEFAULT_ACCOUNT, context.destination_account_name,
        balance_amount - context.destination.balance,
        'Priming destination test account'
    )
    assert_that(context.destination.balance, equal_to(balance_amount))

@when('we transfer {transfer_amount:Decimal} BTC from {source} to {destination}')
def move_funds(context, transfer_amount, source, destination):
    source_wallet = wallet_from_name(context, source)
    destination_wallet = wallet_from_name(context, destination)

    context.transaction_id, context.fee = source_wallet.transfer_to(destination_wallet, transfer_amount)

    check_async({
        context.transaction_id: _wrap_with_confirmation(context, no_op),
    })


@then('the balance in the {wallet_name} wallet will be {expected_balance:Decimal} BTC')
def check_balance(context, wallet_name, expected_balance):
    wallet = wallet_from_name(context, wallet_name)
    assert_that(wallet.balance, equal_to(expected_balance))

@then('the balance in the {wallet_name} wallet will be {expected_balance:Decimal} BTC less the fee')
def check_balance_with_fee(context, wallet_name, expected_balance):
    wallet = wallet_from_name(context, wallet_name)
    assert_that(wallet.balance, equal_to(expected_balance + context.fee))
