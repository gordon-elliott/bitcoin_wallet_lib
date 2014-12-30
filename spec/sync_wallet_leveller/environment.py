__copyright__ = 'Copyright(c) Gordon Elliott 2014'

from test_wallet_leveller.behave_utils import configure_context


def before_all(context):
    # -- SET LOG LEVEL: behave --logging-level=ERROR ...
    # on behave command-line or in "behave.ini".
    context.config.setup_logging()


def before_feature(context, feature):
    # each test gets a separate account
    configure_context(context)
