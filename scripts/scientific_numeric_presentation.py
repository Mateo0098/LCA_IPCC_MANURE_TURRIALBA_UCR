"""Presentación numérica científica para los productos académicos del TFG.

Este módulo solo transforma valores en texto visible. No participa en el
cálculo del inventario, la integración experimental ni la EICV.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from typing import Final


SUPERSCRIPT_DIGITS: Final = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


@dataclass(frozen=True)
class NumberFormat:
    """Regla editorial explícita para una familia de magnitudes."""

    significant_digits: int | None = None
    decimal_places: int | None = None
    scientific_below: float | None = 1e-3
    scientific_at_or_above: float | None = 1e6
    strip_trailing_zeros: bool = True
    explicit_sign: bool = False

    def __post_init__(self) -> None:
        if (self.significant_digits is None) == (self.decimal_places is None):
            raise ValueError(
                "Debe definirse exactamente una regla: cifras significativas o decimales."
            )
        if self.significant_digits is not None and self.significant_digits < 1:
            raise ValueError("Las cifras significativas deben ser positivas.")


# Convenciones editoriales generales. Las mediciones con resolución o
# incertidumbre conocida deben usar una regla específica en el consumidor.
CALCULATED: Final = NumberFormat(significant_digits=4)
CALCULATED_COMPACT: Final = NumberFormat(significant_digits=3)
PERCENTAGE: Final = NumberFormat(decimal_places=1, scientific_below=None)


def _decimal(value: object) -> Decimal:
    if isinstance(value, Decimal):
        number = value
    else:
        try:
            number = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValueError(f"No es una magnitud numérica finita: {value!r}") from exc
    if not number.is_finite():
        raise ValueError(f"No es una magnitud numérica finita: {value!r}")
    return number


def decimal_places_from_uncertainty(
    uncertainty: object, *, uncertainty_significant_digits: int = 2
) -> int:
    """Obtiene la posición decimal coherente con una incertidumbre disponible.

    No estima incertidumbre. Solo usa la magnitud ya proporcionada para escoger
    la última posición que se mostrará, de acuerdo con JCGM 100:2008, 7.2.6.
    """

    number = abs(_decimal(uncertainty))
    if number == 0:
        raise ValueError("Una incertidumbre nula no justifica resolución editorial.")
    exponent = number.adjusted() - uncertainty_significant_digits + 1
    return -exponent


def _quantize_significant(number: Decimal, digits: int) -> Decimal:
    if number == 0:
        return Decimal(0)
    quantum = Decimal(1).scaleb(number.copy_abs().adjusted() - digits + 1)
    return number.quantize(quantum, rounding=ROUND_HALF_EVEN)


def _group_integer(text: str) -> str:
    sign = ""
    if text.startswith("-"):
        sign, text = "−", text[1:]
    groups: list[str] = []
    while text:
        groups.append(text[-3:])
        text = text[:-3]
    return sign + "\u00a0".join(reversed(groups or ["0"]))


def _fixed_text(number: Decimal, decimal_places: int, strip_zeros: bool) -> str:
    quantum = Decimal(1).scaleb(-decimal_places)
    rounded = number.quantize(quantum, rounding=ROUND_HALF_EVEN)
    if rounded == 0:
        rounded = abs(rounded)
    visible_places = max(0, decimal_places)
    raw = f"{rounded:.{visible_places}f}"
    integer, separator, fraction = raw.partition(".")
    if strip_zeros and fraction:
        fraction = fraction.rstrip("0")
    grouped = _group_integer(integer)
    return grouped + ("," + fraction if separator and fraction else "")


def _scientific_text(number: Decimal, digits: int, strip_zeros: bool) -> str:
    if number == 0:
        return "0"
    exponent = number.copy_abs().adjusted()
    mantissa = number.scaleb(-exponent)
    mantissa = _quantize_significant(mantissa, digits)
    if abs(mantissa) >= 10:
        mantissa = mantissa / 10
        exponent += 1
    mantissa_text = _fixed_text(mantissa, digits - 1, strip_zeros)
    return f"{mantissa_text} × 10{str(exponent).translate(SUPERSCRIPT_DIGITS)}"


def format_number(value: object, rule: NumberFormat = CALCULATED) -> str:
    """Formatea una magnitud sin alterar su valor de origen."""

    number = _decimal(value)
    absolute = abs(number)
    use_scientific = number != 0 and (
        (rule.scientific_below is not None and absolute < Decimal(str(rule.scientific_below)))
        or (
            rule.scientific_at_or_above is not None
            and absolute >= Decimal(str(rule.scientific_at_or_above))
        )
    )
    if use_scientific:
        digits = rule.significant_digits or max(1, rule.decimal_places or 0)
        text = _scientific_text(number, digits, rule.strip_trailing_zeros)
    elif rule.significant_digits is not None:
        rounded = _quantize_significant(number, rule.significant_digits)
        places = max(0, -rounded.as_tuple().exponent)
        text = _fixed_text(rounded, places, rule.strip_trailing_zeros)
    else:
        text = _fixed_text(number, rule.decimal_places or 0, rule.strip_trailing_zeros)
        if number != 0 and text == "0":
            digits = max(1, rule.decimal_places or 0)
            text = _scientific_text(number, digits, rule.strip_trailing_zeros)
    if rule.explicit_sign and number > 0:
        return "+" + text
    return text


def fixed(
    value: object,
    decimal_places: int,
    *,
    explicit_sign: bool = False,
    strip_trailing_zeros: bool = True,
    scientific_below: float | None = None,
) -> str:
    """Atajo para mediciones o convenciones con posición decimal justificada.

    ``decimal_places`` puede ser negativo para redondear a decenas, centenas u
    órdenes superiores sin alterar el valor de origen.
    """

    return format_number(
        value,
        NumberFormat(
            decimal_places=decimal_places,
            scientific_below=scientific_below,
            scientific_at_or_above=None,
            strip_trailing_zeros=strip_trailing_zeros,
            explicit_sign=explicit_sign,
        ),
    )


def estimate_with_uncertainty(
    estimate: object,
    uncertainty: object,
    *,
    uncertainty_significant_digits: int = 2,
) -> str:
    """Presenta estimador y dispersión en una posición decimal compartida.

    La función no calcula ni interpreta la incertidumbre: únicamente formatea
    una dispersión ya disponible, incluso cuando su última posición justificada
    está a la izquierda de la unidad.
    """

    position = decimal_places_from_uncertainty(
        uncertainty,
        uncertainty_significant_digits=uncertainty_significant_digits,
    )
    return (
        f"{fixed(estimate, position, strip_trailing_zeros=False)} ± "
        f"{fixed(uncertainty, position, strip_trailing_zeros=False)}"
    )


def significant(
    value: object,
    digits: int = 4,
    *,
    explicit_sign: bool = False,
    scientific_below: float | None = 1e-3,
    scientific_at_or_above: float | None = 1e6,
) -> str:
    """Atajo para resultados derivados sin incertidumbre formal disponible."""

    return format_number(
        value,
        NumberFormat(
            significant_digits=digits,
            scientific_below=scientific_below,
            scientific_at_or_above=scientific_at_or_above,
            explicit_sign=explicit_sign,
        ),
    )


def axis_tick(value: float) -> str:
    """Etiqueta breve para ejes, con coma decimal y sin cero negativo."""

    if not math.isfinite(value):
        return ""
    absolute = abs(value)
    if value == 0:
        return "0"
    if absolute < 1e-3 or absolute >= 1e6:
        return significant(value, 3)
    if absolute >= 100:
        return fixed(value, 0)
    if absolute >= 10:
        return fixed(value, 1)
    if absolute >= 1:
        return fixed(value, 2)
    if absolute >= 0.1:
        return fixed(value, 2)
    return fixed(value, 4)
