from __future__ import annotations

from docx import Document
from docx.oxml.ns import qn

from scripts.academic_word_math import add_symbol_definitions, add_word_equation


def _math_text(paragraph) -> str:
    return "".join(node.text or "" for node in paragraph._p.iter(qn("m:t")))


def test_numbered_equation_remains_native_omml_with_structural_tabs() -> None:
    document = Document()

    paragraph = add_word_equation(document, r"m_{\mathrm{A1}}=m_{\mathrm{entrada}}", number=1)

    assert paragraph.text.strip() == "(1)"
    assert _math_text(paragraph) == "mA1=mentrada"
    assert len(paragraph._p.xpath("./w:pPr/w:tabs/w:tab")) == 2
    assert len(paragraph._p.xpath(".//m:oMath")) == 1


def test_symbol_definitions_use_inline_omml_without_visible_latex() -> None:
    document = Document()

    paragraph = add_symbol_definitions(
        document,
        [
            (r"m_{\mathrm{A1}}", "es la masa anual de entrada (kg/año)"),
            (r"f_{\mathrm{N,húmeda}}", "es una fracción másica (kg N/kg; adimensional)"),
        ],
    )

    assert paragraph is not None
    assert paragraph.text.startswith("Donde:")
    assert "_" not in paragraph.text
    assert "\\mathrm" not in paragraph.text
    assert len(paragraph._p.xpath(".//m:oMath")) == 2
    assert [_math_text(paragraph)] == ["mA1fN,húmeda"]
