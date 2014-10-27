__copyright__ = 'Copyright(c) Gordon Elliott 2014'

from blinker import Namespace


LISTENER_PORT = 6501


notification_signals = Namespace()

block_publisher = notification_signals.signal('block')
transaction_publisher = notification_signals.signal('transaction')
alert_publisher = notification_signals.signal('alert')
