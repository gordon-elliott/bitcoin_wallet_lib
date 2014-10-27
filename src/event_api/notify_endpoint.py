__copyright__ = 'Copyright(c) Gordon Elliott 2014'

import logging

from flask import Flask

from event_api.signals import block_publisher, transaction_publisher, alert_publisher, LISTENER_PORT
from event_api.push_pull import announce


LOG = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/')
def index():
    return 'bitcoind notifier'

"""
 -blocknotify=<cmd>     Execute command when the best block changes (%s in cmd is replaced by block hash)
 -walletnotify=<cmd>    Execute command when a wallet transaction changes (%s in cmd is replaced by TxID)
 -alertnotify=<cmd>     Execute command when a relevant alert is received (%s in cmd is replaced by message)
"""

@app.route('/notify/<int:daemon_id>/block/<block_hash>')
def notify_block(daemon_id, block_hash):
    block_publisher.send(app, daemon_id=daemon_id, block_hash=block_hash)
    return 'Notify daemon {}, changed block {}\n'.format(daemon_id, block_hash)

@app.route('/notify/<int:daemon_id>/wallet/<transaction_id>')
def notify_wallet(daemon_id, transaction_id):
    transaction_publisher.send(app, daemon_id=daemon_id, transaction_id=transaction_id)
    return 'Notify daemon {}, wallet transaction {}\n'.format(daemon_id, transaction_id)

@app.route('/notify/<int:daemon_id>/alert/<message>')
def notify_alert(daemon_id, message):
    alert_publisher.send(app, daemon_id=daemon_id, message='{0}'.format(message))
    return 'Notify daemon {}, alert message {}\n'.format(daemon_id, message)


# @transaction_publisher.connect_via(app)
# def transaction_logger(sender, daemon_id, transaction_id, **extra):
#     LOG.info("Transaction from %r, daemon %r, transaction %r", sender, daemon_id, transaction_id)
#
@transaction_publisher.connect_via(app)
def transaction_announcer(sender, daemon_id, transaction_id, **extra):
    announce(LISTENER_PORT, transaction_id, daemon_id)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)

