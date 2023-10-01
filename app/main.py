import binascii
import io
import os
from typing import List

import strawberry
from fastapi import FastAPI, UploadFile, File, HTTPException
from minio import Minio
from minio.commonconfig import CopySource
from strawberry.asgi import GraphQL
from strawberry.schema import Schema
from strawberry.types import Info
from typing import Optional
from strawberry.file_uploads import Upload

minio_client = Minio(endpoint="192.168.23.49:9000", access_key="fB7tN1WMnkAPzciqkPOG",
                     secret_key="WxzjBKitDBoBViQLpEhx4LywKyj20PKVxWtwpWJM", secure=False)


def _generate_code():
    return binascii.hexlify(os.urandom(20)).decode('utf-8')


@strawberry.type
class Message:
    message: str
    status_code: int


@strawberry.input
class BucketInput:
    name: str


@strawberry.input
class FileTransferInput:
    source_bucket: str
    destination_bucket: str
    object_list: List[str]


@strawberry.input
class FileRemoveInput:
    bucket_name: str
    object_name: str


@strawberry.type
class Query:
    @strawberry.field
    async def make_bucket(self, info: Info, bucket_name: str) -> Optional[Message]:
        try:
            minio_client.make_bucket(bucket_name=bucket_name)
            return Message(message="Bucket created", status_code=1200
                           )
        except Exception as e:
            return Message(message=str(e), status_code=1400)

    @strawberry.field
    async def bucket_exists(self, info: Info, bucket_name: str) -> Optional[Message]:
        bucket_exist = minio_client.bucket_exists(bucket_name)
        return Message(message=bucket_exist, status_code=1200)

    @strawberry.field
    async def list_buckets(self, info: Info) -> Optional[Message]:
        buckets = minio_client.list_buckets()
        return Message(message=buckets, status_code=1200)

    @strawberry.field
    async def list_objects(self, info: Info, bucket_name: str) -> Optional[Message]:
        objects = minio_client.list_objects(bucket_name=bucket_name)
        return Message(message=objects, status_code=1200)

    @strawberry.field
    def get_object(self, info: Info, bucket_name: str, object_name: str) -> Optional[Message]:
        try:
            response = minio_client.get_object(bucket_name=bucket_name, object_name=object_name)
            return Message(message=response.url, status_code=1200)
        except Exception as e:
            return Message(message=str(e), status_code=1400)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def remove_bucket(self, info: Info, input: BucketInput) -> Optional[Message]:
        try:
            minio_client.remove_bucket(input.name)
            return Message(message="Bucket removed", status_code=1200)
        except Exception as e:
            return Message(message=str(e), status_code=1400)

    @strawberry.mutation
    async def fput_object(self, info: Info, bucket_name: str, file: Upload) -> Optional[Message]:
        try:
            object_id = _generate_code()
            user_metadata = {
                "owner_id": "test",
                "object_id": object_id,
            }
            file_object = await file.read()
            response = minio_client.put_object(bucket_name, object_id, io.BytesIO(file_object), length=-1,
                                               part_size=10 * 1024 * 1024, metadata=user_metadata, )
            return Message(message=response.object_name, status_code=1200)
        except Exception as e:
            return Message(message=str(e), status_code=1400)

    @strawberry.mutation
    async def transfer_bucket(self, info: Info, input: FileTransferInput) -> Optional[Message]:
        source_exists = minio_client.bucket_exists(input.source_bucket)
        destination_exists = minio_client.bucket_exists(input.destination_bucket)

        if not (source_exists and destination_exists):
            return Message(detail="Source or destination bucket does not exist")
        try:
            for item in input.object_list:
                minio_client.copy_object(
                    input.destination_bucket,
                    item,
                    CopySource(input.source_bucket, item)  # source bucket/object
                )
                minio_client.remove_object(input.source_bucket, item)
            return Message(message="Objects copied successfully and removed from temp bucket.", status_code=1200)
        except Exception as e:
            return Message(message=str(e), status_code=1400)

    @strawberry.mutation
    async def remove_object(self, info: Info, input: FileRemoveInput) -> Optional[Message]:
        try:
            minio_client.remove_object(input.bucket_name, input.object_name)
            return Message(message="Object removed", status_code=1200)
        except Exception as e:
            return Message(message=str(e), status_code=1400)


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQL(schema)
app = FastAPI()

app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)


# Object actions


# set_object_tags(bucket_name, object_name, tags, version_id=None)


@app.put("/put_object")
def put_object(bucket_name: str, object_name: str, file: bytes = File(...)):
    length = minio_client.put_object(bucket_name=bucket_name, object_name=object_name, data=file, length=-1)
    return {"length": length}


# Other actions


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
