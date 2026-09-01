"""
Structured representation of Albert's portfolio
"""

from dataclasses import dataclass


@dataclass
class Holding:
    name: str
    asset_class: str  #"Acoes", "Fundos", "Renda Fixa"
    value: float  #R$ position value
    allocation_pct: float  #% of total portfolio
    stated_return_pct: float  #rentabilidade reported in the portfolio doc


TOTAL_INVESTIDO = 386_858.82

#Hand-encoded from "XP - Albert_s portfolio.txt"
HOLDINGS = [
    #Acoes (19.32% of portfolio) - these have live price data in the CSV,
    #so their return will be RECOMPUTED from price data rather than trusted
    #at face value (see profitability.py). stated_return_pct kept for reference.
    Holding("LREN3", "Acoes", 27_812.04, 8.91, -41.7),
    Holding("MRFG3", "Acoes", 15_432.89, 4.94, 43.5),
    Holding("ARZZ3", "Acoes", 10_923.72, 3.50, -31.05),
    Holding("HAPV3", "Acoes", 6_143.14, 1.97, -74.58),

    #Fundos de Investimento (67.71%) - no price-level data available (CSV
    #only covers listed stocks), so we carry the stated monthly return as-is.
    #This is a documented assumption/limitation, not a silent guess.
    Holding("Riza Lotus Plus Advisory FIC FIRF REF DI CP", "Fundos", 96_178.73, 30.81, 15.51),
    Holding("Brave I FIC FIM CP", "Fundos", 72_567.43, 23.24, 19.08),
    Holding("Trend Investback FIC FIRF Simples", "Fundos", 305.44, 0.10, 16.01),
    Holding("Truxt Long Bias Advisory FIC FIM", "Fundos", 12_522.05, 4.01, -12.13),
    Holding("STK Long Biased FIC FIA", "Fundos", 9_745.97, 3.12, -14.51),
    Holding("Constellation Institucional Advisory FIC FIA", "Fundos", 8_475.02, 2.71, -25.66),
    Holding("Ibiuna Hedge ST Advisory FIC FIM", "Fundos", 11_601.02, 3.72, 33.74),

    #Renda Fixa (12.97%)
    Holding("CDB Banco C6 Consignado S.A. - SET/2024", "Renda Fixa", 40_478.75, 12.97, None),
]

#Risk-profile-compatible product criteria, from "XP - Albert_s risk profile.txt"
#Used by recommend.py to check whether each holding actually fits Albert's
#"Moderado" profile, and to justify swap candidates from the CSV universe.
RISK_PROFILE = {
    "classification": "Moderado",
    "compatible_equity_criteria": "Acoes de empresas consolidadas com historico de pagamento de dividendos",
    "compatible_fixed_income_criteria": "Classificacao de credito BB+ ou superior",
    "horizon": "Medio a longo prazo",
}

#Which held stocks are NOT dividend-paying blue chips (per risk profile
#criteria). This is the crux of the buy/sell logic: these names may not fit
#Albert's stated risk profile at all, independent of recent performance.
#(Documented judgment call - HAPV3/ARZZ3/MRFG3 are mid-cap growth/cyclical
#names without a consistent dividend policy comparable to the CSV's blue-chip
#universe; LREN3 pays some dividends but is a higher-beta retail name.)
EQUITY_PROFILE_FIT = {
    "LREN3": "Parcial - paga dividendos mas e' varejo de alto beta",
    "MRFG3": "Nao - frigorifico ciclico, sem politica de dividendos consistente",
    "ARZZ3": "Nao - consumo discricionario de alto crescimento, dividend yield baixo",
    "HAPV3": "Nao - saude/crescimento, historico de prejuizo, sem dividendos relevantes",
}