import binascii
import io
import os
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from minio import Minio
from minio.commonconfig import CopySource

app = FastAPI()

minio_client = Minio(endpoint="192.168.23.49:9000", access_key="fB7tN1WMnkAPzciqkPOG",
                     secret_key="WxzjBKitDBoBViQLpEhx4LywKyj20PKVxWtwpWJM", secure=False)


def _generate_code():
    return binascii.hexlify(os.urandom(20)).decode('utf-8')


# Bucket actions
@app.post("/make_bucket")
def make_bucket(bucket_name: str):
    try:
        minio_client.make_bucket(bucket_name=bucket_name)
        return {"message": "Bucket created"}
    except Exception as e:
        return {"message": str(e)}


@app.get("/list_buckets")
def list_buckets():
    buckets = minio_client.list_buckets()
    return {"buckets": buckets}


@app.get("/bucket_exists")
def bucket_exists(bucket_name: str):
    return {"exists": minio_client.bucket_exists(bucket_name)}


@app.delete("/remove_bucket")
def remove_bucket(bucket_name: str):
    try:
        minio_client.remove_bucket(bucket_name)
        return {"message": "Bucket removed"}
    except Exception as e:
        return {"message": str(e)}


# Object actions
@app.get("/list_objects")
def list_objects(bucket_name: str):
    objects = minio_client.list_objects(bucket_name=bucket_name)
    return {"objects": objects}


@app.get("/get_object")
def get_object(bucket_name: str, object_name: str):
    try:
        response = minio_client.get_object(bucket_name=bucket_name, object_name=object_name)
        return {"message": response.url}
    except Exception as e:
        return {"message": str(e)}


# set_object_tags(bucket_name, object_name, tags, version_id=None)


@app.put("/put_object")
def put_object(bucket_name: str, object_name: str, file: bytes = File(...)):
    length = minio_client.put_object(bucket_name=bucket_name, object_name=object_name, data=file, length=-1)
    return {"length": length}


@app.post("/fput_object")
async def fput_object(bucket_name: str, object_name: str, file: UploadFile = File(...)):
    try:
        object_id = _generate_code()
        user_metadata = {
            "owner_id": "test",
            "object_id": object_id,
        }
        file_object = await file.read()
        response = minio_client.put_object(bucket_name, object_id, io.BytesIO(file_object), length=-1,
                                           part_size=10 * 1024 * 1024, metadata=user_metadata, )
        return {"message": response.object_name}
    except Exception as e:
        return {"message": str(e)}


# Other actions
@app.post("/remove_object")
def remove_object(bucket_name: str, object_name: str):
    minio_client.remove_object(bucket_name, object_name)
    return {"message": "Object removed"}


@app.post("/transfer_bucket")
def transfer_bucket(source_bucket: str, destination_bucket: str, object_list: List[str]):
    source_exists = minio_client.bucket_exists(source_bucket)
    destination_exists = minio_client.bucket_exists(destination_bucket)

    if not (source_exists and destination_exists):
        return {"detail": "Source or destination bucket does not exist"}
    try:
        for item in object_list:
            minio_client.copy_object(
                destination_bucket,
                item,
                CopySource(source_bucket, item)  # source bucket/object
            )
            minio_client.remove_object(source_bucket, item)
        return {"message": "Objects copied successfully and removed from temp bucket."}
    except Exception as e:
        return {"message": str(e)}


# @app.post("/transfer_bucket")
# def transfer_bucket(source_bucket: str, destination_bucket: str, object_list: List[str]):
#     source_exists = minio_client.bucket_exists(source_bucket)
#     print(source_exists)
#     destination_exists = minio_client.bucket_exists(destination_bucket)
#     print(destination_exists)
#     if not (source_exists and destination_exists):
#         return {"status_code": 404, "detail": "Item not found"}
#     # for item in object_list:
#     #     minio_client.copy_object(
#     #         destination_bucket,
#     #         item.object_name,
#     #         CopySource(destination_bucket, item),
#     #     )
#     return {"message": "item copied"}


@app.get("/presigned_get_object")
def presigned_get_object(bucket_name: str, object_name: str):
    url = minio_client.presigned_get_object(bucket_name, object_name)
    return {"url": url}
