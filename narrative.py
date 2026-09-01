"""
Turns structured, already-computed data into client-facing Portuguese prose
via the OpenAI API.
"""

import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"

NO_GREETING_RULE = (
    " Nao inclua saudacao (ex: 'Prezado', 'Caro Albert') nem despedida "
    "(ex: 'Atenciosamente') - escreva APENAS o corpo do paragrafo, pois ele "
    "sera inserido dentro de uma carta que ja tem sua propria saudacao e "
    "despedida em outro lugar."
)
#we use it to not repeat the boilerpate of calling the API 4 times and we use a low temperature to
#not get creative answers on a finance doc
def _chat(system: str, user: str, temperature: float = 0.3) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content.strip()


def portfolio_summary_pt(class_returns: dict, portfolio_return: float, holdings_note: str) -> str:
    system = (
        "Voce e um analista financeiro escrevendo um paragrafo para uma carta mensal "
        "de investimentos em portugues do Brasil, tom profissional e claro. "
        "Use APENAS os numeros fornecidos abaixo - nao invente nenhum numero, "
        "nao mencione benchmark se nao for fornecido um valor de benchmark."
        + NO_GREETING_RULE
    )
    user = (
        f"Retorno total ponderado do mes: {portfolio_return:+.2f}%\n"
        f"Retorno por classe de ativo: {class_returns}\n"
        f"Contexto adicional: {holdings_note}\n\n"
        "Escreva 1-2 paragrafos client-facing resumindo a performance do mes."
    )
    return _chat(system, user)


def macro_summary_pt(macro_raw_text: str) -> str:
    system = (
        "Voce e um analista financeiro resumindo um relatorio macroeconomico para "
        "uma carta a um cliente, em portugues, 1 paragrafo, tom analitico mas acessivel. "
        "Ignore disclaimers legais e rodapes regulatorios do texto - foque apenas nos "
        "dados e projecoes macroeconomicas relevantes para decisoes de investimento."
        +NO_GREETING_RULE
    )
    return _chat(system, f"Relatorio macro bruto:\n\n{macro_raw_text[:6000]}")


def recommendation_pt(sell_list: list, buy_list: list, fixed_income_note: str, risk_profile_summary: str) -> str:
    system = (
        "Voce e um analista financeiro escrevendo a secao de recomendacoes de uma carta "
        "de investimentos, em portugues, para um cliente de perfil moderado. "
        "As decisoes de compra/venda JA FORAM TOMADAS por um motor de regras - "
        "seu trabalho e apenas explicar essas decisoes de forma fluida e justificada, "
        "NAO decidir novas recomendacoes nem inventar ativos que nao estao nas listas."
        +NO_GREETING_RULE
    )
    user = (
        f"Perfil do cliente: {risk_profile_summary}\n"
        f"Acoes a reduzir/vender (motivo: fora do perfil de risco + retorno acumulado negativo): {sell_list}\n"
        f"Acoes candidatas a compra (blue chips pagadoras de dividendos, momentum positivo no mes): {buy_list}\n"
        f"Visao sobre renda fixa: {fixed_income_note}\n\n"
        "Escreva 1-2 paragrafos de recomendacao, tom consultivo, sem jargao excessivo."
    )
    return _chat(system, user)


def risk_profile_summary_pt(risk_profile_raw_text: str) -> str:
    system = (
        "Resuma o perfil de risco do cliente abaixo em 1 frase curta, em portugues, "
        "para uso interno em outra secao da carta. Baseie-se apenas no texto fornecido."
    )
    return _chat(system, risk_profile_raw_text[:3000])