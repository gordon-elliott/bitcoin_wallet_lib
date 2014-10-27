__copyright__ = 'Copyright(c) Gordon Elliott 2014'

import logging
import zmq

from event_api.constants import ZMQ_MESSAGE_ENCODING

LOG = logging.getLogger(__name__)

DEFAULT_PORT = 5556
DEFAULT_MESSAGE_SEPARATOR = ','


class Publisher(object):

    def __init__(self, port=DEFAULT_PORT, message_separator=DEFAULT_MESSAGE_SEPARATOR):
        self._message_separator = message_separator
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind("tcp://*:{0}".format(port))
        LOG.info("Publisher started on port %d", port)

    def send(self, topic, message_data):
        # 0MQ requires that a byte sequence be transmitted
        self.socket.send(bytes("{0}{1}{2}".format(topic, self._message_separator, message_data), ZMQ_MESSAGE_ENCODING))
        LOG.info("Publisher sent %s with topic %s", message_data, topic)


def subscribe(ports, topic_filter, associated_data, callback, message_separator=DEFAULT_MESSAGE_SEPARATOR):

    # Socket to talk to server
    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    for port in ports:
        socket.connect("tcp://localhost:{0}".format(port))

    LOG.info("Subscriber collecting messages for %s from ports %r", topic_filter, ports)

    socket.setsockopt(zmq.SUBSCRIBE, bytes(topic_filter, ZMQ_MESSAGE_ENCODING))

    raw_data = socket.recv()
    # decode byte sequence into a (unicode) string
    topic, message_data = raw_data.decode().split(message_separator)
    LOG.info("Subscriber received topic: %s, message_data: %s", topic, message_data)

    return callback(topic, message_data, associated_data)

