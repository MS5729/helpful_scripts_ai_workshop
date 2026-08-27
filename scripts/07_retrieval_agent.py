"""Retrieval agent: search Atlas and print source citations for a question."""
import argparse, os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from workshop_common import required_env
from openai import OpenAI
from pymongo import MongoClient

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("question")
parser.add_argument("--top-k", type=int, default=5)
args = parser.parse_args()
client = OpenAI(api_key=required_env("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL") or None)
vector = client.embeddings.create(model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"), input=args.question).data[0].embedding
collection = MongoClient(required_env("MONGODB_URI"))[required_env("MONGODB_DATABASE")][os.getenv("MONGODB_VECTOR_COLLECTION", "rag_chunks")]
results = collection.aggregate([{"$vectorSearch": {"index": os.getenv("MONGODB_VECTOR_INDEX", "vector_index"), "path": "embedding", "queryVector": vector, "numCandidates": args.top_k * 20, "limit": args.top_k}}, {"$project": {"_id": 0, "text": 1, "metadata": 1, "score": {"$meta": "vectorSearchScore"}}}])
for number, result in enumerate(results, 1):
    print(f"[{number}] score={result['score']:.4f} source={result.get('metadata', {})}")
    print(result["text"][:1000], "\n")
