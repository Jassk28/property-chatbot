# app.py
# A simple chatbot website that answers questions using the scraped data (data.json)
# Run it with:  python app.py   then open http://localhost:7860

import json
import os
import re

import requests
from flask import Flask, jsonify, render_template, request

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL = os.environ.get("MODEL", "openrouter/free")  # picks a free model automatically

app = Flask(__name__)

# ---- 1) Load the scraped data and cut it into small pieces ("chunks") ----
CHUNKS = []
with open("data.json", encoding="utf-8") as f:
    for page in json.load(f):
        text = page["text"]
        for i in range(0, len(text), 1500):
            CHUNKS.append({"source": page["source"], "url": page["url"], "text": text[i:i + 1500]})
print("Loaded", len(CHUNKS), "chunks")


def words(text):
    return set(re.findall(r"\w+", text.lower()))


# ---- 2) Find the chunks that best match the question (simple keyword search) ----
def find_relevant(question, top=6):
    q = words(question)
    scored = []
    for c in CHUNKS:
        score = len(q & words(c["text"] + " " + c["source"] + " " + c["url"]))
        scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for score, c in scored[:top] if score > 0]


# ---- 3) Ask the AI model, giving it the relevant data ----
def ask_ai(question):
    context = "\n\n".join(
        f"[{c['source']} - {c['url']}]\n{c['text']}" for c in find_relevant(question)
    )
    messages = [
        {"role": "system", "content": (
            "You are a helpful real-estate assistant for Wasalt (Saudi Arabia property portal) "
            "and DarGlobal (luxury real-estate developer). Answer ONLY using the data below. "
            "If the answer is not in the data, say you don't have that information. "
            "Prices on Wasalt are in SAR. Keep answers short and clear.\n\nDATA:\n" + context
        )},
        {"role": "user", "content": question},
    ]
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        json={"model": MODEL, "messages": messages},
        timeout=90,
    )
    data = r.json()
    if "choices" not in data:
        return "Sorry, the AI service returned an error: " + str(data.get("error", data))
    return data["choices"][0]["message"]["content"]


# ---- 4) Web pages ----
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    question = request.json.get("message", "").strip()
    if not question:
        return jsonify({"reply": "Please type a question."})
    try:
        return jsonify({"reply": ask_ai(question)})
    except Exception as e:
        return jsonify({"reply": f"Sorry, something went wrong: {e}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))
