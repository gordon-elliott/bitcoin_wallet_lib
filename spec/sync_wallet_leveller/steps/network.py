__copyright__ = 'Copyright(c) Gordon Elliott 2014'

from decimal import Decimal

from behave import given, when, then
from hamcrest import assert_that, equal_to

from test_wallet_leveller.behave_utils import wallet_from_name, create_wallet
from test_wallet_leveller.constants import DEFAULT_ACCOUNT


@given('a suite of wallets')
def wallet_list(context):
    for row in context.table:
        wallet_name = row['name']
        wallet = create_wallet(context, wallet_name)
        balance = Decimal(row['balance'])
        wallet.move_to_account(
            DEFAULT_ACCOUNT, context.account_names[wallet_name],
            balance - wallet.balance,
            'Priming test wallet'
        )
        desired = Decimal(row['desired']) if row['desired'] else None
        lwm = Decimal(row['lwm']) if row['lwm'] else None
        hwm = Decimal(row['hwm']) if row['hwm'] else None
        context.leveller.add_wallet(wallet, desired, lwm, hwm)

@given('the wallets are connected thus')
def connection_list(context):
    for row in context.table:
        source_wallet = wallet_from_name(context, row['source'])
        destination_wallet = wallet_from_name(context, row['destination'])

        context.leveller.connect(source_wallet, destination_wallet, row['weight'])

@when('the funds in {modified_wallet} are adjusted by {payment_amount:Decimal} BTC')
def introduce_funds(context, modified_wallet, payment_amount):
    wallet = wallet_from_name(context, modified_wallet)
    wallet.move_to_account(
        DEFAULT_ACCOUNT, context.account_names[modified_wallet],
        payment_amount,
        'Payment to/from test wallet'
    )

@then('the leveller finds no funds need to be moved')
def no_transfers(context):
    transfers = list(context.leveller.proposed_transfers())

    assert_that(len(transfers), equal_to(0), 'Transfers found where none were expected')

@then('the leveller will identify that the following transfers are required')
def sequence_of_transfers(context):
    expected_transfers = {
        (
            wallet_from_name(context, row['source']),
            wallet_from_name(context, row['destination']),
            Decimal(row['amount'])
        )
        for row in context.table
    }

    actual_transfers = {
        (
            transfer.source,
            transfer.destination,
            transfer.amount
        )
        for transfer in context.leveller.proposed_transfers()
    }

    assert_that(actual_transfers, equal_to(expected_transfers))

@then('the adjusted balance in the {wallet_name} wallet will be {adjusted_balance:Decimal} BTC')
def check_balance(context, wallet_name, adjusted_balance):
    wallet = wallet_from_name(context, wallet_name)
    assert_that(context.leveller.adjusted_balance(wallet), equal_to(adjusted_balance))

