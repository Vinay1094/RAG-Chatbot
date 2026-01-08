import logging
import pandas as pd
import gradio as gr
try:
    from rapidfuzz import process, fuzz
    _HAS_FUZZY = True
except Exception:
    _HAS_FUZZY = False

FALLBACK_RESPONSE = "Sorry can not find the answer"


# Load data
def _load_csv_safe(path):
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def _sanitize_df(df):
    """Return a dataframe with normalized column names and canonical keys.

    Normalization rules:
    - lower-case, strip whitespace, replace spaces with underscores
    - map common fund columns (e.g., 'shortname', 'portfolioname', 'name') -> 'fund_name'
    - map 'tradedate' -> 'trade_date'
    """
    if df is None:
        return None

    # normalize column names
    new_cols = []
    for c in df.columns:
        nc = str(c).strip().lower().replace(" ", "_")
        new_cols.append(nc)
    df = df.copy()
    df.columns = new_cols

    # map common names to canonical names
    col_map = {}
    # fund name alternatives
    for alt in ("fund_name", "shortname", "short_name", "portfolio_name", "portfolioname", "name"):
        if alt in df.columns and "fund_name" not in df.columns:
            col_map[alt] = "fund_name"
            break

    # trade date
    if "tradedate" in df.columns and "trade_date" not in df.columns:
        col_map["tradedate"] = "trade_date"

    # common pnl column - try to preserve if present
    for alt in ("pnl", "pl_ytd", "pl", "pl_ytd"):
        if alt in df.columns and "pnl" not in df.columns:
            col_map[alt] = "pnl"
            break

    if col_map:
        df = df.rename(columns=col_map)

    return df


holdings_df = _load_csv_safe("holdings.csv")
trades_df = _load_csv_safe("trades.csv")

holdings_df = _sanitize_df(holdings_df)
trades_df = _sanitize_df(trades_df)

