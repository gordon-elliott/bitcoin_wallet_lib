__copyright__ = 'Copyright(c) Gordon Elliott 2014'

import logging
import zmq

from collections import defaultdict

from event_api.constants import ZMQ_MESSAGE_ENCODING

LOG = logging.getLogger(__name__)

DEFAULT_PORT = 5557
DEFAULT_MESSAGE_SEPARATOR = ','


class Listener(object):

    def __init__(self, port=DEFAULT_PORT, message_separator=DEFAULT_MESSAGE_SEPARATOR):
        self._port = port
        self._message_separator = message_separator
        self._callbacks_by_topic = {}

    def register(self, topic, callback, associated_data):
        LOG.info("Callback registered for %s", topic)
        self._callbacks_by_topic[topic] = (callback, associated_data)

    def listen(self):
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind("tcp://*:{0}".format(self._port))
        LOG.info("Listening on port %d", self._port)

        callback_complete = defaultdict(bool)
        while(not all(
            callback_complete[topic]
            for topic in self._callbacks_by_topic
        )):
            raw_data = socket.recv()

            # raw bytes need to be decoded to a (unicode) string for processing
            topic, message_data = raw_data.decode().split(self._message_separator)

            if topic in self._callbacks_by_topic:
                LOG.info("Subscriber received topic: %s, message_data: %s", topic, message_data)

                callback, associated_data = self._callbacks_by_topic[topic]

                complete, result = callback(topic, message_data, associated_data)
                callback_complete[topic] = callback_complete[topic] or complete

                if complete:
                    yield result



def announce(port, topic, message_data, message_separator=DEFAULT_MESSAGE_SEPARATOR):

    # Socket to talk to client
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect("tcp://localhost:{0}".format(port))

    # 0MQ requires that the payload be a byte sequence
    socket.send(bytes(u"{0}{1}{2}".format(topic, message_separator, message_data), ZMQ_MESSAGE_ENCODING))

    LOG.info("Publisher sent %s with topic %s to port %r", message_data, topic, port)
