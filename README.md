# Wasalt & DarGlobal Property Chatbot

An AI chatbot that answers questions about real-estate listings scraped from
**Wasalt** (wasalt.sa) and **DarGlobal** (darglobal.co.uk).

## How it works
1. `scraper.py` opens public pages of both websites in a headless browser (Playwright)
   and saves the page text to `data.json` (DarGlobal: the projects page plus every project page
   it links to). Wasalt's Cloudflare check blocks automated browsers, so Wasalt listing pages
   were copied by hand from a normal browser into `wasalt_pages/*.txt` and merged into
   `data.json` with `add_manual_pages.py`.
2. `app.py` (Flask) loads `data.json`, splits it into chunks, finds the chunks that match
   the user's question (keyword search) and sends them to a **free OpenRouter model**
   (`openrouter/free`) which writes the answer.
3. `templates/index.html` is the chat web page.
4. `Dockerfile` packages the app into a container. It is deployed on Render (free plan) directly from the Dockerfile.

## Files
| File | Purpose |
|------|---------|
| scraper.py | Collects the data → data.json |
| app.py | Chatbot server (Flask + OpenRouter) |
| templates/index.html | Chat page |
| Dockerfile | Container definition |
| requirements.txt | Python libraries |
| add_manual_pages.py | Adds hand-copied Wasalt pages to data.json |
| wasalt_pages/ | Wasalt page text copied from the browser |

## Run locally
```bash
pip install playwright flask requests
playwright install chromium
python scraper.py                      # creates data.json
export OPENROUTER_API_KEY=sk-or-...    # your key
python app.py                          # open http://localhost:7860
```

## Run with Docker
```bash
docker build -t property-chatbot .
docker run -p 7860:7860 -e OPENROUTER_API_KEY=sk-or-... property-chatbot
```

## Live demo
URL: (paste your Render link here)
