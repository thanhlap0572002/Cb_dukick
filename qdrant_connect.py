from lib import *


def create_qdrant_collection(client, collection_name):
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
    )

def insert_data_into_qdrant(client, collection_name, points):
    client.upsert(
        collection_name=collection_name,
        wait=True,
        points=[PointStruct(**point) for point in points]
    )

