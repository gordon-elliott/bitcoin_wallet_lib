__copyright__ = 'Copyright(c) Gordon Elliott 2014'

from event_api.pub_sub import Publisher


BLOCK_NOTIFIER_PORT = 55540
TRANSACTION_NOTIFIER_PORT = 55541
ALERT_NOTIFIER_PORT = 55542

block_publisher = Publisher(BLOCK_NOTIFIER_PORT)
transaction_publisher = Publisher(TRANSACTION_NOTIFIER_PORT)
alert_publisher = Publisher(ALERT_NOTIFIER_PORT)
