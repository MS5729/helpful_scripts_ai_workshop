"""Check MongoDB Atlas Vector Search configuration and optionally run a live query."""
import argparse
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1]))

from pymongo import MongoClient
from workshop_common import required_env


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--query", help="Optionally run a real vector search using this question")
parser.add_argument("--top-k", type=int, default=3)
args = parser.parse_args()

uri = required_env("MONGODB_URI")
database_name = required_env("MONGODB_DATABASE")
collection_name = os.getenv("MONGODB_VECTOR_COLLECTION", "rag_chunks")
index_name = os.getenv("MONGODB_VECTOR_INDEX", "vector_index")

mongo = MongoClient(uri, serverSelectionTimeoutMS=5000)
try:
    mongo.admin.command("ping")
    database = mongo[database_name]
    collection = database[collection_name]
    print("MongoDB Atlas: OK")
    print(f"Database: {database_name}")
    print(f"Collection: {collection_name}")
    print(f"Documents: {collection.count_documents({})}")

    indexes = list(collection.list_search_indexes())
    matching_index = next((item for item in indexes if item.get("name") == index_name), None)
    if matching_index is None:
        print(f"Vector index '{index_name}': NOT FOUND")
        print(f"Available indexes: {[item.get('name') for item in indexes]}")
        raise SystemExit(1)
    print(f"Vector index '{index_name}': FOUND")
    print(f"Index status: {matching_index.get('status', 'unknown')}")

    sample = collection.find_one({}, {"embedding": 1, "model": 1})
    if sample and sample.get("embedding"):
        print(f"Stored embedding dimensions: {len(sample['embedding'])}")
        print(f"Stored embedding model: {sample.get('model', 'not recorded')}")
    else:
        print("Stored embeddings: no documents available to inspect")

    if args.query:
        from openai import OpenAI

        client = OpenAI(
            api_key=required_env("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL") or None,
        )
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        vector = client.embeddings.create(model=model, input=args.query).data[0].embedding
        results = list(collection.aggregate([
            {"$vectorSearch": {
                "index": index_name,
                "path": "embedding",
                "queryVector": vector,
                "numCandidates": max(args.top_k * 20, 20),
                "limit": args.top_k,
            }},
            {"$project": {"_id": 0, "score": {"$meta": "vectorSearchScore"}}},
        ]))
        print(f"Live vector search: OK ({len(results)} results)")
        for number, result in enumerate(results, 1):
            print(f"  Result {number} score: {result.get('score', 0):.4f}")
finally:
    mongo.close()
