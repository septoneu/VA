#!/usr/bin/env python3
import json

with open("depscan-bom.json", "r", encoding="utf-8") as file:
    raw_data = file.read().strip()

json_objects = raw_data.split("\n")
parsed_json = [json.loads(obj) for obj in json_objects]

with open("final_report.json", "w", encoding="utf-8") as output_file:
    json.dump(parsed_json, output_file, indent=4)

print("✅ JSON fixed! Saved as 'final_report.json'")
