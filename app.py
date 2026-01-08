import pandas as pd
import gradio as gr

FALLBACK_RESPONSE = "Sorry can not find the answer"

# Load data
try:
    holdings_df = pd.read_csv("holdings.csv")
except:
    holdings_df = None

try:
    trades_df = pd.read_csv("trades.csv")
except:
    trades_df = None


def get_total_holdings(fund_name):
    if holdings_df is None or "fund_name" not in holdings_df.columns:
        return None
    df = holdings_df[holdings_df["fund_name"].str.lower() == fund_name.lower()]
    return len(df) if not df.empty else None


def get_total_trades(fund_name):
    if trades_df is None or "fund_name" not in trades_df.columns:
        return None
    df = trades_df[trades_df["fund_name"].str.lower() == fund_name.lower()]
    return len(df) if not df.empty else None


def get_yearly_pnl(year):
    required = {"fund_name", "trade_date", "pnl"}
    if trades_df is None or not required.issubset(trades_df.columns):
        return None

    df = trades_df.copy()
    df["trade_date"] = pd.to_datetime(df["trade_date"], errors="coerce")
    df["year"] = df["trade_date"].dt.year

    yearly = df[df["year"] == year]
    if yearly.empty:
        return None

    return yearly.groupby("fund_name")["pnl"].sum().sort_values(ascending=False)


def chatbot(question):
    q = question.lower()

    if holdings_df is not None:
        for fund in holdings_df["fund_name"].unique():
            if fund.lower() in q and "holding" in q:
                res = get_total_holdings(fund)
                return f"Total number of holdings for {fund} is {res}" if res else FALLBACK_RESPONSE

    if trades_df is not None:
        for fund in trades_df["fund_name"].unique():
            if fund.lower() in q and "trade" in q:
                res = get_total_trades(fund)
                return f"Total number of trades for {fund} is {res}" if res else FALLBACK_RESPONSE

    if "performed better" in q or "performance" in q:
        for year in range(2000, 2100):
            if str(year) in q:
                pnl = get_yearly_pnl(year)
                return f"In {year}, {pnl.idxmax()} performed better based on yearly Profit and Loss" if pnl is not None else FALLBACK_RESPONSE

    return FALLBACK_RESPONSE


demo = gr.Interface(
    fn=chatbot,
    inputs=gr.Textbox(label="Ask a question"),
    outputs=gr.Textbox(label="Answer"),
    title="Fund Data Chatbot",
    description="Answers strictly from uploaded files. No internet, no hallucination."
)

demo.launch()
