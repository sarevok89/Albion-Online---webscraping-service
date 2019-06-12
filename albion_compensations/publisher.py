import logging
import os

import pika
import pika.exceptions


logger = logging.getLogger(__name__)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)
logger.setLevel(logging.DEBUG)


class Publisher:
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
        self.queue = queue
        if not self._conn or self._conn.is_closed:
            self._conn = pika.BlockingConnection(self._params)
            if not self._channel or self._channel.is_closed:
                self._channel = self._conn.channel()
                self._channel.queue_declare(queue=self.queue, durable=True)
                logger.info("Webscraper connected with RabbitMQ")

    def _publish(self, routing_key, msg):
        self._channel.basic_publish(exchange='',
                                    routing_key=routing_key,
                                    body=msg,
                                    properties=pika.BasicProperties(
                                        delivery_mode=2))
        logger.info('message sent: %s', msg)

    def publish(self, routing_key,  msg):
        """Publish msg, reconnecting if necessary."""

        try:
            self._publish(routing_key, msg)
        except pika.exceptions.ConnectionClosed:
            logger.exception('Reconnecting to queue')
            self.connect(self.queue)
            self._publish(routing_key, msg)
        except pika.exceptions.StreamLostError:
            logger.exception('Reconnecting to queue')
            self.connect(self.queue)
            self._publish(routing_key, msg)
        except pika.exceptions.ChannelWrongStateError:
            logger.exception('Reconnecting to queue')
            self.connect(self.queue)
            self._publish(routing_key, msg)
        except AssertionError:
            logger.exception('Reconnecting to queue')
            self.connect(self.queue)
            self._publish(routing_key, msg)
        except IndexError:
            logger.exception('Reconnecting to queue')
            self.connect(self.queue)
            self._publish(routing_key, msg)
        except Exception as e:
            logger.exception(e)
            self.connect(self.queue)
            self._publish(routing_key, msg)

    def close(self):
        if self._conn and self._conn.is_open:
            logger.info('Closing queue connection')
            self._conn.close()
