"""
Orchestrates the full pipeline: compute -> recommend -> narrate -> format.

Run with:
    export OPENAI_API_KEY="sk-..."
    python3 main.py
"""

from profitability import compute_holding_returns, compute_portfolio_return, compute_class_returns
from recommend import sell_reduce_candidates, buy_candidates, fixed_income_view
from portfolio_data import RISK_PROFILE
from build_letter import build_letter_docx
import narrative

CSV_PATH = "data/profitability_calc_wip.csv"


def main():
    #1. Real, traceable numbers
    holding_returns = compute_holding_returns(CSV_PATH)
    class_returns = compute_class_returns(holding_returns)
    portfolio_return = compute_portfolio_return(holding_returns)

    #2. Rule-based recommendations (NOT decided by the LLM)
    sells = sell_reduce_candidates(CSV_PATH)
    buys = buy_candidates(CSV_PATH)
    fi_note = fixed_income_view()

    with open("data/macro.txt", encoding="utf-8") as f:
        macro_raw = f.read()
    with open("data/risk_profile.txt", encoding="utf-8") as f:
        risk_raw = f.read()

    #3. Narrative generation (LLM only phrases decisions already made above)
    portfolio_para = narrative.portfolio_summary_pt(
        class_returns, portfolio_return,
        holdings_note="Retorno mensal recalculado via precos de mercado; fundos/renda fixa "
                       "carregam o retorno declarado no extrato (sem historico de preco disponivel).",
    )
    macro_para = narrative.macro_summary_pt(macro_raw)
    risk_summary = narrative.risk_profile_summary_pt(risk_raw)
    reco_para = narrative.recommendation_pt(sells, buys, fi_note, risk_summary)

    #4. Formatted output
    build_letter_docx(
        client_name="Albert",
        portfolio_paragraph=portfolio_para,
        macro_paragraph=macro_para,
        recommendation_paragraph=reco_para,
        advisor_name="Antonio Bicudo",
        output_path="outputs/carta_albert.docx",
    )
    print("Carta gerada em outputs/carta_albert.docx")


if __name__ == "__main__":
    main()