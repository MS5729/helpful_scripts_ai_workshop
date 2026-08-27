"""Chunker agent: ask an LLM for semantic section labels, then chunk locally."""
import argparse, os, json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from workshop_common import chunk_records, output_json, parse_file, required_env
from openai import OpenAI

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("file")
args = parser.parse_args()
client = OpenAI(api_key=required_env("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL") or None)
model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
records = parse_file(args.file)
for record in records:
    response = client.chat.completions.create(model=model, temperature=0, response_format={"type": "json_object"}, messages=[
        {"role": "system", "content": "Return JSON with one field named section. Give a short section label based only on the supplied text."},
        {"role": "user", "content": record["text"]},
    ])
    record["section"] = json.loads(response.choices[0].message.content).get("section", "General")
chunks = chunk_records(records)
output_json("04_chunks_agent.json", chunks)
print(f"Created {len(chunks)} semantically labeled chunks")
