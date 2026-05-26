# Prospect Discovery Tool

A small Python tool that builds a prospect list by searching the Google Places API across a configurable set of ZIP codes and storing the results in a local SQLite database (`prospects.db`).

This is the first stage of a three-stage pipeline:

1. **Discover** (this tool) — Pull raw place data from Google Places for every ZIP code in scope.
2. **Enrich & validate** — A CrewAI agent crew reads from `prospects.db`, fills in missing details (e.g., pastor / decision-maker name, denomination, contact email), and scores quality.
3. **Activate** — Validated, enriched prospects are imported into HubSpot and assigned to a Sequence.

## What you get

Each row in `prospects.db` (table: `prospects`) represents one business and includes:

- Identity: name, place ID, business status
- Location: full address, city, state, ZIP, lat/long
- Contact: phone, website
- Classification: primary type, vertical label
- Reputation: Google rating, review count

A second table (`searched_targets`) records which ZIP codes have been searched for which vertical, so reruns automatically skip work already done and retry only failures.

## One-time setup

```bash
uv sync                                           # install dependencies
export GOOGLE_MAPS_API_KEY='your-key-here'        # or place in a .env file
```

The API key should be restricted in Google Cloud Console to the Places API (New).

## Running a search

```bash
uv run main.py
```

You'll see live progress with an ETA. The tool is safe to interrupt (`Ctrl+C`); the next run resumes from where it left off.

## Configuring the search

Two files control what gets searched:

- **`zip_codes.txt`** — one ZIP code per line. Edit to change geographic scope.
- **`main.py`** (top of file) — set `VERTICAL` and `QUERY_TEMPLATE` to target a different industry or business type.

Example to search schools instead of places of worship:

```python
VERTICAL = "schools"
QUERY_TEMPLATE = "elementary schools | middle schools | high schools in zip code {zip_code}"
```

Each vertical is tracked independently, so the same ZIP can be searched for multiple verticals without conflict.

## Cost and scale

Google Places API is billed per request. A full run over ~300 ZIP codes with the current field selection typically runs **15–25 minutes** and costs **$25–45**. Refer to [Google's pricing](https://mapsplatform.google.com/pricing/) for current rates.

## Output files

| File | Purpose |
|---|---|
| `prospects.db` | SQLite database with prospect and search-history tables |
| `failed_searches.txt` | Timestamped log of any ZIP codes that failed after retries |
