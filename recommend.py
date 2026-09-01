"""
Buy/Sell/Hold recommendation logic.

WHY THIS EXISTS:
v1 had zero recommendation logic - the final letter's "advice" was a generic,
copy-paste-able paragraph ("continue diversifying") that would fit almost any
client. This module produces recommendations that are actually specific to
Albert, grounded in three real inputs:
  1. His stated risk profile criteria (dividend-paying blue chips / BB+ fixed
     income) from the risk profile doc.
  2. Real monthly price performance from the CSV (see profitability.py).
  3. The macro backdrop (Selic at 15.5%, GDP slowing, equities pressured
     domestically) from the macro report.
"""

from portfolio_data import HOLDINGS, EQUITY_PROFILE_FIT
from profitability import compute_holding_returns, load_stock_prices

#the rule for 'sell_reduce_candidates' is an if/elif/else of two combined conditions
#mismatches_profile and cumulative_negative, the stock is marked as 'NAO' in EQUITY_PROFILE_FIT
#and the cumulative return since purchase is negative, if both are true -> REDUZIR/VENDER; if only one ->
#MONITORAR; if neither are true -> MANTER 
def sell_reduce_candidates(csv_path: str) -> list:
    holding_returns = compute_holding_returns(csv_path)
    by_name = {h.name: h for h in HOLDINGS}
    out = []
    for hr in holding_returns:
        if hr["asset_class"] != "Acoes":
            continue
        h = by_name[hr["name"]]
        fit = EQUITY_PROFILE_FIT.get(hr["name"], "n/a")
        cumulative_negative = h.stated_return_pct is not None and h.stated_return_pct < 0
        mismatches_profile = fit.startswith("Nao")
        if mismatches_profile and cumulative_negative:
            action = "REDUZIR/VENDER"
        elif mismatches_profile or fit.startswith("Parcial"):
            action = "MONITORAR"
        else:
            action = "MANTER"
        out.append({
            "name": hr["name"],
            "action": action,
            "profile_fit": fit,
            "cumulative_return_pct": h.stated_return_pct,
            "monthly_return_pct": hr["return_pct"],
            "allocation_pct": hr["allocation_pct"],
        })
    return out

#here we get every other stocks that arent on albert's portfolio, compute the cumulative return
#sort it from the biggest, filter the positives and return the top 3. The informations on the csv
#is the list of possible candidates to get into albert's portfolio
def buy_candidates(csv_path: str, top_n: int = 3) -> list:
    prices = load_stock_prices(csv_path)
    held_names = {h.name for h in HOLDINGS}
    candidates = []
    for name, p in prices.items():
        if name in held_names:
            continue
        monthly_return = (p["current"] / p["last_month"] - 1) * 100
        candidates.append({"name": name, "monthly_return_pct": monthly_return})
    candidates.sort(key=lambda c: c["monthly_return_pct"], reverse=True)
    positive_momentum = [c for c in candidates if c["monthly_return_pct"] > 0]
    return positive_momentum[:top_n]

#we took some informations for the macro doc to make this hardcoded text, as example we took the 15.50
#selic from the macro report, it is really some that we could improve
def fixed_income_view(macro_selic_terminal: float = 15.50) -> str:
    return (
        f"Com a Selic projetada em {macro_selic_terminal:.2f}% ao final do ciclo de aperto, "
        "instrumentos de renda fixa pos-fixados/atrelados a inflacao (como o CDB atual, IPCA+5,45%) "
        "oferecem retorno real atrativo com baixo risco - recomenda-se MANTER ou considerar AUMENTAR "
        "a alocacao em renda fixa de qualidade, aproveitando a janela de juros altos."
    )