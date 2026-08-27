"""Parser with no AI: extract text and source metadata from a local file."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from workshop_common import output_json, parse_file

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("file")
args = parser.parse_args()
records = parse_file(args.file)
output_json("01_parsed_records.json", records)
print(f"Parsed {len(records)} records from {args.file}")
