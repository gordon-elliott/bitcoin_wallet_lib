__copyright__ = 'Copyright(c) Gordon Elliott 2014'

from flask import Flask
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
    return 'Notify daemon {}, changed block {}\n'.format(daemon_id, block_hash)

@app.route('/notify/<int:daemon_id>/wallet/<transaction_id>')
def notify_wallet(daemon_id, transaction_id):
    return 'Notify daemon {}, wallet transaction {}\n'.format(daemon_id, transaction_id)

@app.route('/notify/<int:daemon_id>/alert/<message>')
def notify_alert(daemon_id, message):
    return 'Notify daemon {}, alert message {}\n'.format(daemon_id, message)

if __name__ == '__main__':
    app.run(debug=True)

