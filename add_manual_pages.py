# add_manual_pages.py
# Adds pages you copied by hand (text files in the "wasalt_pages" folder) to data.json
# Run it with:  .venv/bin/python add_manual_pages.py

import json
import os
import re

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
    # Check the page matches the file name: every word of the name (e.g. villas, sale, jeddah)
    # must appear near the top of the page
    def simple(word):
        return word.lower().rstrip("s")  # villas -> villa, properties -> propertie
    top_words = {simple(w) for w in re.findall(r"\w+", text[:3000])}
    missing = [w for w in name[:-4].split("-") if simple(w) not in top_words]
    if missing:
        print("WRONG", name, "- page doesn't mention", missing, "- please copy it again")
        continue
    data.append({"source": "Wasalt", "url": "wasalt.sa (copied page: " + name[:-4] + ")", "text": text})
    print("OK  ", name, len(text), "chars")
    added += 1

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

darglobal = sum(1 for p in data if p["source"] == "DarGlobal")
print(f"\nSaved data.json  (Wasalt: {added}, DarGlobal: {darglobal})")
