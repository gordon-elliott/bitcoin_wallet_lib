__copyright__ = 'Copyright(c) Gordon Elliott 2014'

import random

from mock import patch

from wallet_leveller.wallet import Wallet

from test_wallet_leveller.mock_auth_service_proxy import MockAuthServiceProxy

from test_wallet_leveller.test_wallet_signals import (
    SOURCE_URI,
    DESTINATION_URI,
    SOURCE_ACCOUNT_PATTERN,
    DESTINATION_ACCOUNT_PATTERN,
    FEE
)

def before_all(context):
    # -- SET LOG LEVEL: behave --logging-level=ERROR ...
    # on behave command-line or in "behave.ini".
    context.config.setup_logging()

@patch('wallet_leveller.wallet.AuthServiceProxy', new=MockAuthServiceProxy)
def before_feature(context, feature):
    # each test gets a separate account
    feature_uid = random.randint(1, 1000000)
    context.source_account_name = SOURCE_ACCOUNT_PATTERN.format(feature_uid)
    context.destination_account_name = DESTINATION_ACCOUNT_PATTERN.format(feature_uid)

    context.source = Wallet(SOURCE_URI, context.source_account_name, FEE)
    context.destination = Wallet(DESTINATION_URI, context.destination_account_name, FEE)