# setup logging for debugging queries
logging.basicConfig(
    filename="app_debug.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def _extract_fund_candidates(df):
    """Return a set of candidate fund names from likely columns.

    Looks for columns containing keywords like 'fund', 'name', 'short', 'portfolio', 'client'
    and collects unique non-null string values.
    """
    if df is None:
        return set()
    candidates = set()
    # prefer explicit fund-like columns first
    preferred = [
        "fund_name",
        "portfolio_name",
        "portfolioname",
        "shortname",
        "short_name",
        "portfolio",
        "strategyname",
        "strategy1name",
        "strategy2name",
    ]
    for col in preferred:
        if col in df.columns:
            try:
                vals = df[col].dropna().astype(str).unique()
                for v in vals:
                    s = v.strip()
                    if s:
                        candidates.add(s)
            except Exception:
                pass
    if candidates:
        return candidates

    # fallback: scan broader columns
    for col in df.columns:
        if any(k in col for k in ("fund", "name", "short", "portfolio", "client", "custodian")):
            try:
                vals = df[col].dropna().astype(str).unique()
                for v in vals:
                    s = v.strip()
                    if s:
                        candidates.add(s)
            except Exception:
                continue
    return candidates


_holdings_candidates = _extract_fund_candidates(holdings_df)
_trades_candidates = _extract_fund_candidates(trades_df)


def _find_best_fund(query: str, candidates: set, min_score: int = 70):
    """Return best matching fund from candidates using substring or fuzzy match."""
    if not candidates:
        return None, None
    q = query.lower()
    # exact word-boundary match first to avoid short-token false positives
    import re
    for c in sorted(candidates, key=lambda x: -len(x)):
        try:
            if not isinstance(c, str):
                continue
            pat = r"\b" + re.escape(c.lower()) + r"\b"
            if re.search(pat, q):
                return c, 100
        except Exception:
            continue

    # fuzzy fallback
    if _HAS_FUZZY:
        # extractOne returns (match, score, idx)
        match = process.extractOne(query, list(candidates), scorer=fuzz.token_set_ratio)
        if match and match[1] >= min_score:
            return match[0], int(match[1])

    return None, None


def get_total_holdings(fund_name: str):
    if holdings_df is None:
        return None
    # prefer canonical column
    if "fund_name" in holdings_df.columns:
        df = holdings_df[holdings_df["fund_name"].astype(str).str.lower() == fund_name.lower()]
        return len(df) if not df.empty else None

    # fallback: search across likely name-like columns
    cols = [c for c in holdings_df.columns if any(k in c for k in ("fund", "name", "short", "portfolio", "client"))]
    total = 0
    matched = False
    for col in cols:
        try:
            m = holdings_df[holdings_df[col].astype(str).str.lower() == fund_name.lower()]
            if not m.empty:
                total += len(m)
                matched = True
        except Exception:
            continue
    return total if matched else None


def get_total_trades(fund_name: str):
    if trades_df is None:
        return None
    if "fund_name" in trades_df.columns:
        df = trades_df[trades_df["fund_name"].astype(str).str.lower() == fund_name.lower()]
        return len(df) if not df.empty else None

    cols = [c for c in trades_df.columns if any(k in c for k in ("fund", "name", "short", "portfolio", "client"))]
    total = 0
    matched = False
    for col in cols:
        try:
            m = trades_df[trades_df[col].astype(str).str.lower() == fund_name.lower()]
            if not m.empty:
                total += len(m)
                matched = True
        except Exception:
            continue
    return total if matched else None


def get_yearly_pnl(year: int):
    # Preferred: trade-level pnl with trade_date
    if trades_df is not None and {"trade_date", "pnl"}.issubset(set(trades_df.columns)) and "fund_name" in trades_df.columns:
        df = trades_df.copy()
        df["trade_date"] = pd.to_datetime(df["trade_date"], errors="coerce")
        df["year"] = df["trade_date"].dt.year
        yearly = df[df["year"] == int(year)]
        if not yearly.empty:
            return yearly.groupby("fund_name")["pnl"].sum().sort_values(ascending=False)

    # Fallback: use holdings-level P/L columns (e.g., pl_ytd, pl_mtd, pl)
    if holdings_df is not None:
        # find a pnl-like column
        pnl_col = None
        for alt in ("pnl", "pl_ytd", "pl", "pl_ytd", "pl_mtd", "pl_qtd", "pl_dtd"):
            if alt in holdings_df.columns:
                pnl_col = alt
                break
        # find a fund-like column
        fund_col = None
        if "fund_name" in holdings_df.columns:
            fund_col = "fund_name"
        else:
            for c in holdings_df.columns:
                if any(k in c for k in ("fund", "name", "short", "portfolio", "client")):
                    fund_col = c
                    break

        if pnl_col and fund_col:
            try:
                series = holdings_df.groupby(holdings_df[fund_col].astype(str))[pnl_col].sum().sort_values(ascending=False)
                logging.info("Using holdings-level PnL fallback (no trade-level yearly PnL). Year filter ignored.")
                return series
            except Exception:
                return None

    return None


def get_overall_pnl():
    """Return overall PnL per fund (trade-level if available, else holdings-level)."""
    # trade-level overall
    if trades_df is not None and {"fund_name", "pnl"}.issubset(set(trades_df.columns)):
        try:
            return trades_df.groupby("fund_name")["pnl"].sum().sort_values(ascending=False)
        except Exception:
            pass

    # holdings-level fallback
    if holdings_df is not None:
        pnl_col = None
        for alt in ("pnl", "pl_ytd", "pl", "pl_mtd", "pl_qtd", "pl_dtd"):
            if alt in holdings_df.columns:
                pnl_col = alt
                break
        fund_col = "fund_name" if "fund_name" in holdings_df.columns else None
        if not fund_col:
            for c in holdings_df.columns:
                if any(k in c for k in ("fund", "name", "short", "portfolio", "client")):
                    fund_col = c
                    break

        if pnl_col and fund_col:
            try:
                return holdings_df.groupby(holdings_df[fund_col].astype(str))[pnl_col].sum().sort_values(ascending=False)
            except Exception:
                pass

    return None


def chatbot(question: str):

    q = question.lower()
    logging.info("Question received: %s", question)

    # holdings queries: search across candidate columns
    if "holding" in q or "holdings" in q:
        fund, score = _find_best_fund(question, _holdings_candidates)
        if fund:
            res = get_total_holdings(fund)
            logging.info("Matched holdings fund '%s' (score=%s) -> %s", fund, score, res)
            if res:
                return f"Total number of holdings for {fund} is {res}"
            return FALLBACK_RESPONSE

    # trades queries: search across candidate columns
    if "trade" in q or "trades" in q:
        fund, score = _find_best_fund(question, _trades_candidates)
        if fund:
            res = get_total_trades(fund)
            logging.info("Matched trades fund '%s' (score=%s) -> %s", fund, score, res)
            if res:
                return f"Total number of trades for {fund} is {res}"
            holdings_res = get_total_holdings(fund)
            if holdings_res:
                return f"No trade records found for {fund}. Holdings count: {holdings_res}"
            return FALLBACK_RESPONSE

        # if not found in trades candidates, try holdings candidates to provide alternate info
        fund_h, score_h = _find_best_fund(question, _holdings_candidates)
        if fund_h:
            holdings_res = get_total_holdings(fund_h)
            if holdings_res:
                return f"No trade records found; did you mean {fund_h}? Holdings count: {holdings_res}"
            return FALLBACK_RESPONSE

    # performance queries
    if "performed better" in q or "performance" in q or "performed" in q or "best" in q:
        years = [int(token) for token in q.split() if token.isdigit() and 1900 <= int(token) <= 2100]
        if years:
            year = years[0]
            pnl = get_yearly_pnl(year)
            if pnl is not None and not pnl.empty:
                return f"In {year}, {pnl.idxmax()} performed better based on yearly Profit and Loss"
            # fallback to overall if yearly not available
            overall = get_overall_pnl()
            if overall is not None and not overall.empty:
                return f"No trade-level yearly PnL for {year}; using available overall PnL. Top: {overall.idxmax()}"
            return FALLBACK_RESPONSE

        # no year specified -> use overall PnL
        overall = get_overall_pnl()
        if overall is not None and not overall.empty:
            return f"Overall top performer based on available PnL: {overall.idxmax()}"
        return FALLBACK_RESPONSE

    return FALLBACK_RESPONSE


demo = gr.Interface(
    fn=chatbot,
    inputs=gr.Textbox(label="Ask a question"),
    outputs=gr.Textbox(label="Answer"),
    title="Fund Data Chatbot",
    description="Answers strictly from uploaded files. No internet, no hallucination."
)


if __name__ == "__main__":
    demo.launch()


