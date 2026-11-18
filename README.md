# Wasalt & DarGlobal Property Chatbot

An AI chatbot that answers questions about real-estate data collected from
**Wasalt** (wasalt.sa) and **DarGlobal** (darglobal.co.uk).

## 🔗 Live demo
**https://property-chatbot-jx10.onrender.com**

> Hosted on Render's free plan: if nobody has used it for 15 minutes, the first load can take
> about 50 seconds while the server wakes up. After that it responds normally.

Source code: https://github.com/Jassk28/property-chatbot

## 💬 Example questions
**Wasalt (Riyadh listings)**
- Show me villas for sale in Riyadh with prices
- Apartments for sale in Riyadh under 600,000
- What properties are available in Al Arid?
- What is the cheapest villa in Riyadh?
- Show me apartments in Riyadh with 3 bedrooms

**DarGlobal (luxury projects)**
- Which DarGlobal projects are in Oman?
- Tell me about DG1
- What DarGlobal projects are in Dubai?
- Tell me about Trump International Hotel & Tower Dubai
- Which DarGlobal projects are in Spain?

## 📦 Data collected
| Source | Pages | What's included |
|--------|-------|-----------------|
| DarGlobal | 31 | Projects overview plus every individual project page (UAE, Oman, Qatar, Spain, UK, Saudi Arabia) |
| Wasalt | 5 | Riyadh: apartments for sale, villas for sale, Al Arid properties and villas, one apartment listing |

The chatbot answers **only from this data**. If something isn't in it (e.g. Jeddah listings or
rentals), it says it doesn't have that information instead of making it up.
Wasalt prices are in SAR.

## ⚙️ How it works
1. **Scraping:** `scraper.py` uses Playwright (a headless browser) to open DarGlobal's projects
   page, then visits every project page linked from it, and saves the page text to `data.json`.
   Wasalt's Cloudflare security check blocks automated browsers, so Wasalt listing pages were
   opened in a normal browser, their text copied into `wasalt_pages/*.txt`, and merged into
   `data.json` with `add_manual_pages.py`. That script checks each page matches its file name.
2. **Search:** `app.py` (Flask) splits the data into small chunks. For each question it finds the
   most relevant chunks using a simple keyword search.
3. **AI answer:** those chunks and the question are sent to a **free OpenRouter model**
   (`openrouter/free`, which picks an available free model automatically). The model writes
   the answer using only that data.
4. **Web page:** `templates/index.html` is the chat interface.
5. **Container & deployment:** the `Dockerfile` packages the app with Gunicorn. Render builds and
   runs this Docker image directly from the GitHub repository.

## 📁 Files
| File | Purpose |
|------|---------|
| scraper.py | Collects DarGlobal pages → data.json |
| add_manual_pages.py | Adds the copied Wasalt pages to data.json |
| wasalt_pages/ | Wasalt page text copied from the browser |
| data.json | All collected data used by the chatbot |
| app.py | Chatbot server (Flask + OpenRouter) |
| templates/index.html | Chat page |
| Dockerfile | Container definition |
| requirements.txt | Python libraries |

## 🖥️ Run locally
```bash
pip install playwright flask requests
playwright install chromium
python scraper.py                      # collects DarGlobal pages into data.json
python add_manual_pages.py             # adds the Wasalt pages
export OPENROUTER_API_KEY=sk-or-...    # your OpenRouter key
python app.py                          # open http://localhost:7860
```

## 🐳 Run with Docker
```bash
docker build -t property-chatbot .
docker run -p 7860:7860 -e OPENROUTER_API_KEY=sk-or-... property-chatbot
```
Then open http://localhost:7860

## 🔑 Configuration
| Variable | Required | Default |
|----------|----------|---------|
| OPENROUTER_API_KEY | Yes | — |
| MODEL | No | openrouter/free |
| PORT | No | 7860 (Render sets this automatically) |
