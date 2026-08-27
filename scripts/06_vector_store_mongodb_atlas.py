"""MongoDB Atlas vector store: embed and upsert chunks, or search by query."""
import argparse, os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from workshop_common import chunk_records, parse_file, required_env
from openai import OpenAI
from pymongo import MongoClient

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("file")
parser.add_argument("--query", help="Run Atlas vector search instead of upserting")
parser.add_argument("--top-k", type=int, default=5)
args = parser.parse_args()
client = OpenAI(api_key=required_env("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL") or None)
model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
mongo = MongoClient(required_env("MONGODB_URI"))
collection = mongo[required_env("MONGODB_DATABASE")][os.getenv("MONGODB_VECTOR_COLLECTION", "rag_chunks")]
index = os.getenv("MONGODB_VECTOR_INDEX", "vector_index")
if args.query:
    vector = client.embeddings.create(model=model, input=args.query).data[0].embedding
    results = collection.aggregate([{"$vectorSearch": {"index": index, "path": "embedding", "queryVector": vector, "numCandidates": args.top_k * 20, "limit": args.top_k}}, {"$project": {"_id": 0, "text": 1, "metadata": 1, "score": {"$meta": "vectorSearchScore"}}}])
    for result in results:
        print(result)
else:
    chunks = chunk_records(parse_file(args.file))
    vectors = client.embeddings.create(model=model, input=[chunk["text"] for chunk in chunks]).data
    documents = [{"text": chunk["text"], "metadata": chunk["metadata"], "embedding": vector.embedding, "model": model} for chunk, vector in zip(chunks, vectors)]
    if documents:
        collection.insert_many(documents)
    print(f"Stored {len(documents)} chunks in {collection.name}")
