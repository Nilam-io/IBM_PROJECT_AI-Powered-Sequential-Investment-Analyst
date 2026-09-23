import html
import io
import math
import os
import re
from datetime import datetime, timedelta
from urllib.parse import quote

import pandas as pd
import requests
import streamlit as st
import yfinance as yf
from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv()

st.set_page_config(page_title="Meridian Investment Analyst", page_icon="M", layout="wide")

PEERS = {"AAPL": ["MSFT", "GOOGL"], "MSFT": ["AAPL", "GOOGL"], "GOOGL": ["MSFT", "META"], "NVDA": ["AMD", "INTC"], "TSLA": ["F", "GM"], "AMZN": ["WMT", "MSFT"], "JPM": ["BAC", "GS"], "JNJ": ["PFE", "MRK"]}


def css():
    st.markdown("""
    <style>
    :root { --ink:#13213c; --muted:#66738a; --line:#dfe5ef; --blue:#315cff; --blue2:#2345c8; --bg:#f5f7fb; }
    .stApp { background:var(--bg); color:var(--ink); }
    .block-container { max-width:1280px; padding:1.2rem 2.2rem 4rem; }
    [data-testid="stHeader"] { background:rgba(245,247,251,.9); }
    .mast { display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--line); padding:12px 0 22px; margin-bottom:28px; }
    .brand { font-size:1rem; font-weight:850; letter-spacing:.16em; color:var(--ink); } .brand b { color:var(--blue); }
    .eyebrow { color:var(--blue); font-size:.7rem; font-weight:800; letter-spacing:.15em; text-transform:uppercase; }
    h1 { font-size:2.55rem!important; letter-spacing:-.045em!important; color:var(--ink)!important; margin-bottom:.25rem!important; }
    h2,h3 { color:var(--ink)!important; } [data-testid="stCaptionContainer"] { color:var(--muted)!important; }
    .panel { background:#fff; border:1px solid var(--line); border-radius:12px; box-shadow:0 8px 24px rgba(30,45,75,.05); padding:22px; margin:14px 0; }
    .panel h3 { margin-top:0; } .section { font-size:1.22rem; font-weight:800; margin:30px 0 12px; color:var(--ink); }
    .trust { border-left:4px solid var(--blue); } .trust-items { display:flex; flex-wrap:wrap; gap:22px; color:#344054; font-size:.9rem; }
    .trust-items b { color:var(--blue); margin-right:5px; }
    .steps { display:grid; grid-template-columns:repeat(5,1fr); gap:10px; margin:20px 0; } .step { padding:15px; background:#fff; border:1px solid var(--line); border-radius:9px; }
    .step.done { border-color:var(--blue); box-shadow:0 0 0 1px var(--blue); } .step-num { color:var(--blue); font-size:.7rem; font-weight:800; letter-spacing:.12em; }
    .step-name { font-weight:750; margin-top:6px; } .step-state { color:var(--muted); font-size:.78rem; margin-top:4px; }
    .metric { background:#fff; border:1px solid var(--line); border-radius:10px; padding:17px; min-height:108px; box-shadow:0 5px 18px rgba(30,45,75,.04); }
    .metric-label { color:var(--muted); font-size:.7rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; } .metric-value { font-size:1.5rem; font-weight:850; margin-top:8px; }
    .metric-note { color:#16805c; font-size:.78rem; margin-top:4px; } .warn { color:#b54708; }
    .callout { padding:18px 20px; border-radius:9px; border-left:4px solid; margin:10px 0; } .positive { background:#ecfdf3; border-color:#12b76a; color:#14532d; } .neutral { background:#fffaeb; border-color:#d99000; color:#713f12; } .negative { background:#fff1f3; border-color:#e11d48; color:#881337; }
    .callout-title { font-weight:850; font-size:1.1rem; margin-bottom:6px; } .source { color:#475467; font-size:.85rem; padding:4px 0; }
    .hero { background:linear-gradient(120deg,#13213c 0%,#1e3471 58%,#315cff 100%); color:#fff; border-radius:14px; padding:26px; margin:18px 0; box-shadow:0 14px 30px rgba(25,45,100,.18); }
    .hero h2 { color:#fff!important; margin:5px 0 2px; } .hero .muted { color:#cbd5ef!important; font-size:.86rem; }
    .hero-verdict { color:#fff; font-size:2rem; font-weight:850; letter-spacing:-.03em; } .hero-copy { color:#e3e9f8; max-width:720px; line-height:1.55; }
    .score { background:#fff; border:1px solid var(--line); border-radius:10px; padding:16px; min-height:94px; } .score-label { color:var(--muted); font-size:.7rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; } .score-value { color:var(--ink); font-size:1.35rem; font-weight:850; margin-top:8px; }
    .nav-note { color:var(--muted); font-size:.8rem; line-height:1.5; padding:8px 0 16px; }
    .source-card { background:#fff; border:1px solid var(--line); border-radius:9px; padding:12px 14px; margin:8px 0; } .source-card a { color:var(--blue); font-weight:700; text-decoration:none; }
    .tab-label { font-weight:800; color:var(--ink); }
    div[data-testid="stButton"] button, div[data-testid="stDownloadButton"] button { background:var(--blue); color:#fff; border:1px solid var(--blue); border-radius:8px; font-weight:750; }
    div[data-testid="stButton"] button:hover, div[data-testid="stDownloadButton"] button:hover { background:var(--blue2); color:#fff; border-color:var(--blue2); }
    .rating div[data-testid="stButton"] button { background:#fff; color:#98a2b3; border-color:#d0d5dd; font-size:1.3rem; min-height:42px; }
    .rating div[data-testid="stButton"] button[kind="primary"] { background:#e5a400; color:#fff; border-color:#e5a400; }
    @media (max-width:720px) { .block-container { padding:1rem; } h1 { font-size:2rem!important; } .steps { grid-template-columns:1fr 1fr; } .trust-items { display:block; } }
    </style>
    """, unsafe_allow_html=True)


