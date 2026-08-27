"""Check API and MongoDB Atlas configuration without revealing secrets."""
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from workshop_common import required_env
from openai import OpenAI
from pymongo import MongoClient

print("Environment diagnosis")
api_key = required_env("OPENAI_API_KEY")
print(f"OPENAI_API_KEY: present ({len(api_key)} characters)")
client = OpenAI(api_key=api_key, base_url=os.getenv("OPENAI_BASE_URL") or None)
try:
    models = client.models.list()
    print(f"OpenAI-compatible API: reachable ({len(list(models.data))} models visible)")
except Exception as error:
    print(f"OpenAI-compatible API: FAILED ({error})")

uri = required_env("MONGODB_URI")
database_name = required_env("MONGODB_DATABASE")
mongo = MongoClient(uri, serverSelectionTimeoutMS=5000)
try:
    mongo.admin.command("ping")
    database = mongo[database_name]
    collection_name = os.getenv("MONGODB_VECTOR_COLLECTION", "rag_chunks")
    collection = database[collection_name]
    index_name = os.getenv("MONGODB_VECTOR_INDEX", "vector_index")
    indexes = list(collection.list_search_indexes())
    names = {item.get("name") for item in indexes}
    print(f"MongoDB Atlas: reachable (database={database_name})")
    print(f"Vector collection: {collection_name} ({collection.count_documents({})} documents)")
    print(f"Vector index {index_name}: {'found' if index_name in names else 'NOT FOUND'}")
finally:
    mongo.close()
