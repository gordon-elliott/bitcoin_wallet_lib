__copyright__ = 'Copyright(c) Gordon Elliott 2014'

from behave import given, when, then
from hamcrest import assert_that, equal_to


@when('the wallets are added to the leveller')
def add_wallets(context):
    pass

@then('the leveller can check that the defined network has no cycles')
def no_cycles(context):
    assert_that(context.leveller.is_valid_dag, equal_to(True))

@then('the leveller can spot that the defined network includes cycles')
def cycles_exist(context):
    assert_that(context.leveller.is_valid_dag, equal_to(False))
