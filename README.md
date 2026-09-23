# IBM_PROJECT_AI-Powered-Sequential-Investment-Analyst
IBM_Bob - – AI-Powered Sequential Investment Analyst using IBM Granite, RAG, and Agentic AI to automate financial research. It sequentially analyzes market data, KPIs, peer performance, news sentiment, and risks to generate evidence-based investment insights through an interactive Streamlit dashboard.



Investment Analyst Agent

An AI-powered Sequential Task Agent that analyzes a stock ticker step-by-step — fetching real financial data, computing KPIs, benchmarking against competitors, analyzing live news sentiment, and generating a final investment recommendation — with full transparency into how every step arrived at its answer.

Built for Problem Statement #4: Sequential Task Agent – Investment Analyst.

Why This Is Different

Most AI research tools (including commercial products like Stoxo) return a single "black box" answer — you get a conclusion, but not the reasoning trail behind it. This project takes the opposite approach:

Sequential, not parallel. Each agent's output is the literal input to the next — KPIs are calculated from the exact data fetched in Step 1, not computed independently. This is a true dependency chain, not five agents running in isolation and merging results.
Every step is inspectable. The "Pipeline Trail" tab shows exactly what each agent received, what it computed, and whether it used an LLM call or pure deterministic Python — so nothing is asserted without a visible basis.
Real, cited sources. News sentiment is drawn from live Google News RSS headlines with clickable source links — not hardcoded sample text.
Token-efficient by design. Only 2 of the 5 pipeline steps (Sentiment, Recommendation) make LLM calls. Data fetching, KPI math, and benchmarking are pure Python/pandas — zero token cost.
Pipeline Architecture
Ticker Input
     │
     ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌──────────────────┐
│ 1. Data      │──▶│ 2. KPI      │──▶│ 3. Benchmark │──▶│ 4. Sentiment │──▶│ 5. Recommendation │
│ Agent        │   │ Agent       │   │ Agent        │   │ Agent        │   │ Agent             │
│ (Python)     │   │ (Python)    │   │ (Python)     │   │ (LLM call)   │   │ (LLM call)        │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘   └──────────────────┘
  yfinance data      P/E, growth,      vs. 2 competitor   Live Google      Final verdict +
  fetch              margins, D/E      tickers            News RSS +      justification
                                                            LLM analysis
Step	Agent	Uses LLM?	Purpose
1	Data Agent	No	Fetches live price, market cap, and financials via yfinance
2	KPI Agent	No	Computes P/E ratio, revenue growth, profit margin, debt-to-equity
3	Benchmark Agent	No	Compares KPIs against 2 competitor tickers
4	Sentiment Agent	Yes (1 call)	Fetches real headlines (Google News RSS) and analyzes sentiment
5	Recommendation Agent	Yes (1 call)	Synthesizes all prior outputs into a final BUY/HOLD/AVOID verdict
Tech Stack
Frontend/UI: Streamlit (Python-only, no Node.js/npm required)
Orchestration: LangChain
LLM Provider: Configurable via a single file (llm_config.py) — currently set up for Groq (development) and designed to switch to IBM watsonx.ai / Granite for final submission
Financial Data: yfinance (free, no API key)
News Data: Google News RSS via feedparser (free, no API key)
Charts: Plotly
Project Structure
investment-analyst-agent/
├── agents/
│   ├── data_agent.py           # Fetches financial data (yfinance)
│   ├── kpi_agent.py             # Calculates KPIs (pure Python)
│   ├── benchmark_agent.py       # Competitor comparison (pure Python)
│   ├── sentiment_agent.py       # Real news + LLM sentiment analysis
│   └── recommendation_agent.py  # Final LLM-generated recommendation
├── llm_config.py                # Central LLM client — swap providers here only
├── orchestrator.py              # Runs all 5 agents in sequence
├── app.py                       # Streamlit UI (entry point)
├── requirements.txt
├── .env.example
└── README.md
Setup & Running Locally
bash
# 1. Clone the repo
git clone <your-repo-url>
cd investment-analyst-agent

# 2. Create and activate a virtual environment
python -m venv myenv
myenv\Scripts\activate        # Windows
# source myenv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env
# Open .env and add: GROQ_API_KEY=your_key_here

# 5. Run the app
python -m streamlit run app.py

The app opens automatically at http://localhost:8501.

Get a free Groq API key at console.groq.com.

Switching to IBM watsonx.ai / Granite

This project was deliberately structured so that swapping LLM providers requires editing exactly one file: llm_config.py.

To switch from Groq (development) to IBM watsonx.ai/Granite (submission):

Open llm_config.py
Replace the Groq client initialization with the IBM watsonx.ai client, using your watsonx.ai project ID, API key, and a Granite model (e.g. ibm/granite-13b-chat)
No other file needs to change — orchestrator.py and all files in agents/ call the LLM through this single config, regardless of provider
Limitations
Sentiment analysis is based on the 5 most recent headlines at the time of analysis — deeper historical sentiment trends are a natural next step.
Benchmarking currently compares against 2 hardcoded competitor tickers per stock; a future version could let users select competitors dynamically.
This tool provides AI-generated analysis for educational purposes only. It is not financial advice — always consult a licensed financial adviser before making investment decisions.
