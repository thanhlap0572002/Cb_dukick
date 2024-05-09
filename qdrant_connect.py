from lib import *

client = QdrantClient(
    url="https://785dad3b-d933-4697-87ad-93ccebc059d8.us-east4-0.gcp.cloud.qdrant.io:6333", 
    api_key="9GNe65ku1CMzizKksXJTM1Q_qqCfwjFgA-lv8-TpX4QwtWcGX2MHKQ",
    timeout= 3000
)

def create_qdrant_collection(client, collection_name):
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE)
    )
    

# def insert_data_into_qdrant(client, collection_name, points):
#     client.upsert(
#         collection_name=collection_name,
#         wait=True,
#         points=[PointStruct(**point) for point in points]
#     )
def insert_data_into_qdrant(client, collection_name, points):
    client.upload_points(
        collection_name=collection_name,
        wait=True,
        points=[PointStruct(**point) for point in points]
    )

def search_data_into_qdrant(client, collection_name, query, model_id):
    hits = client.search(
    collection_name=collection_name,
    query_vector=SentenceTransformer(model_id).encode(query).tolist(),
    limit=5)
    return hits