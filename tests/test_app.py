import importlib
import app


def setup_module():
    # reload app to ensure dataframes are loaded fresh
    importlib.reload(app)


def test_total_holdings_garfield():
    res = app.get_total_holdings("Garfield")
    assert res == 221, f"expected 221 holdings for Garfield, got {res}"


def test_total_trades_holdco11():
    res = app.get_total_trades("HoldCo 11")
    assert res == 6, f"expected 6 trades for HoldCo 11, got {res}"


def test_chatbot_holdings_response():
    resp = app.chatbot("How many holdings does Garfield have?")
    assert "221" in resp, f"unexpected chatbot response: {resp}"


def test_overall_pnl_available():
    series = app.get_overall_pnl()
    assert series is not None and len(series) > 0
