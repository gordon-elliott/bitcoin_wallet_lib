__copyright__ = 'Copyright(c) Gordon Elliott 2014'

import logging
import unittest
import time

from multiprocessing import Process, Queue

from event_api.pub_sub import Publisher, subscribe


class PubSubTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.INFO)

    def test_one_publisher_one_subscriber(self):
        server_port = 5559
        client_data = {'data': 93839}
        topic = 9399827
        message_data = '<message sent>'

        def server(port):
            srv = Publisher(port)

            time.sleep(1)
            srv.send(str(topic - 1), 'some payload')
            time.sleep(1)
            srv.send(str(topic), message_data)  # topic we are interested in
            time.sleep(1)
            srv.send(str(topic + 1), 'another payload')
            time.sleep(1)

        def client(ports, result_queue, topic_filter, associated_data):
            def callback(cb_topic, cb_message_data, cb_associated_data):
                self.assertEqual(str(topic), cb_topic)
                self.assertEqual(message_data, cb_message_data)
                self.assertEqual(client_data, cb_associated_data)

            try:
                result = subscribe(ports, topic_filter, associated_data, callback)
            except Exception as ex:
                result = ex

            result_queue.put(result)

        Process(target=server, args=(server_port,)).start()

        result_queue = Queue()
        Process(target=client, args=([server_port], result_queue, str(topic), client_data)).start()

        result = result_queue.get()
        if isinstance(result, Exception):
            raise result

    def test_one_publisher_multiple_subscribers(self):
        server_port = 5560

        fixtures = {
            9399827: ('first message', {'data': 93839}),
            9399829: ('second message', {'data': 93838}),
            9399831: ('last message', {'data': 93837}),
        }

        def server(port):
            srv = Publisher(port)

            time.sleep(1)
            srv.send('77777', 'some payload')
            time.sleep(1)
            for topic, fixture in iter(fixtures.items()):
                srv.send(str(topic), fixture[0])  # topics we are interested in
                time.sleep(1)
            srv.send('88888', 'another payload')
            time.sleep(1)

        def client(ports, result_queue, topic_filter, associated_data):
            def callback(cb_topic, cb_message_data, cb_associated_data):
                self.assertIn(int(cb_topic), fixtures)
                fixture = fixtures[int(cb_topic)]
                self.assertEqual(fixture[0], cb_message_data)
                self.assertEqual(fixture[1], cb_associated_data)

            try:
                result = subscribe(ports, topic_filter, associated_data, callback)
            except Exception as ex:
                result = ex

            result_queue.put(result)

        Process(target=server, args=(server_port,)).start()

        result_queue = Queue()
        for topic, fixture in iter(fixtures.items()):
            Process(target=client, args=([server_port], result_queue, str(topic), fixture[1])).start()

        for _ in fixtures:
            result = result_queue.get()
            if isinstance(result, Exception):
                raise result
