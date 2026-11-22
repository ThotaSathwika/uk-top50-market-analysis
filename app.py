import html
import itertools
import time

import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

st.set_page_config(page_title="UK Top 50 · Market Pulse", page_icon="🎧", layout="wide")

# ---------- Theme ----------
PINK, CYAN, VIOLET, AMBER, LIME = "#FF2E88", "#00E5FF", "#8B5CF6", "#FFC24B", "#3DFFA2"
NEON = [PINK, CYAN, VIOLET, AMBER, LIME, "#FF7A45", "#5B8CFF"]

pio.templates["neon"] = go.layout.Template(layout=dict(
    font=dict(family="Outfit, sans-serif", color="#E9E7FF", size=13),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    colorway=NEON, title=dict(font=dict(size=17, color="#FFFFFF"), x=0.01),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)",
               automargin=True, title=dict(standoff=14)),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)",
               automargin=True, title=dict(standoff=14)),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    hoverlabel=dict(bgcolor="#1B1438", bordercolor=PINK, font=dict(color="white")),
    margin=dict(l=20, r=20, t=60, b=30),
))
pio.templates.default = "neon"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Outfit', sans-serif; }
.stApp {
  background:
    radial-gradient(circle at 10% 0%, rgba(255,46,136,0.20), transparent 40%),
    radial-gradient(circle at 90% 10%, rgba(0,229,255,0.16), transparent 40%),
    radial-gradient(circle at 50% 100%, rgba(139,92,246,0.22), transparent 50%),
    #0B0820;
  color: #E9E7FF;
}
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.6rem; max-width: 1400px; }
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #160F35 0%, #0B0820 100%);
  border-right: 1px solid rgba(255,255,255,0.08);
}
section[data-testid="stSidebar"] * { color: #E9E7FF; }

/* Hero */
.hero {
  position: relative; overflow: hidden; border-radius: 28px; padding: 38px 42px;
  background: linear-gradient(120deg, #FF2E88, #8B5CF6 45%, #00B8D9);
  background-size: 200% 200%; animation: shift 12s ease infinite;
  box-shadow: 0 20px 60px rgba(139,92,246,0.35);
}
@keyframes shift { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
.hero h1 { font-size: 3rem; font-weight: 800; margin: 0; color: white; letter-spacing: -1px; line-height: 1.05; }
.hero p { font-size: 1.1rem; margin: 10px 0 18px; color: rgba(255,255,255,0.9); max-width: 720px; }
.chip { display: inline-block; padding: 6px 14px; margin: 0 8px 6px 0; border-radius: 999px;
  background: rgba(255,255,255,0.18); backdrop-filter: blur(6px); color: white; font-size: .85rem; font-weight: 600; }
.eq { position: absolute; right: 42px; bottom: 30px; display: flex; gap: 6px; align-items: flex-end; height: 90px; }
.eq span { width: 10px; border-radius: 6px; background: rgba(255,255,255,0.75); animation: bounce 1.1s ease-in-out infinite; }
.eq span:nth-child(2){animation-delay:.15s} .eq span:nth-child(3){animation-delay:.3s}
.eq span:nth-child(4){animation-delay:.45s} .eq span:nth-child(5){animation-delay:.6s}
.eq span:nth-child(6){animation-delay:.75s} .eq span:nth-child(7){animation-delay:.9s}
@keyframes bounce { 0%,100%{height:15%} 50%{height:100%} }

/* KPI cards */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 24px 0 8px; }
.kpi {
  position: relative; border-radius: 20px; padding: 18px 20px; overflow: hidden;
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.09);
  backdrop-filter: blur(10px); transition: transform .25s ease, box-shadow .25s ease;
}
.kpi:hover { transform: translateY(-4px); box-shadow: 0 12px 30px rgba(0,0,0,0.35); }
.kpi::before { content: ""; position: absolute; inset: 0 0 auto 0; height: 4px; background: var(--c); }
.kpi .icon { font-size: 1.4rem; }
.kpi .label { font-size: .8rem; text-transform: uppercase; letter-spacing: 1.2px; color: #A9A3D6; margin-top: 6px; }
.kpi .value { font-size: 2rem; font-weight: 800; color: white; line-height: 1.15; }
.kpi .hint { font-size: .78rem; color: var(--c); font-weight: 600; }

/* Section titles */
.sec { font-size: 1.5rem; font-weight: 800; margin: 26px 0 4px; color: white; }
.sec small { display: block; font-size: .9rem; font-weight: 400; color: #A9A3D6; }

/* Now-playing cards */
.np-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }
.np { border-radius: 18px; overflow: hidden; background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08); transition: transform .25s ease; }
.np:hover { transform: scale(1.03); }
.np img { width: 100%; aspect-ratio: 1; object-fit: cover; display: block; }
.np .meta { padding: 10px 12px 12px; }
.np .rank { font-weight: 800; font-size: 1.4rem; background: linear-gradient(90deg, #FF2E88, #00E5FF);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.np .song { font-weight: 600; color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.np .artist { font-size: .82rem; color: #A9A3D6; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.badge { font-size: .65rem; padding: 2px 7px; border-radius: 6px; background: #FF2E88; color: white;
  font-weight: 700; margin-left: 4px; vertical-align: middle; }

/* Podium */
.podium { display: grid; grid-template-columns: 1fr 1.15fr 1fr; gap: 16px; align-items: end; }
.pod { text-align: center; border-radius: 22px; padding: 18px; background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1); }
.pod img { width: 110px; height: 110px; border-radius: 50%; object-fit: cover; border: 4px solid var(--c);
  box-shadow: 0 0 30px var(--c); }
.pod.first img { width: 140px; height: 140px; }
.pod .medal { font-size: 1.8rem; }
.pod .name { font-weight: 800; color: white; font-size: 1.15rem; margin-top: 8px; }
.pod .stat { color: #A9A3D6; font-size: .9rem; }

/* Insight callout */
.insight { border-radius: 16px; padding: 14px 18px; margin: 8px 0 14px;
  background: linear-gradient(90deg, rgba(255,46,136,0.15), rgba(0,229,255,0.08));
  border-left: 4px solid #FF2E88; color: #F2F0FF; }

/* Tabs as pills */
.stTabs [role="tablist"] { gap: 8px; background: rgba(255,255,255,0.04); padding: 6px;
  border-radius: 999px; border: 1px solid rgba(255,255,255,0.08); }
.stTabs [role="tab"] { border-radius: 999px; padding: 8px 18px; color: #CFCBF2; font-weight: 600; }
.stTabs [aria-selected="true"] { background: linear-gradient(90deg, #FF2E88, #8B5CF6); color: white !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }
div[data-testid="stPlotlyChart"] { background: rgba(255,255,255,0.03); border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.07); overflow: hidden; }
.foot { text-align: center; color: #7E78AE; font-size: .85rem; margin: 40px 0 10px; }
@media (max-width: 900px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .np-grid { grid-template-columns: repeat(2, 1fr); } .hero h1 { font-size: 2rem; } .eq { display: none; } }
</style>
""", unsafe_allow_html=True)

# ---------- Data ----------
BAND_NAMES = ["Chase & Status", "Earth, Wind & Fire", "Baddiel, Skinner & Lightning Seeds",
              'Bobby "Boris" Pickett & The Crypt-Kickers', "Richy Mitch & The Coal Miners"]
UK_ARTISTS = {"Central Cee", "Dua Lipa", "Chase & Status", "RAYE", "Arctic Monkeys", "D-Block Europe", "Dave",
              "cassö", "Harry Styles", "Natasha Bedingfield", "Charli xcx", "Ella Henderson", "Coldplay"}
INTL_ARTISTS = {"Taylor Swift", "Sabrina Carpenter", "Billie Eilish", "Olivia Rodrigo", "Chappell Roan",
                "Benson Boone", "Drake", "The Killers", "Noah Kahan", "Teddy Swims", "The Weeknd", "Tate McRae",
                "Ariana Grande", "Hozier", "Vance Joy", "Lord Huron", "Post Malone", "Michael Marcagi", "SZA",
                "Doja Cat", "Dasha", "Ice Spice", "Jazzy", "Kanye West", "David Guetta", "David Kushner", "Beyoncé"}


def split_artists(name):
    for band in BAND_NAMES:
        name = name.replace(band, band.replace(" & ", "§"))
    return [a.strip().replace("§", " & ") for a in name.split(" & ")]


@st.cache_data
def load_data(path="Atlantic_United_Kingdom.csv"):
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
    df["artist"] = df["artist"].str.strip()
    df["song"] = df["song"].str.strip()
    df["album_type"] = df["album_type"].str.lower().str.strip()
    df = df.drop_duplicates(subset=["date", "position"], keep="first")   # one date had two snapshots
    df = df[df["position"].between(1, 50)]
    df["artist_list"] = df["artist"].apply(split_artists)
    df["n_artists"] = df["artist_list"].str.len()
    df["track_type"] = df["n_artists"].map(lambda n: "Collaboration" if n > 1 else "Solo")
    df["rank_group"] = pd.cut(df["position"], [0, 10, 25, 50], labels=["Top 10", "11-25", "26-50"])
    df["duration_min"] = df["duration_ms"] / 60000
    df["duration_group"] = pd.cut(df["duration_min"], [0, 2.5, 3.5, 4.5, 100],
                                  labels=["Short <2.5m", "Standard 2.5-3.5m", "Long 3.5-4.5m", "Very long >4.5m"])
    df["popularity_group"] = pd.cut(df["popularity"], [-1, 60, 75, 85, 100],
                                    labels=["Low ≤60", "Mid 61-75", "High 76-85", "Very high 86+"])
    df["explicit_label"] = df["is_explicit"].map({True: "Explicit", False: "Clean"})
    return df


def explode_artists(df):
    return df.explode("artist_list").rename(columns={"artist_list": "single_artist"})


def section(title, sub=""):
    st.markdown(f"<div class='sec'>{title}<small>{sub}</small></div>", unsafe_allow_html=True)


def insight(text):
    st.markdown(f"<div class='insight'>💡 {text}</div>", unsafe_allow_html=True)


df_all = load_data()

# ---------- Sidebar filters ----------
st.sidebar.markdown("## 🎛️ Mix Console")
min_d, max_d = df_all["date"].min().date(), df_all["date"].max().date()
date_range = st.sidebar.date_input("📅 Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
if len(date_range) != 2:
    st.stop()
start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

all_artists = sorted(explode_artists(df_all)["single_artist"].unique())
artist_pick = st.sidebar.multiselect("🎤 Artist", all_artists, placeholder="All artists")
track_pick = st.sidebar.segmented_control("🤝 Track type", ["All", "Solo", "Collaboration"], default="All") or "All"
album_types = sorted(df_all["album_type"].unique())
album_pick = st.sidebar.pills("💿 Album type", album_types, selection_mode="multi", default=album_types)
st.sidebar.markdown("---")
st.sidebar.caption("Data: Atlantic Recording Corporation · UK Top 50 daily snapshots")

df = df_all[(df_all["date"] >= start) & (df_all["date"] <= end) & df_all["album_type"].isin(album_pick or [])]
if track_pick != "All":
    df = df[df["track_type"] == track_pick]
if artist_pick:
    df = df[df["artist_list"].apply(lambda xs: any(a in artist_pick for a in xs))]

# ---------- Hero ----------
st.markdown(f"""
<div class="hero">
  <h1>UK Top 50<br>Market Pulse 🇬🇧</h1>
  <p>Who rules the UK charts, who teams up, and what UK listeners really stream:
  market structure, artist diversity and content localization for Atlantic Recording Corporation.</p>
  <span class="chip">📅 {start:%d %b %Y} → {end:%d %b %Y}</span>
  <span class="chip">🗓️ {df['date'].nunique()} daily charts</span>
  <span class="chip">🎵 {len(df):,} chart entries</span>
  <div class="eq"><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.warning("No chart entries match these filters. Try widening the date range or clearing the artist filter.")
    st.stop()

ex = explode_artists(df)

# ---------- KPIs ----------
artist_counts = ex["single_artist"].value_counts()
shares = artist_counts / artist_counts.sum()
hhi = (shares ** 2).sum() * 10000
cr5 = shares.head(5).sum() * 100
unique_artists = ex["single_artist"].nunique()
diversity = unique_artists / len(ex)
collab_ratio = (df["track_type"] == "Collaboration").mean() * 100
explicit_share = df["is_explicit"].mean() * 100
singles, albums = (df["album_type"] == "single").sum(), (df["album_type"] == "album").sum()
single_album_ratio = singles / albums if albums else float("nan")
variety = df.drop_duplicates(["song", "artist"]).shape[0] / len(df)

hhi_hint = "Unconcentrated" if hhi < 1500 else ("Moderate" if hhi < 2500 else "Highly concentrated")
kpis = [
    ("👑", "Artist Concentration (HHI)", f"{hhi:,.0f}", hhi_hint, PINK),
    ("🏆", "Top-5 Artist Share", f"{cr5:.1f}%", "of all appearances", CYAN),
    ("🎤", "Unique Artists", f"{unique_artists:,}", "in selection", VIOLET),
    ("🌈", "Diversity Score", f"{diversity:.3f}", "unique ÷ entries", AMBER),
    ("🤝", "Collaboration Ratio", f"{collab_ratio:.1f}%", "multi-artist tracks", LIME),
    ("🔞", "Explicit Share", f"{explicit_share:.1f}%", "explicit entries", PINK),
    ("💿", "Single : Album", f"{single_album_ratio:.2f}" if albums else "All singles" if singles else "–",
     f"{singles:,} vs {albums:,}", CYAN),
    ("🎨", "Content Variety", f"{variety:.3f}", "distinct songs ÷ entries", VIOLET),
]
st.markdown("<div class='kpi-grid'>" + "".join(
    f"<div class='kpi' style='--c:{c}'><div class='icon'>{i}</div><div class='label'>{l}</div>"
    f"<div class='value'>{v}</div><div class='hint'>{h}</div></div>" for i, l, v, h, c in kpis
) + "</div>", unsafe_allow_html=True)

# ---------- Now playing: latest chart in selection ----------
last_day = df["date"].max()
top5 = df_all[df_all["date"] == last_day].nsmallest(5, "position")
section("🔥 On the chart right now", f"Top 5 on {last_day:%d %B %Y}, the latest day in your selection")
st.markdown("<div class='np-grid'>" + "".join(
    f"<div class='np'><img src='{html.escape(r.album_cover_url)}' loading='lazy'>"
    f"<div class='meta'><div class='rank'>#{r.position}</div>"
    f"<div class='song'>{html.escape(r.song)}{'<span class=badge>E</span>' if r.is_explicit else ''}</div>"
    f"<div class='artist'>{html.escape(r.artist)}</div></div></div>" for r in top5.itertuples()
) + "</div>", unsafe_allow_html=True)

st.write("")
tabs = st.tabs(["🏆 Dominance", "🏁 Chart Race", "🤝 Collabs", "🔞 Explicit", "💿 Albums", "⏱️ Duration", "📄 Data"])

# ---------- Dominance ----------
with tabs[0]:
    lb = (ex.groupby("single_artist")
          .agg(appearances=("song", "size"), songs=("song", "nunique"), best_rank=("position", "min"),
               avg_rank=("position", "mean"), avg_popularity=("popularity", "mean"), days=("date", "nunique"))
          .sort_values("appearances", ascending=False).reset_index())
    lb["share_%"] = lb["appearances"] / len(ex) * 100
    covers = ex.groupby("single_artist")["album_cover_url"].agg(lambda s: s.value_counts().index[0])

    section("🥇 The podium", "Most chart appearances in the selection")
    top3 = lb.head(3)
    order = [1, 0, 2] if len(top3) == 3 else list(range(len(top3)))
    medals, colors = ["🥇", "🥈", "🥉"], [AMBER, CYAN, PINK]
    st.markdown("<div class='podium'>" + "".join(
        f"<div class='pod {'first' if i == 0 else ''}' style='--c:{colors[i]}'>"
        f"<img src='{html.escape(covers[top3.iloc[i].single_artist])}'><div class='medal'>{medals[i]}</div>"
        f"<div class='name'>{html.escape(top3.iloc[i].single_artist)}</div>"
        f"<div class='stat'>{top3.iloc[i].appearances:,} appearances · {top3.iloc[i]['share_%']:.1f}% share</div></div>"
        for i in order
    ) + "</div>", unsafe_allow_html=True)

    top_n = st.slider("Artists on the leaderboard", 5, 30, 15)
    lbn = lb.head(top_n)
    fig = px.bar(lbn[::-1], x="appearances", y="single_artist", orientation="h", color="appearances",
                 color_continuous_scale=[VIOLET, PINK, AMBER], text="appearances",
                 hover_data={"songs": True, "best_rank": True, "avg_rank": ":.1f", "share_%": ":.2f"},
                 labels={"single_artist": "", "appearances": "Chart appearances"}, title="Artist dominance leaderboard")
    fig.update_traces(marker_line_width=0, textposition="outside", textfont_color="white")
    fig.update_layout(height=32 * top_n + 120, coloraxis_showscale=False)
    st.plotly_chart(fig, width="stretch", theme=None)

    c1, c2 = st.columns([1, 1.4])
    tagged = ex[ex["single_artist"].isin(UK_ARTISTS | INTL_ARTISTS)].copy()
    with c1:
        if tagged.empty:
            st.info("None of the 40 tagged artists are in this selection.")
        else:
            tagged["origin"] = tagged["single_artist"].isin(UK_ARTISTS).map({True: "🇬🇧 UK", False: "🌍 International"})
            fig = px.pie(tagged, names="origin", hole=0.62, title="Domestic vs international",
                         color="origin", color_discrete_map={"🇬🇧 UK": PINK, "🌍 International": CYAN})
            fig.update_traces(textinfo="percent+label", marker_line_color="#0B0820", marker_line_width=3)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, width="stretch", theme=None)
            st.caption("Origin tagged manually for the 40 most-charting artists; Irish acts count as international.")
    with c2:
        daily = ex.groupby("date")["single_artist"].nunique().reset_index(name="unique_artists")
        fig = px.area(daily, x="date", y="unique_artists", title="Unique artists per day",
                      labels={"unique_artists": "Unique artists", "date": ""})
        fig.update_traces(line_color=CYAN, fillcolor="rgba(0,229,255,0.18)")
        st.plotly_chart(fig, width="stretch", theme=None)
    insight(f"An HHI of <b>{hhi:,.0f}</b> means the market is <b>{hhi_hint.lower()}</b>. "
            f"<b>{lb.iloc[0].single_artist}</b> leads with {lb.iloc[0]['share_%']:.1f}% of appearances.")

# ---------- Chart race ----------
with tabs[1]:
    section("🏁 The artist chart race", "Press ▶ Play race to watch total appearances build month by month, or drag the slider")
    months = ex["date"].dt.to_period("M")
    monthly = ex.assign(month=months).groupby(["month", "single_artist"]).size().unstack(fill_value=0)
    if len(monthly) < 2:
        st.info("Pick a date range covering at least two months to run the race.")
    else:
        cum = monthly.cumsum().stack().reset_index(name="appearances")
        cum["month"] = cum["month"].astype(str)
        cum["rank"] = cum.groupby("month")["appearances"].rank(method="first", ascending=False)
        race = cum[cum["rank"] <= 10].sort_values(["month", "appearances"])
        names = race["single_artist"].unique()
        cmap = {n: NEON[i % len(NEON)] for i, n in enumerate(names)}
        month_list = list(race["month"].unique())
        x_max = race["appearances"].max() * 1.15

        def race_fig(m):
            r = race[race["month"] == m]
            fig = go.Figure(go.Bar(x=r["appearances"].tolist(), y=r["single_artist"].tolist(), orientation="h",
                                   text=r["appearances"].tolist(), textposition="outside",
                                   marker_color=[cmap[n] for n in r["single_artist"]], marker_line_width=0,
                                   hovertemplate="%{y}: %{x}<extra></extra>"))
            fig.update_layout(height=540, title_text=f"📅 {pd.Period(m).strftime('%B %Y')}", margin=dict(l=150),
                              xaxis=dict(range=[0, x_max], title="Total appearances so far"))
            return fig

        c1, c2 = st.columns([1, 5])
        play = c1.button("▶ Play race", type="primary", width="stretch")
        pick = c2.select_slider("Month", month_list, value=month_list[-1], label_visibility="collapsed")
        holder = st.empty()
        if play:
            for m in month_list:
                holder.plotly_chart(race_fig(m), width="stretch", theme=None, key=f"race-{m}")
                time.sleep(0.6)
        else:
            holder.plotly_chart(race_fig(pick), width="stretch", theme=None)
        leaders = monthly.idxmax(axis=1)
        insight(f"<b>{leaders.value_counts().index[0]}</b> was the most-charting artist in "
                f"<b>{leaders.value_counts().iloc[0]} of {len(leaders)}</b> months.")

# ---------- Collaborations ----------
with tabs[2]:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(df, names="track_type", hole=0.62, title="Solo vs collaboration",
                     color="track_type", color_discrete_map={"Solo": VIOLET, "Collaboration": LIME})
        fig.update_traces(textinfo="percent+label", marker_line_color="#0B0820", marker_line_width=3)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch", theme=None)
    with c2:
        by_rank = df.groupby("rank_group", observed=True)["track_type"] \
            .apply(lambda s: (s == "Collaboration").mean() * 100).reset_index(name="collab_pct")
        fig = px.bar(by_rank, x="rank_group", y="collab_pct", text_auto=".1f", color="rank_group",
                     color_discrete_sequence=[PINK, VIOLET, CYAN], title="Collaboration rate by rank group",
                     labels={"rank_group": "", "collab_pct": "% collaborations"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch", theme=None)
    collab_only = df.loc[df.n_artists > 1, "n_artists"]
    insight(f"The average song credits <b>{df['n_artists'].mean():.2f}</b> artists; collaborations average "
            f"<b>{collab_only.mean() if len(collab_only) else 0:.2f}</b>.")

    section("🕸️ Collaboration universe", "Node size and glow = number of partners. Drag, zoom and hover.")
    collabs = df[df["n_artists"] > 1].drop_duplicates(["song", "artist"])
    G = nx.Graph()
    for artists in collabs["artist_list"]:
        for a, b in itertools.combinations(artists, 2):
            G.add_edge(a, b, weight=G[a][b]["weight"] + 1 if G.has_edge(a, b) else 1)
    if G.number_of_nodes() == 0:
        st.info("No collaborations in the current selection.")
    else:
        max_nodes = st.slider("Artists shown (most connected first)", 10, 150, 60)
        H = G.subgraph([n for n, _ in sorted(G.degree, key=lambda x: x[1], reverse=True)[:max_nodes]])
        pos = nx.spring_layout(H, k=0.6, seed=42)
        ex_x, ex_y = [], []
        for a, b in H.edges():
            ex_x += [pos[a][0], pos[b][0], None]
            ex_y += [pos[a][1], pos[b][1], None]
        deg = dict(H.degree())
        nodes = list(H.nodes())
        node_colors = [PINK if n in UK_ARTISTS else CYAN if n in INTL_ARTISTS else VIOLET for n in nodes]
        net = go.Figure([
            go.Scatter(x=ex_x, y=ex_y, mode="lines", line=dict(width=1, color="rgba(255,255,255,0.18)"),
                       hoverinfo="none"),
            go.Scatter(x=[pos[n][0] for n in nodes], y=[pos[n][1] for n in nodes], mode="markers",
                       marker=dict(size=[16 + 7 * deg[n] for n in nodes], color=node_colors, opacity=0.25),
                       hoverinfo="none"),
            go.Scatter(x=[pos[n][0] for n in nodes], y=[pos[n][1] for n in nodes], mode="markers+text",
                       text=nodes, textposition="top center", textfont=dict(size=10, color="#E9E7FF"),
                       marker=dict(size=[7 + 3 * deg[n] for n in nodes], color=node_colors,
                                   line=dict(width=1, color="white")),
                       hovertext=[f"<b>{n}</b><br>{deg[n]} partners" for n in nodes], hoverinfo="text"),
        ])
        net.update_layout(showlegend=False, height=680, xaxis=dict(visible=False), yaxis=dict(visible=False),
                          dragmode="pan")
        st.plotly_chart(net, width="stretch", theme=None, config={"scrollZoom": True})
        st.caption(f"🩷 UK artist · 🩵 International · 💜 Untagged — {G.number_of_nodes()} artists, "
                   f"{G.number_of_edges()} collaboration links in selection.")

# ---------- Explicit ----------
with tabs[3]:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(df, names="explicit_label", hole=0.62, title="Explicit vs clean",
                     color="explicit_label", color_discrete_map={"Explicit": PINK, "Clean": LIME})
        fig.update_traces(textinfo="percent+label", marker_line_color="#0B0820", marker_line_width=3)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch", theme=None)
    with c2:
        er = df.groupby("rank_group", observed=True)["is_explicit"].mean().mul(100).reset_index()
        fig = px.bar(er, x="rank_group", y="is_explicit", text_auto=".1f", color="rank_group",
                     color_discrete_sequence=[PINK, VIOLET, CYAN], title="Explicit share by rank group",
                     labels={"rank_group": "", "is_explicit": "% explicit"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch", theme=None)
    pos_exp = df.groupby("position")["is_explicit"].mean().mul(100).reset_index()
    fig = px.line(pos_exp, x="position", y="is_explicit", markers=True, title="Explicit share at every chart position",
                  labels={"is_explicit": "% explicit", "position": "Chart position"})
    fig.update_traces(line=dict(color=PINK, width=3, shape="spline"), marker=dict(color=AMBER, size=6))
    fig.add_hline(y=explicit_share, line_dash="dot", line_color=CYAN,
                  annotation_text=f"overall {explicit_share:.1f}%", annotation_font_color=CYAN)
    st.plotly_chart(fig, width="stretch", theme=None)
    comp = df.groupby("explicit_label").agg(avg_popularity=("popularity", "mean"),
                                            avg_position=("position", "mean"), entries=("song", "size")).round(2)
    st.dataframe(comp, width="stretch")
    top10_exp = df.loc[df.position <= 10, "is_explicit"].mean() * 100
    insight(f"Explicit tracks are <b>{top10_exp:.1f}%</b> of Top 10 entries against <b>{explicit_share:.1f}%</b> "
            f"overall. UK listeners don't push explicit songs down the chart.")

# ---------- Albums ----------
with tabs[4]:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(df, names="album_type", hole=0.62, title="Release format share",
                     color_discrete_sequence=[VIOLET, PINK, AMBER])
        fig.update_traces(textinfo="percent+label", marker_line_color="#0B0820", marker_line_width=3)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch", theme=None)
    with c2:
        ar = df.groupby(["rank_group", "album_type"], observed=True).size().reset_index(name="n")
        fig = px.bar(ar, x="rank_group", y="n", color="album_type", barmode="group",
                     color_discrete_sequence=[VIOLET, PINK, AMBER], title="Release format by rank group",
                     labels={"rank_group": "", "n": "Entries", "album_type": ""})
        st.plotly_chart(fig, width="stretch", theme=None)
    df_size = df.assign(album_size=pd.cut(df["total_tracks"], [0, 1, 5, 12, 20, 1000],
                                          labels=["1 (single)", "2-5 (EP)", "6-12", "13-20", "20+ (deluxe)"]))
    sz = df_size.groupby("album_size", observed=True).agg(
        entries=("song", "size"), songs=("song", "nunique"), avg_position=("position", "mean"),
        avg_popularity=("popularity", "mean")).reset_index()
    fig = px.scatter(sz, x="album_size", y="avg_position", size="entries", color="avg_popularity",
                     color_continuous_scale=[VIOLET, PINK, AMBER], size_max=70, text="entries",
                     title="Album size vs chart position (bubble = entries, colour = popularity)",
                     labels={"album_size": "Tracks on release", "avg_position": "Average position (lower = better)",
                             "avg_popularity": "Popularity"})
    fig.update_yaxes(autorange="reversed")
    fig.update_traces(textfont_color="white")
    st.plotly_chart(fig, width="stretch", theme=None)
    if albums:
        insight(f"Singles average position <b>{df.loc[df.album_type == 'single', 'position'].mean():.1f}</b> vs "
                f"<b>{df.loc[df.album_type == 'album', 'position'].mean():.1f}</b> for album tracks.")

# ---------- Duration ----------
with tabs[5]:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(df, x="duration_min", nbins=40, title="Track length distribution",
                           labels={"duration_min": "Minutes"}, color_discrete_sequence=[CYAN])
        fig.update_traces(marker_line_width=0, opacity=0.85)
        fig.add_vline(x=df["duration_min"].median(), line_dash="dot", line_color=PINK,
                      annotation_text=f"median {df['duration_min'].median():.2f} min", annotation_font_color=PINK)
        st.plotly_chart(fig, width="stretch", theme=None)
    with c2:
        dg = df.groupby("duration_group", observed=True).size().reset_index(name="entries")
        fig = px.bar(dg, x="duration_group", y="entries", text_auto=True, color="duration_group",
                     color_discrete_sequence=[LIME, CYAN, VIOLET, PINK], title="Short-form vs long-form",
                     labels={"duration_group": ""})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch", theme=None)
    hm = pd.crosstab(df["duration_group"], df["popularity_group"], normalize="index").mul(100).round(1)
    fig = px.imshow(hm, text_auto=True, aspect="auto", color_continuous_scale=["#120C2E", VIOLET, PINK, AMBER],
                    labels=dict(x="Popularity bucket", y="Duration bucket", color="% of row"),
                    title="Duration × popularity (% of each duration group)")
    st.plotly_chart(fig, width="stretch", theme=None)
    insight(f"<b>{df['duration_min'].between(2.5, 4.5).mean() * 100:.0f}%</b> of entries run 2.5–4.5 minutes; "
            f"UK listeners stick to classic song lengths.")

# ---------- Data ----------
with tabs[6]:
    show = df.drop(columns=["artist_list"]).sort_values(["date", "position"])
    st.dataframe(show, width="stretch", hide_index=True, column_config={
        "album_cover_url": st.column_config.ImageColumn("Cover"),
        "date": st.column_config.DateColumn("Date", format="DD MMM YYYY"),
        "popularity": st.column_config.ProgressColumn("Popularity", min_value=0, max_value=100, format="%d"),
    })
    st.download_button("⬇️ Download filtered data (CSV)", show.to_csv(index=False), "uk_top50_filtered.csv",
                       type="primary")

st.markdown("<div class='foot'>Built with ❤️ by Thota Sathwika · Unified Mentor × Atlantic Recording Corporation"
            "</div>", unsafe_allow_html=True)
