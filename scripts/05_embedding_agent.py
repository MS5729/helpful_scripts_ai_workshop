"""Embedding agent: create vectors for deterministic chunks."""
import argparse, os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from workshop_common import chunk_records, output_json, parse_file, required_env
from openai import OpenAI

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("file")
args = parser.parse_args()
client = OpenAI(api_key=required_env("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL") or None)
model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
chunks = chunk_records(parse_file(args.file))
response = client.embeddings.create(model=model, input=[chunk["text"] for chunk in chunks])
for chunk, embedding in zip(chunks, response.data):
    chunk["embedding"] = embedding.embedding
output_json("05_embedded_chunks.json", chunks)
print(f"Embedded {len(chunks)} chunks with {model}")
