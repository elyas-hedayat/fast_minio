import pika
import json

from fastapi import FastAPI
from minio import Minio
from minio.commonconfig import CopySource

app = FastAPI()

minio_client = Minio(endpoint="192.168.23.49:9000", access_key="fB7tN1WMnkAPzciqkPOG",
                     secret_key="WxzjBKitDBoBViQLpEhx4LywKyj20PKVxWtwpWJM", secure=False)

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
channel.queue_declare(queue="MinIO")


def on_request(ch, method, props, body):
    data = json.loads(body)
    source_exists = minio_client.bucket_exists(data['source_bucket'])
    destination_exists = minio_client.bucket_exists(data['destination_bucket'])

    if not (source_exists and destination_exists):
        return {"detail": "Source or destination bucket does not exist"}
    for item in data['file_list']:
        minio_client.copy_object(
            data['destination_bucket'],
            item,
            CopySource(data['source_bucket'], item)  # source bucket/object
        )
        minio_client.remove_object(data['source_bucket'], item)
    ch.basic_ack(delivery_tag=method.delivery_tag, multiple=True)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="MinIO", on_message_callback=on_request)
channel.start_consuming()
