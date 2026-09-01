"""
Assembles the final client letter as a formatted .docx.
"""

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH


def build_letter_docx(
    client_name: str,
    portfolio_paragraph: str,
    macro_paragraph: str,
    recommendation_paragraph: str,
    advisor_name: str,
    output_path: str,
):
    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    doc.add_paragraph(f"Prezado {client_name},")
    intro = doc.add_paragraph(
        "Segue o relatorio mensal referente ao desempenho do seu portfolio, ao cenario "
        "macroeconomico e as recomendacoes alinhadas ao seu perfil de investidor."
    )

    doc.add_heading("Desempenho do Portfolio", level=2)
    doc.add_paragraph(portfolio_paragraph)

    doc.add_heading("Cenario Macroeconomico", level=2)
    doc.add_paragraph(macro_paragraph)

    doc.add_heading("Recomendacoes", level=2)
    doc.add_paragraph(recommendation_paragraph)

    doc.add_paragraph(
        "Estamos a disposicao para discutir os resultados e esclarecer qualquer duvida."
    )
    doc.add_paragraph("Atenciosamente,")
    sign = doc.add_paragraph(advisor_name)
    sign.alignment = WD_ALIGN_PARAGRAPH.LEFT

    doc.save(output_path)
