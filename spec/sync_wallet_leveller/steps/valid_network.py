__copyright__ = 'Copyright(c) Gordon Elliott 2014'

from behave import given, when, then
from hamcrest import assert_that, equal_to

from wallet_leveller.leveller import NetworkInvalid

@when('the wallets are added to the leveller')
def add_wallets(context):
    pass

@then('the leveller can check that the defined network is valid')
def no_cycles(context):
    valid, errors = context.leveller.is_valid
    assert_that(valid, equal_to(True))

@then('the leveller can spot that the defined network includes cycles')
def cycles_exist(context):
    valid, errors = context.leveller.is_valid
    assert_that(valid, equal_to(False))
    assert_that(errors, equal_to([NetworkInvalid.IsNotDAG]))

@then('the leveller can spot that the defined network has root nodes with a high water mark')
def invalid_roots(context):
    valid, errors = context.leveller.is_valid
    assert_that(valid, equal_to(False))
    assert_that(NetworkInvalid.RootWithHighWaterMark in errors)

@then('the leveller can spot that a duplicate connection between wallets has been specified')
def duplicate_connection(context):
    assert_that(context.connections_correct, equal_to(False))

@then('the leveller can spot that there is a conflict between the watermarks')
def watermark_conflict(context):
    assert_that(context.watermark_conflict, equal_to(True))

@then('the leveller can spot that there is no conflict between the watermarks')
def watermark_no_conflict(context):
    assert_that(context.watermark_conflict, equal_to(False))


