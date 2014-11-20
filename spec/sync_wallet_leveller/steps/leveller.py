__copyright__ = 'Copyright(c) Gordon Elliott 2014'

from behave import given, when, then
from hamcrest import assert_that, equal_to

from wallet_leveller.leveller import Leveller
from test_wallet_leveller.common import wallet_from_name


@given('we have a leveller')
def create_leveller(context):
    context.leveller = Leveller()

@given('we add the {wallet_name} wallet to the leveller specifying a {low_water_mark:Decimal} BTC low water mark')
def add_wallet(context, wallet_name, low_water_mark):
    wallet = wallet_from_name(context, wallet_name)
    context.leveller.add_wallet(wallet, low_water_mark)

@given('we connect the {source} wallet to the {destination} wallet specifying a link weight of 1')
def connect_wallets(context, source, destination):
    source_wallet = wallet_from_name(context, source)
    destination_wallet = wallet_from_name(context, destination)

    context.leveller.connect(source_wallet, destination_wallet)

@when('we ask the leveller')
def ask_the_leveller(context):
    # no-op
    pass

@when('the leveller moves {transfer_amount:Decimal} BTC from the {source} wallet to the {destination} wallet')
def leveller_moves_funds(context, transfer_amount, source, destination):
    source_wallet = wallet_from_name(context, source)
    destination_wallet = wallet_from_name(context, destination)

    context.transaction_id, context.fee = source_wallet.transfer_to(destination_wallet, transfer_amount)

@then('the leveller can identify that the {wallet_name} wallet additionally requires {additional_amount:Decimal} BTC')
def required_funds(context, wallet_name, additional_amount):
    wallet = wallet_from_name(context, wallet_name)
    required = context.leveller.required_funds(wallet)

    assert_that(additional_amount, equal_to(required))

@then('the leveller will identify that {transfer_amount:Decimal} BTC needs to be moved from the {source} wallet to the {destination} wallet')
def proposed_transfers(context, transfer_amount, source, destination):
    assert False
