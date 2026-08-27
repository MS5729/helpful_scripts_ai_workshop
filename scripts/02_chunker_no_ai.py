"""Chunker with no AI: deterministic word-window chunking."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from workshop_common import chunk_records, output_json, parse_file

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("file")
parser.add_argument("--size", type=int, default=800)
parser.add_argument("--overlap", type=int, default=100)
args = parser.parse_args()
chunks = chunk_records(parse_file(args.file), args.size, args.overlap)
output_json("02_chunks.json", chunks)
print(f"Created {len(chunks)} chunks")
