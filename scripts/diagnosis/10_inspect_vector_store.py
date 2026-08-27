"""Inspect Atlas vector count, dimensions, models, and metadata without printing full vectors."""
import argparse, os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from workshop_common import required_env
from pymongo import MongoClient

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--samples", type=int, default=3)
args = parser.parse_args()
mongo = MongoClient(required_env("MONGODB_URI"), serverSelectionTimeoutMS=5000)
collection = mongo[required_env("MONGODB_DATABASE")][os.getenv("MONGODB_VECTOR_COLLECTION", "rag_chunks")]
try:
    print(f"Collection: {collection.name}")
    print(f"Documents: {collection.count_documents({})}")
    models = collection.distinct("model")
    print(f"Embedding models: {models or ['not recorded']}")
    sample = collection.find({}, {"embedding": 1, "text": 1, "metadata": 1, "model": 1}).limit(args.samples)
    for number, document in enumerate(sample, 1):
        print(f"\nSample {number}")
        print(f"Embedding dimensions: {len(document.get('embedding', []))}")
        print(f"Metadata: {document.get('metadata', {})}")
        print(f"Text preview: {document.get('text', '')[:200]}")
finally:
    mongo.close()
