import os
import sys

import pika
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils import status
from utils.utils import copy_and_delete_files

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="192.168.23.49",
        port=5672,
        credentials=pika.PlainCredentials(
            "admin", "admin"
        ),
    )
)
channel = connection.channel()
channel.queue_declare(queue="MinIO", durable=True, arguments={'x-message-ttl': 20000})


def handle_minio_request(ch, method, proper, body):
    try:
        request_data = json.loads(body)
        copy_and_delete_files(
            file_list=request_data['file_list'],
            source_bucket=request_data['source_bucket'],
            destination_bucket=request_data['destination_bucket']
        )
        response = {"status_code": status.HTTP_SUCCESS}
    except Exception as e:
        response = {"status_code": status.HTTP_ERROR}

    ch.basic_publish(exchange='', routing_key=proper.reply_to,
                     properties=pika.BasicProperties(correlation_id=proper.correlation_id),
                     body=json.dumps(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="MinIO", on_message_callback=handle_minio_request)
channel.start_consuming()
