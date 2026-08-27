"""Parser agent: use an LLM to classify extracted records into useful fields."""
import argparse, json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from workshop_common import output_json, parse_file, required_env
from openai import OpenAI

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("file")
args = parser.parse_args()
client = OpenAI(api_key=required_env("OPENAI_API_KEY"), base_url=__import__("os").getenv("OPENAI_BASE_URL") or None)
model = __import__("os").getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
records = parse_file(args.file)
structured = []
for record in records:
    response = client.chat.completions.create(model=model, temperature=0, response_format={"type": "json_object"}, messages=[
        {"role": "system", "content": "Extract structured document facts. Return JSON with title, summary, topics, and entities. Do not invent facts."},
        {"role": "user", "content": record["text"]},
    ])
    structured.append({**record, "structured": json.loads(response.choices[0].message.content)})
output_json("03_parser_agent.json", structured)
print(f"Structured {len(structured)} records")
