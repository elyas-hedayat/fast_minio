import binascii
import os
from minio import Minio

minio_client = Minio(endpoint="192.168.23.49:9000", access_key="fB7tN1WMnkAPzciqkPOG",
                     secret_key="WxzjBKitDBoBViQLpEhx4LywKyj20PKVxWtwpWJM", secure=False)


def _generate_code():
    return binascii.hexlify(os.urandom(20)).decode('utf-8')
