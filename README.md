# UK Top 50 Playlist — Market Structure, Artist Diversity & Content Localization Analysis

Unified Mentor internship project for **Atlantic Recording Corporation**.
An interactive Streamlit dashboard that studies how the UK Top 50 playlist is structured: who dominates it, how
diverse it is, how collaborations, explicit content, release format and track length relate to chart presence.

**Author:** Thota Sathwika — B.Tech CSE, B V Raju Institute of Technology (BVRIT), Narsapur

## Dataset
`Atlantic_United_Kingdom.csv` — 27,800 rows of daily UK Top 50 snapshots, 18 May 2024 to 27 Nov 2025.

| Column | Description |
|---|---|
| date | Date of playlist snapshot (DD-MM-YYYY) |
| position | Playlist rank (1–50) |
| song / artist | Song title and artist(s), collaborators separated by `&` |
| popularity | Popularity score (0–100) |
| duration_ms | Track length in milliseconds |
| album_type | single / album / compilation |
| total_tracks | Tracks in the release |
| is_explicit | Explicit content flag |
| album_cover_url | Album artwork URL |

## Data cleaning
- Parsed dates; removed a duplicate snapshot on 01-03-2025 (one entry kept per date and rank → 27,750 rows, 555 days).
- Trimmed artist and song names; split collaborations on `&`, keeping acts whose own name contains `&`
  (e.g. *Chase & Status*, *Earth, Wind & Fire*) as one artist.
- Added rank groups (Top 10 / 11–25 / 26–50), duration buckets and popularity buckets.

## KPIs
| KPI | Definition | Full-period value |
|---|---|---|
| Artist Concentration Index | Herfindahl index of artist appearance shares (× 10,000) | 116 |
| Top-5 Concentration Ratio | Share of appearances held by the top 5 artists | 15.3% |
| Unique Artist Count | Distinct artists | 358 |
| Diversity Score | Unique artists ÷ total artist entries | 0.010 |
| Collaboration Ratio | Entries with 2+ credited artists | 17.7% |
| Explicit Content Share | Entries flagged explicit | 32.0% |
| Single : Album Ratio | Single entries ÷ album entries | 0.66 |
| Content Variety Index | Distinct songs ÷ total entries | 0.030 |

## Dashboard modules
- **Chart Race** — animated cumulative bar race of the top 10 artists by month
- **Artist Dominance** — leaderboard, UK vs international split (top-40 artists), unique artists per day
- **Collaborations** — solo vs collab share, collaboration rate by rank group, interactive collaboration network
- **Explicit vs Clean** — share, by rank group and by chart position
- **Album Structure** — release format share, format by rank, album size vs inclusion
- **Track Duration** — distribution, short vs long form, duration × popularity heatmap
- **Data** — filtered table with CSV download

Filters: date range, artist, solo/collaboration toggle, album type.

## Design
Neon dark theme (`.streamlit/config.toml` + custom CSS): animated gradient hero, KPI cards, live Top 5 with album artwork, artist podium, animated monthly chart race, glowing collaboration network.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (Streamlit Community Cloud)
1. Push this folder (including the CSV) to a public GitHub repository.
2. Go to https://share.streamlit.io → **Create app** → choose the repo, branch `main`, main file `app.py`.
3. Deploy, then copy the `https://<name>.streamlit.app` link.

## Tech stack
Python · Pandas · Plotly · NetworkX · Streamlit
