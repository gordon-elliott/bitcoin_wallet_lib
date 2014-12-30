__copyright__ = 'Copyright(c) Gordon Elliott 2014'

#
# To execute
#
# PYTHONPATH=/projects/bitcoin/src:/projects/bitcoin/test:/projects/bitcoin/python-bitcoinrpc-master behave sync_wallet_leveller
#

from behave import given, when, then
from hamcrest import assert_that, equal_to

from test_wallet_leveller.behave_utils import wallet_from_name, create_wallet
from test_wallet_leveller.constants import DEFAULT_ACCOUNT


@given('we have a {wallet_name} wallet with a balance of {balance_amount:Decimal} BTC')
def set_wallet_balance(context, wallet_name, balance_amount):
    wallet = create_wallet(context, wallet_name)
    wallet.move_to_account(
        DEFAULT_ACCOUNT, context.account_names[wallet_name],
        balance_amount - wallet.balance,
        'Priming test wallet'
    )
    assert_that(wallet.balance, equal_to(balance_amount))

@when('we transfer {transfer_amount:Decimal} BTC from {source} to {destination}')
def move_funds(context, transfer_amount, source, destination):
    source_wallet = wallet_from_name(context, source)
    destination_wallet = wallet_from_name(context, destination)

    context.transaction_id, context.fee = source_wallet.transfer_to(destination_wallet, transfer_amount)

@then('the balance in the {wallet_name} wallet will be {expected_balance:Decimal} BTC')
def check_balance(context, wallet_name, expected_balance):
    wallet = wallet_from_name(context, wallet_name)
    assert_that(wallet.balance, equal_to(expected_balance))

@then('the balance in the {wallet_name} wallet will be {expected_balance:Decimal} BTC less the fee')
def check_balance_with_fee(context, wallet_name, expected_balance):
    wallet = wallet_from_name(context, wallet_name)
    assert_that(wallet.balance, equal_to(expected_balance + context.fee))
