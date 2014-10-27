__copyright__ = 'Copyright(c) Gordon Elliott 2014'

import logging
import unittest
import time

from collections import defaultdict
from multiprocessing import Process, Queue

from event_api.push_pull import Listener, announce


def server(port, topic, message_text):
    time.sleep(1)
    announce(port, str(topic), message_text)


class PushPullTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.INFO)

    def _distribute_and_collate(self, client, server, messages, registrations, client_port):
        result_queue = Queue()
        client_process = Process(target=client, args=(client_port, result_queue, registrations))
        client_process.daemon = True
        client_process.start()

        for topic, msg_text in messages:
            server_process = Process(target=server, args=(client_port, topic, msg_text))
            server_process.daemon = True
            server_process.start()

        results = []
        result = result_queue.get()
        while result is not None:
            if isinstance(result, Exception):
                raise result
            else:
                results.append(result)

            result = result_queue.get()

        return results

    def test_multiple_publishers_one_subscriber(self):
        """ Confirm behaviour of multiple publishers and one subscriber
        """

        def client(port, result_queue, registrations):
            def callback(cb_topic, cb_message_data, cb_associated_data):
                self.assertIn(int(cb_topic), registrations)
                expected_message, data = registrations[int(cb_topic)]
                self.assertEqual(expected_message, cb_message_data)
                self.assertEqual(data, cb_associated_data)

                return True, (int(cb_topic), cb_message_data)

            listener = Listener(port)
            try:
                for topic, (_, data) in iter(registrations.items()):
                    listener.register(str(topic), callback, data)

                for result in listener.listen():
                    result_queue.put(result)
            except Exception as ex:
                result_queue.put(ex)

            result_queue.put(None)

        messages = [
            (9827, 'first message', ),
            (9829, 'second message', ),
            (9831, 'last message', ),
        ]
        registrations = {
            9827: ('first message', {'exdata': 654}),
            9829: ('second message', {'exdata': 873}),
            9831: ('last message', {'exdata': 298}),
        }

        actual = self._distribute_and_collate(client, server, messages, registrations, client_port=5561)

        self.assertEqual(set(messages), set(actual))

    def test_multiple_messages_per_listener(self):
        """ Test that different messages for the same topic can be processed
        """

        def client(port, result_queue, registrations):
            topic_messages = defaultdict(set)

            def callback(cb_topic, cb_message_data, cb_associated_data):
                topic =  int(cb_topic)
                topic_messages[topic].add(cb_message_data)
                return len(topic_messages[topic]) >= 2, (topic, cb_message_data)

            listener = Listener(port)
            try:
                for topic, (_, data) in iter(registrations.items()):
                    listener.register(str(topic), callback, data)

                for result in listener.listen():
                    pass

                for topic, messages in iter(topic_messages.items()):
                    topic_name, ex_data = registrations[topic]
                    result_queue.put((topic, (topic_name, ex_data, messages)))

            except Exception as ex:
                result_queue.put(ex)

            result_queue.put(None)

        messages = [
            (9827, 'first message'),
            (9829, 'second message'),
            (9829, 'third message'), # a second message on the second topic
            (9828, 'forth message'), # unknown topic
            (9827, 'fifth message')  # a second message on the first topic
        ]
        registrations = {
            9827: ('topic 0', {'exdata': 654}),
            9829: ('topic 1', {'exdata': 873}),
        }
        expected = {
            9827: ('topic 0', {'exdata': 654}, {'first message', 'fifth message'}),
            9829: ('topic 1', {'exdata': 873}, {'second message', 'third message'}),
        }

        actual = self._distribute_and_collate(client, server, messages, registrations, client_port=5562)

        self.assertEqual(expected, dict(actual))

    def test_filter_messages(self):
        """ Test that all messages matching a filter are returned but no other messages are processed
        """

        def client(port, result_queue, registrations):

            def callback(cb_topic, cb_message_data, cb_associated_data):
                topic =  int(cb_topic)
                return cb_message_data == 'match filter', (topic, cb_message_data)

            listener = Listener(port)
            try:
                for topic, (_, data) in iter(registrations.items()):
                    listener.register(str(topic), callback, data)

                for result in listener.listen():
                    result_queue.put(result)

            except Exception as ex:
                result_queue.put(ex)

            result_queue.put(None)

        messages = [
            (9827, 'miss filter'),  # not recorded
            (9829, 'match filter'), # returned
            (9829, 'match filter'), # a second message on the second topic
            (9828, 'miss filter'),  # unknown topic
            (9827, 'match filter')  # a second message on the first topic, matches this time
        ]
        registrations = {
            9827: ('topic 0', {'exdata': 654}),
            9829: ('topic 1', {'exdata': 873}),
        }
        expected = {
            9827: ('match filter'),
            9829: ('match filter'),
        }

        actual = self._distribute_and_collate(client, server, messages, registrations, client_port=5563)

        self.assertEqual(expected, dict(actual))
