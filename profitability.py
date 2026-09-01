"""
Real monthly profitability calculation.
WHY THIS EXISTS:
v1 never touched csv_path at all. The final letter's "3.5%
total return, 0.2pp above benchmark" is not derived from anything - the LLM
invented it while "summarizing" the raw portfolio text dump. This module
replaces that with an actual weighted calculation from price data, and is
explicit about which parts are computed vs. carried from the source doc.
"""

import csv
from portfolio_data import HOLDINGS, TOTAL_INVESTIDO

#function responsible for reading the CSV file and converting it into a dictionary 
def load_stock_prices(csv_path: str) -> dict:
    prices = {}
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            prices[row["Asset"]] = {
                "current": float(row["Current price"]),
                "last_month": float(row["Last month price"]),
            }
    return prices

#for each albert's position compute_holding_returns asks "is this stock in the csv?"
#if so, we compute the percentage return
#else we use the number that was already on the statement bc we dont have their historical price
#we use source to compute exactly from which every number came from
def compute_holding_returns(csv_path: str) -> list:
    prices = load_stock_prices(csv_path)
    results = []
    for h in HOLDINGS:
        if h.asset_class == "Acoes" and h.name in prices:
            p = prices[h.name]
            computed_return = (p["current"] / p["last_month"] - 1) * 100
            source = "csv_price_data"
        else:
            computed_return = h.stated_return_pct
            source = "portfolio_doc_stated" if computed_return is not None else "no_return_data"
        results.append({
            "name": h.name,
            "asset_class": h.asset_class,
            "value": h.value,
            "allocation_pct": h.allocation_pct,
            "return_pct": computed_return,
            "source": source,
        })
    return results

#we cmpute the weighted average return across the portfolio, we divide it by weight total and not
#100% bc we have assets that dont generate return (CDB)
def compute_portfolio_return(holding_returns: list) -> float:
    """Allocation-weighted average return across the whole portfolio."""
    weighted_sum = 0.0
    weight_total = 0.0
    for h in holding_returns:
        if h["return_pct"] is None:
            continue
        weighted_sum += h["return_pct"] * h["allocation_pct"]
        weight_total += h["allocation_pct"]
    return weighted_sum / weight_total if weight_total else 0.0

#same logic as compute_portfolio but here we group by classes stocks / funds/ fixed income
def compute_class_returns(holding_returns: list) -> dict:
    by_class = {}
    for h in holding_returns:
        by_class.setdefault(h["asset_class"], {"weighted_sum": 0.0, "weight_total": 0.0})
        if h["return_pct"] is None:
            continue
        by_class[h["asset_class"]]["weighted_sum"] += h["return_pct"] * h["allocation_pct"]
        by_class[h["asset_class"]]["weight_total"] += h["allocation_pct"]
    return {
        cls: (v["weighted_sum"] / v["weight_total"] if v["weight_total"] else 0.0)
        for cls, v in by_class.items()
    }

