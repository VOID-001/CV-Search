from pinecone import Pinecone, ServerlessSpec
import time
import os

def get_pinecone_index():
    # Initialize Pinecone client with the API key from settings
    pinecone_api_key = os.getenv('PINECONE_API_KEY')
    index_name = os.getenv('PINECONE_INDEX_NAME')
    pinecone_dimension = int(os.getenv('PINECONE_DIMENSION'))
    pinecone_metric = os.getenv('PINECONE_METRIC')
    pinecone_cloud = os.getenv('PINECONE_CLOUD')
    pinecone_region = os.getenv('PINECONE_REGION')

    pc = Pinecone(api_key=pinecone_api_key)

    # Check if the index already exists
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    if index_name not in existing_indexes:
        # Create the index if it does not exist
        pc.create_index(
            index_name,
            dimension=pinecone_dimension,
            metric=pinecone_metric,
            spec=ServerlessSpec(
                cloud=pinecone_cloud,
                region=pinecone_region
            )
        )

    # Wait for the index to be initialized
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)

    # Access the index
    pinecone_index = pc.Index(index_name)

    return pinecone_index