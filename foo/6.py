import json
from pathlib import Path

input_path = Path(__file__).parent / "data_snippets.json"
output_filename = Path(__file__).parent / "data_snippets_code"
def get_data(path: str) -> list[str]:
    data = []
    with open(path, encoding="utf-8") as file:
        data = json.load(file)
    return data

def parse_data(data: list[str]):
    out: list[str] = []
    for entry in data:
        out.append(entry["code"])
    return out

def write_to_csv(data: list[str], path: Path):
    path = path.with_suffix(".csv")
    with open(path, mode="w", encoding="utf-8") as file:
        file.write("code\n")
        file.write("\n".join(f"'{json.dumps(s)[1:-1]}'" for s in data))

def write_to_json(data: list[str], path: Path):
    path = path.with_suffix(".json")
    with open(path, mode="w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def write_to_text(data: list[str], path: Path):
    path = path.with_suffix(".txt")
    with open(path, mode="w", encoding="utf-8") as file:
        file.write("\n".join(f"{json.dumps(s)[1:-1]}" for s in data))

data = get_data(input_path)
out = parse_data(data)
# write_to_csv(out, output_path)
# write_to_json(out, output_path)
write_to_text(out, output_filename)
