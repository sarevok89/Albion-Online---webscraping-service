import django
import json
import logging
import os
import signal
import sys

import boto3
import pika
import pika.exceptions

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "albion_compensations.settings")

django.setup()

from albion_compensations.settings import BASE_DIR

chromedriver_path = os.path.join(
    BASE_DIR, 'webscraper', 'static', 'webscraper', 'chromedriver')
if chromedriver_path not in sys.path:
    sys.path.append(chromedriver_path)


from django.contrib.auth.models import User

from webscraper.models import Killboard
from albion_compensations.settings import MEDIA_ROOT, MEDIA_S3_URL
from webscraper.killboard_app import create_table, \
    create_kill_id_list, generate_excel


logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


class Worker:
    """
    Worker class used to manage everything within worker script. Worker object
    can create new connection

    """
    TYPE = 'direct'

    def __init__(self):
        self._params = pika.URLParameters(
            f"amqp://{os.environ.get('RABBITMQ_USER')}:"
            f"{os.environ.get('RABBITMQ_PASSWORD')}@"
            f"{os.environ.get('RABBITMQ_HOST')}:"
            f"{os.environ.get('RABBITMQ_PORT')}/"
            f"{os.environ.get('RABBITMQ_VHOST')}"
            f"?connection_attempts=5"
            f"&blocked_connection_timeout=5&")
        self._conn = None
        self._channel = None

    def connect(self, queue):
        """
        Method checking if our Worker object is connected with RabbitMQ server.
        If not it connects to RabbitMQ, opens new channel and declares new
        queue.

        """
        self.QUEUE = queue
        if not self._conn or self._conn.is_closed:
            self._conn = pika.BlockingConnection(self._params)
            self._channel = self._conn.channel()
            self._channel.queue_declare(queue=self.QUEUE, durable=True)
            logger.info("Worker connected with RabbitMQ")

    def _consume(self):
        self._channel.basic_qos(prefetch_count=1)
        self._channel.basic_consume(queue=self.QUEUE,
                                    on_message_callback=self.callback)
        self._channel.start_consuming()
        logger.debug('[x] Received new task')

    def consume(self):
        """
        Wrapping method to `_consume` method. In case of ConnectionClosed, or
        StreamLostError it first reconnects before calling `_consume` method.

        """
        while True:
            try:
                self._consume()
            except pika.exceptions.ConnectionClosed:
                logger.exception('Reconnecting to queue')
                self.connect(self.QUEUE)
                self._consume()
            except pika.exceptions.StreamLostError:
                logger.exception('Reconnecting to queue')
                self.connect(self.QUEUE)
                self._consume()
            except Exception as e:
                logger.exception(e)

    def on_signal_connection_closing(self, signum, stack):
        """
        Method for closing connection and channel on signal.

        """
        self._channel.close()
        self._conn.close()
        logger.info(
            f'Closed connection on signal - {signal.Signals(signum).name} '
            f'({signum})')
        sys.exit()

    def callback(self, ch, method, properties, body):
        worker.connect(self.QUEUE)
        logger.info("[x] Received new task!")
        body = json.loads(body)
        text = body.get('text')
        fight_name = body.get('fight_name')
        username = body.get('user')

        try:
            kill_id_list = create_kill_id_list(text)
            dict_list = create_table(kill_id_list)
            file_name = generate_excel(dict_list, fight_name)

            obj = Killboard()
            obj.fight_name = fight_name
            obj.user = User.objects.get(username=username)

            temp_file = os.path.join(MEDIA_ROOT, 'compensations', file_name)

            s3 = boto3.resource('s3')
            s3.meta.client.upload_file(
                temp_file,
                'albion-compensations',
                'media/compensations/' + file_name)

            obj.excel_file = MEDIA_S3_URL + 'compensations/' + file_name
            obj.save()

        except Exception as e:
            logger.exception(e)

        ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    worker = Worker()
    worker.connect('webscraper')
    signal.signal(signal.SIGTERM, worker.on_signal_connection_closing)
    signal.signal(signal.SIGINT, worker.on_signal_connection_closing)

    worker.consume()
