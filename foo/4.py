import sys
import os
import ipdb
from pathlib import Path

file_data = []

with open(Path(__file__).parent.parent / "data" / "gist_out.md", encoding="utf-8") as file:
    file_data = file.readlines()


is_code_block = False
section = []
data = []

for i, line in enumerate(file_data):
    if not line.strip(): continue

    if line.startswith("```"):
        is_code_block = not is_code_block
    
    if is_code_block:
        section.append(line)
        continue

    if line.startswith("# "):
        if len(section) == 0:
            section.append(line)
        else:
            data.append({"k": section[0].split("#")[1], "data": [*section]})
            section = []

    section.append(line)


data = data[1:]
data = sorted(data, key=lambda x: x["k"])
# for x in data:
    # ipdb.set_trace()
#     print(x["k"])

with open(Path(__file__).parent.parent / "data" / "gist_out_sorted.md", mode="w", encoding="utf-8") as file:
    for x in data:
        file.write("".join(x["data"]))
        file.write("\n")
# print(code_block_count)