"""Mock RAG pipeline: learn retrieval locally with no API key or database."""
import argparse, re
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from workshop_common import chunk_records, parse_file

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("file")
parser.add_argument("question")
args = parser.parse_args()
chunks = chunk_records(parse_file(args.file), size=120, overlap=20)
query_terms = set(re.findall(r"[a-z0-9]+", args.question.lower()))
def score(chunk: dict) -> int:
    words = set(re.findall(r"[a-z0-9]+", chunk["text"].lower()))
    return len(query_terms & words)
ranked = sorted(chunks, key=score, reverse=True)
print(f"Question: {args.question}\n")
for number, chunk in enumerate(ranked[:3], 1):
    print(f"[SOURCE {number}] keyword score={score(chunk)} metadata={chunk['metadata']}")
    print(chunk["text"][:500], "\n")
print("This is a teaching demo: keyword overlap replaces embeddings and an LLM.")
