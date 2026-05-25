# Python News Bot

Ein einfacher RSS-News-Bot, der Schlagzeilen aus RSS-Feeds abruft, Top-News kurz zusammenfasst und die Ergebnisse als Markdown speichert.

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Nutzung

```powershell
python news_bot.py --feeds feeds.txt --output news_report.md --top 5
```

Optionen:

- `--feeds`: Textdatei mit einer RSS-URL pro Zeile
- `--output`: Markdown-Zieldatei, Standard ist `news_report.md`
- `--top`: Anzahl der Top-News, Standard ist `5`
- `--max-per-feed`: Maximale Artikel pro Feed, Standard ist `10`

Ohne `--feeds` nutzt der Bot die Standardfeeds aus `news_bot.py`.

---

# Example Output

See `news_report.md` for a sample generated report.

---

# How I Built This Project with Agentic AI.

First, I started Codex CLI in VSCode and used the following prompt:

```text
Erstelle einen einfachen Python-News-Bot, der folgende Anforderungen erfüllt:
- RSS-News abrufen
- Schlagzeilen extrahieren
- Top-News zusammenfassen
- Ergebnisse in Markdown speichern
```

Codex then generated the following files:

- `feeds.txt`
- `requirements.txt`
- `news_bot.py`
- `README.md`

After running `news_bot.py`, the program automatically generated a `news_report.md` file containing summarized news.

This project was a simple experiment in building a small AI-assisted workflow using Codex CLI.

It is very convenient for reading summarized news every day.