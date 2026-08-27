"""Complete RAG pipeline: retrieve Atlas context, answer, and show citations."""
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
embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
vector = client.embeddings.create(model=embedding_model, input=args.question).data[0].embedding
collection = MongoClient(required_env("MONGODB_URI"))[required_env("MONGODB_DATABASE")][os.getenv("MONGODB_VECTOR_COLLECTION", "rag_chunks")]
results = list(collection.aggregate([{"$vectorSearch": {"index": os.getenv("MONGODB_VECTOR_INDEX", "vector_index"), "path": "embedding", "queryVector": vector, "numCandidates": args.top_k * 20, "limit": args.top_k}}, {"$project": {"_id": 0, "text": 1, "metadata": 1, "score": {"$meta": "vectorSearchScore"}}}]))
context = "\n\n".join(f"SOURCE {i}: {item['text']}" for i, item in enumerate(results, 1))
response = client.chat.completions.create(model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"), temperature=0, messages=[
    {"role": "system", "content": "Answer only from the supplied context. If it is insufficient, say so. Cite sources as [SOURCE N]."},
    {"role": "user", "content": f"Question: {args.question}\n\nContext:\n{context}"},
])
print(response.choices[0].message.content)
print("\nSources:")
for number, item in enumerate(results, 1):
    print(f"[SOURCE {number}] {item.get('metadata', {})}")