def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def money(value):
    value = number(value)
    if value is None: return "Unavailable"
    if abs(value) >= 1e12: return f"${value / 1e12:.2f}T"
    if abs(value) >= 1e9: return f"${value / 1e9:.2f}B"
    if abs(value) >= 1e6: return f"${value / 1e6:.2f}M"
    return f"${value:,.2f}"


def safe_text(value):
    replacements = {"✓":"[OK]", "₹":"Rs.", "—":"-", "–":"-", "“":'"', "”":'"', "’":"'", "…":"..."}
    text = str(value if value is not None else "N/A")
    for old, new in replacements.items(): text = text.replace(old, new)
    return text.encode("latin-1", "replace").decode("latin-1")


def safe_url(value):
    return value if isinstance(value, str) and value.startswith("https://") else None


def fetch_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info or {}
    history = stock.history(start=(datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"), end=datetime.now().strftime("%Y-%m-%d"))
    closes = pd.to_numeric(history.get("Close", pd.Series(dtype=float)), errors="coerce").dropna()
    price = number(info.get("currentPrice")) or number(info.get("regularMarketPrice")) or (number(closes.iloc[-1]) if not closes.empty else None)
    news = []
    try:
        for item in (stock.news or [])[:6]:
            content = item.get("content", item)
            title = content.get("title") or item.get("title")
            link = safe_url(content.get("canonicalUrl", {}).get("url") or content.get("clickThroughUrl", {}).get("url") or item.get("link"))
            publisher = content.get("provider", {}).get("displayName") or item.get("publisher") or "Yahoo Finance"
            published = content.get("pubDate") or item.get("providerPublishTime")
            if title:
                news.append({"title": title, "publisher": publisher, "url": link, "published": published})
    except Exception:
        news = []
    if not news:
        news = [{"title": "Recent market coverage was not available from the configured source.", "publisher": "Unavailable", "url": None, "published": None}]
    return {"ticker":ticker, "name":info.get("longName") or info.get("shortName") or ticker, "price":price, "market_cap":number(info.get("marketCap")), "history":closes, "info":info, "news":news, "fetched_at":datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z"), "market_source":f"https://finance.yahoo.com/quote/{quote(ticker)}", "filings_source":f"https://www.sec.gov/edgar/search/#/q={quote(ticker)}&dateRange=all"}


def kpis(data):
    info = data["info"]
    income = yf.Ticker(data["ticker"]).financials
    balance = yf.Ticker(data["ticker"]).balance_sheet
    revenue_growth = number(info.get("revenueGrowth"))
    margin = number(info.get("profitMargins"))
    if revenue_growth is not None: revenue_growth *= 100
    if margin is not None: margin *= 100
    if revenue_growth is None and income is not None and "Total Revenue" in income.index and income.shape[1] > 1:
        values = pd.to_numeric(income.loc["Total Revenue"], errors="coerce").dropna()
        if len(values) > 1 and values.iloc[1] != 0: revenue_growth = (values.iloc[0] - values.iloc[1]) / abs(values.iloc[1]) * 100
    if margin is None and income is not None and "Net Income" in income.index and "Total Revenue" in income.index:
        rev, net = number(income.loc["Total Revenue"].iloc[0]), number(income.loc["Net Income"].iloc[0])
        if rev: margin = net / rev * 100
    debt_equity = number(info.get("debtToEquity"))
    return {"P/E Ratio":number(info.get("trailingPE")) or number(info.get("forwardPE")), "Revenue Growth":revenue_growth, "Profit Margin":margin, "Debt / Equity":debt_equity}


def benchmark(primary, primary_kpis):
    peers = PEERS.get(primary, ["SPY", "QQQ"])
    rows = []
    for peer in peers:
        try: rows.append({"Ticker":peer, **kpis(fetch_data(peer))})
        except Exception: rows.append({"Ticker":peer, "P/E Ratio":None, "Revenue Growth":None, "Profit Margin":None, "Debt / Equity":None})
    return peers, pd.DataFrame([{"Ticker":primary, **primary_kpis}, *rows])


def risk_review(data, primary_kpis, comparison):
    risks = []
    missing = [label for label, value in primary_kpis.items() if value is None]
    if missing:
        risks.append(f"Missing source values: {', '.join(missing)}")
    margin = primary_kpis.get("Profit Margin")
    leverage = primary_kpis.get("Debt / Equity")
    if margin is not None and margin < 0:
        risks.append("Negative reported profit margin")
    if leverage is not None and leverage > 200:
        risks.append("Elevated debt-to-equity ratio")
    if len(data["history"]) > 20:
        volatility = float(data["history"].pct_change().dropna().std() * math.sqrt(252) * 100)
        if volatility > 45:
            risks.append(f"High annualized price volatility ({volatility:.1f}%)")
    else:
        volatility = None
        risks.append("Limited price history available")
    peer_count = max(len(comparison) - 1, 0)
    quality = "High" if not missing and peer_count >= 2 and data["price"] is not None else "Moderate" if data["price"] is not None else "Low"
    return {"quality":quality, "risks":risks, "volatility":volatility}


def granite(prompt):
    api_key, project, url = os.getenv("WATSONX_API_KEY"), os.getenv("WATSONX_PROJECT_ID"), os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    if not api_key or not project: return None, "Local analyst fallback"
    token = requests.post("https://iam.cloud.ibm.com/identity/token", data={"grant_type":"urn:ibm:params:oauth:grant-type:apikey", "apikey":api_key}, headers={"Content-Type":"application/x-www-form-urlencoded"}, timeout=30).json()["access_token"]
    endpoint = f"{url.rstrip('/')}/ml/v1/text/chat?version=2024-05-31"
    payload = {"model_id":os.getenv("GRANITE_MODEL", "ibm/granite-3-3-8b-instruct"), "project_id":project, "messages":[{"role":"user","content":prompt}], "temperature":.2, "max_tokens":500}
    result = requests.post(endpoint, json=payload, headers={"Authorization":f"Bearer {token}", "Content-Type":"application/json"}, timeout=90)
    result.raise_for_status()
    return result.json()["choices"][0]["message"]["content"], "IBM Granite"


def insight(ticker, data, table):
    news = "\n".join(f"- {x['title']} ({x['publisher']})" for x in data["news"])
    prompt = f"Act as an investment analyst. Review {ticker}. KPIs: {table.iloc[0].to_dict()}. News:\n{news}\nReturn exactly: SENTIMENT: Positive/Neutral/Negative\nSUMMARY: two concise sentences.\nVERDICT: Buy/Hold/Sell\nRATIONALE: two concise sentences."
    try: result, provider = granite(prompt)
    except Exception as exc: return {"sentiment":"Neutral", "summary":f"Granite was unavailable: {exc}", "verdict":"Hold", "rationale":"Review the available market data before acting.", "provider":"Fallback"}
    if not result: return {"sentiment":"Neutral", "summary":"News signals are mixed; review the cited sources.", "verdict":"Hold", "rationale":"The available indicators do not establish a decisive edge.", "provider":provider}
    def field(name, default):
        match = re.search(rf"{name}:\s*(.*?)(?=\n[A-Z]+:|$)", result, re.I | re.S)
        return match.group(1).strip() if match else default
    return {"sentiment":field("SENTIMENT", "Neutral"), "summary":field("SUMMARY", result), "verdict":field("VERDICT", "Hold").split()[0].capitalize(), "rationale":field("RATIONALE", result), "provider":provider}


def make_pdf(report):
    pdf = FPDF(); pdf.set_auto_page_break(True, 15); pdf.add_page(); width = pdf.epw
    pdf.set_font("Helvetica", "B", 18); pdf.cell(width, 12, safe_text("Meridian Investment Analyst Report"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 14); pdf.cell(width, 10, safe_text(f'{report["name"]} ({report["ticker"]})'), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10); pdf.cell(width, 8, safe_text(f'Current price: {money(report["price"])}    Market cap: {money(report["market_cap"])}'), new_x="LMARGIN", new_y="NEXT")
    for title, body in [("Sequential methodology", "Data gathering -> KPI validation -> peer benchmarking -> news sentiment -> recommendation"), ("Key performance indicators", "\n".join(f"{k}: {money(v) if k == 'P/E Ratio' and v is not None else ('N/A' if v is None else f'{v:.2f}') }" for k,v in report["kpis"].items()))]:
        pdf.ln(3); pdf.set_font("Helvetica", "B", 12); pdf.cell(width, 8, safe_text(title), new_x="LMARGIN", new_y="NEXT"); pdf.set_font("Helvetica", size=9); pdf.multi_cell(width, 6, safe_text(body))
    pdf.ln(3); pdf.set_font("Helvetica", "B", 12); pdf.cell(width, 8, "Peer benchmark", new_x="LMARGIN", new_y="NEXT"); pdf.set_font("Helvetica", size=8); pdf.multi_cell(width, 6, safe_text(report["benchmark"].to_string(index=False)))
    pdf.ln(3); pdf.set_font("Helvetica", "B", 12); pdf.cell(width, 8, "Sentiment and sources", new_x="LMARGIN", new_y="NEXT"); pdf.set_font("Helvetica", size=9); pdf.multi_cell(width, 6, safe_text(f'Sentiment: {report["insight"]["sentiment"]}\n{report["insight"]["summary"]}\nSources:\n' + "\n".join(f'- {x["title"]} | {x["publisher"]} | {x.get("url") or "No link"}' for x in report["news"])))
    pdf.ln(3); pdf.set_font("Helvetica", "B", 12); pdf.cell(width, 8, "Final recommendation", new_x="LMARGIN", new_y="NEXT"); pdf.set_font("Helvetica", size=9); pdf.multi_cell(width, 6, safe_text(f'{report["insight"]["verdict"]}: {report["insight"]["rationale"]}'))
    pdf.ln(3); pdf.set_font("Helvetica", "B", 12); pdf.cell(width, 8, "Transparency and feedback", new_x="LMARGIN", new_y="NEXT"); pdf.set_font("Helvetica", size=9); pdf.multi_cell(width, 6, safe_text(f'Provider: {report["insight"]["provider"]}\nData quality: {report["review"]["quality"]}\nFetched: {report["fetched_at"]}\nMarket source: {report["market_source"]}\nRegulatory filings: {report["filings_source"]}\nRisk flags: {"; ".join(report["review"]["risks"]) or "None detected"}\nRating: {report.get("rating", "Not submitted")} / 5\nComment: {report.get("feedback", "No comment")}\nThis report is educational research, not personalized financial advice.'))
    output = pdf.output(dest="S"); return output.encode("latin-1") if isinstance(output, str) else bytes(output)


def main():
    css()
    with st.sidebar:
        st.markdown('<div class="brand"><b>M</b> MERIDIAN</div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-note">Institutional-style research workspace for sequential market analysis.</div>', unsafe_allow_html=True)
        st.markdown("**Research controls**")
        ticker = st.text_input("Ticker symbol", "AAPL", max_chars=10, key="ticker_input").strip().upper()
        st.caption("Examples: AAPL, MSFT, NVDA, TSLA")
        st.markdown("**Coverage map**")
        st.markdown("Market data · fundamentals · peers · news · Granite")
        st.divider()
        st.markdown("**Methodology**")
        st.caption("Every run records source links, fetch time, data quality, automated risk checks, and analyst feedback.")
        st.link_button("Open SEC EDGAR", "https://www.sec.gov/edgar/search/")
    st.markdown('<div class="mast"><div class="brand"><b>M</b> MERIDIAN</div><div style="color:#66738a">Decision intelligence / v2</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">Sequential Task Agent / Problem Statement No. 4</div>', unsafe_allow_html=True)
    st.title("Investment Analyst")
    st.caption("From trusted public sources to a concise, auditable investment brief.")
    st.markdown('<div class="panel trust"><b>Why this workspace is different</b><div class="trust-items"><span><b>[OK]</b>Fresh market context</span><span><b>[OK]</b>Peer-relative KPIs</span><span><b>[OK]</b>Linked evidence</span><span><b>[OK]</b>Risk checks before recommendation</span></div></div>', unsafe_allow_html=True)
    if st.button("Run sequential analysis", type="primary"):
        if not ticker: st.error("Enter a ticker symbol."); return
        try:
            with st.status("Running sequential analyst workflow", expanded=True) as status:
                st.write("1 / 5 Gathering market data"); data = fetch_data(ticker)
                st.write("2 / 5 Calculating and validating KPIs"); primary_kpis = kpis(data)
                st.write("3 / 5 Benchmarking comparable companies"); peers, comparison = benchmark(ticker, primary_kpis)
                st.write("4 / 5 Analyzing news sentiment with Granite"); ai = insight(ticker, data, comparison)
                st.write("5 / 5 Preparing recommendation and report"); review = risk_review(data, primary_kpis, comparison); status.update(label="Sequential analysis complete", state="complete")
            report = {**data, "kpis":primary_kpis, "peers":peers, "benchmark":comparison, "insight":ai, "review":review, "news":data["news"]}; st.session_state.report = report
        except Exception as exc: st.error(f"Analysis failed: {exc}")
    report = st.session_state.get("report")
    if not report: return
    steps = ["Market data", "KPI validation", "Peer benchmark", "News sentiment", "Recommendation"]
    st.markdown('<div class="steps">' + ''.join(f'<div class="step done"><div class="step-num">0{i+1}</div><div class="step-name">{name}</div><div class="step-state">Complete</div></div>' for i,name in enumerate(steps)) + '</div>', unsafe_allow_html=True)
    verdict = report["insight"]["verdict"]
    st.markdown(f'<div class="hero"><div class="eyebrow" style="color:#b8c7ff">Executive brief / {html.escape(report["ticker"])}</div><h2>{html.escape(report["name"])}</h2><div class="muted">{html.escape(report["fetched_at"])} · {html.escape(report["insight"]["provider"])}</div><div class="hero-verdict">{html.escape(verdict)}</div><div class="hero-copy">{html.escape(report["insight"]["rationale"])}</div></div>', unsafe_allow_html=True)
    scores = st.columns(4)
    score_values = [("Current price", money(report["price"]), "Live quote"), ("Data quality", report["review"]["quality"], "Source coverage"), ("Risk flags", str(len(report["review"]["risks"])), "Automated checks"), ("Peer set", str(len(report["peers"])), "Comparable companies")]
    for col, (label, value, note) in zip(scores, score_values): col.markdown(f'<div class="score"><div class="score-label">{label}</div><div class="score-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)
    overview, fundamentals, evidence, report_tab = st.tabs(["Overview", "Fundamentals", "Evidence & risk", "Finalize report"])
    with overview:
        c1, c2 = st.columns([1.7, 1])
        with c1:
            st.markdown('<div class="section">Price context</div>', unsafe_allow_html=True)
            if not report["history"].empty: st.line_chart(report["history"], color="#315CFF")
        with c2:
            st.markdown('<div class="section">Recommendation</div>', unsafe_allow_html=True)
            tone = "positive" if verdict == "Buy" else "negative" if verdict == "Sell" else "neutral"
            st.markdown(f'<div class="callout {tone}"><div class="callout-title">{html.escape(verdict)}</div>{html.escape(report["insight"]["summary"])}</div>', unsafe_allow_html=True)
            st.markdown(f'[Open market source]({report["market_source"]})')
            st.markdown(f'[Open SEC filing search]({report["filings_source"]})')
    with fundamentals:
        st.markdown('<div class="section">Key performance indicators</div>', unsafe_allow_html=True)
        cols = st.columns(4)
        for col, (label, value) in zip(cols, report["kpis"].items()):
            shown = "N/A" if value is None else f"{value:.2f}"
            col.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{shown}</div><div class="metric-note {"warn" if value is None else ""}">{"Awaiting source data" if value is None else "Validated indicator"}</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="section">Peer benchmark</div>', unsafe_allow_html=True)
        st.dataframe(report["benchmark"], use_container_width=True, hide_index=True)
    with evidence:
        st.markdown('<div class="section">Market sentiment</div>', unsafe_allow_html=True)
        sentiment_tone = "positive" if "positive" in report["insight"]["sentiment"].lower() else "negative" if "negative" in report["insight"]["sentiment"].lower() else "neutral"
        st.markdown(f'<div class="callout {sentiment_tone}"><div class="callout-title">{html.escape(report["insight"]["sentiment"])}</div>{html.escape(report["insight"]["summary"])}</div>', unsafe_allow_html=True)
        st.markdown('<div class="section">Source ledger</div>', unsafe_allow_html=True)
        for item in report["news"]:
            link = f'<a href="{html.escape(item["url"])}" target="_blank">Open source</a>' if item.get("url") else '<span>Link unavailable</span>'
            st.markdown(f'<div class="source-card"><b>{html.escape(item["title"])}</b><br><span class="muted">{html.escape(item["publisher"])} · {html.escape(str(item.get("published") or "Recent"))}</span> · {link}</div>', unsafe_allow_html=True)
        st.markdown('<div class="section">Risk review</div>', unsafe_allow_html=True)
        risk_text = "No material automated flags detected." if not report["review"]["risks"] else " | ".join(report["review"]["risks"])
        volatility = "N/A" if report["review"]["volatility"] is None else f'{report["review"]["volatility"]:.1f}%'
        st.markdown(f'<div class="callout {"neutral" if report["review"]["risks"] else "positive"}"><div class="callout-title">Automated checks</div>{html.escape(risk_text)}<br><small>Annualized volatility: {volatility}. Review linked filings before acting.</small></div>', unsafe_allow_html=True)
    with report_tab:
        st.markdown('<div class="section">Finalize your research note</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.write("Rate the usefulness of this analysis")
            if "rating" not in st.session_state: st.session_state.rating = 0
            st.markdown('<div class="rating">', unsafe_allow_html=True); star_cols = st.columns(5)
            for i, col in enumerate(star_cols, 1):
                if col.button("★" if i <= st.session_state.rating else "☆", key=f"star_{i}", type="primary" if i <= st.session_state.rating else "secondary"): st.session_state.rating = i; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True); feedback = st.text_area("Feedback", placeholder="What should the analyst improve?", key="feedback")
            report["rating"] = st.session_state.rating; report["feedback"] = feedback
            try: st.download_button("Download finalized report (PDF)", data=make_pdf(report), file_name=f'{ticker}_meridian_report.pdf', mime="application/pdf")
            except Exception as exc: st.error(f"PDF generation failed: {exc}")


if __name__ == "__main__": main()
