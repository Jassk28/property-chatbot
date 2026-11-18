# add_manual_pages.py
# Adds pages you copied by hand (text files in the "wasalt_pages" folder) to data.json
# Run it with:  .venv/bin/python add_manual_pages.py

import json
import os

FOLDER = "wasalt_pages"

# Load existing data (e.g. DarGlobal pages from scraper.py), drop old Wasalt entries
data = []
if os.path.exists("data.json"):
    with open("data.json", encoding="utf-8") as f:
        data = [p for p in json.load(f) if p["source"] != "Wasalt"]

added = 0
for name in sorted(os.listdir(FOLDER)):
    if not name.endswith(".txt"):
        continue
    with open(os.path.join(FOLDER, name), encoding="utf-8") as f:
        text = f.read().strip()
    if len(text) < 300:
        print("SKIP", name, "(too short - did you paste the page?)")
        continue
    data.append({"source": "Wasalt", "url": "https://wasalt.sa/en/" + name[:-4], "text": text})
    print("OK  ", name, len(text), "chars")
    added += 1

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

darglobal = sum(1 for p in data if p["source"] == "DarGlobal")
print(f"\nSaved data.json  (Wasalt: {added}, DarGlobal: {darglobal})")
