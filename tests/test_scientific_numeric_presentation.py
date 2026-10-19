from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from quantitative_comparison import Comparison  # noqa: E402
from scientific_numeric_presentation import (  # noqa: E402
    NumberFormat,
    decimal_places_from_uncertainty,
    fixed,
    format_number,
    significant,
)


class ScientificNumericPresentationTests(unittest.TestCase):
    def test_round_half_even_uses_decimal_values(self) -> None:
        self.assertEqual(fixed(Decimal("2.345"), 2, strip_trailing_zeros=False), "2,34")
        self.assertEqual(fixed(Decimal("2.355"), 2, strip_trailing_zeros=False), "2,36")

    def test_negative_small_value_is_not_hidden_as_negative_zero(self) -> None:
        shown = fixed(Decimal("-0.0004"), 3)
        self.assertEqual(shown, "−4 × 10⁻⁴")
        self.assertNotEqual(shown, "0")
        self.assertNotIn("−0", shown)

    def test_exact_zero_remains_zero(self) -> None:
        self.assertEqual(fixed(Decimal("0"), 3), "0")

    def test_small_nonzero_value_uses_scientific_notation(self) -> None:
        shown = significant(Decimal("0.000000174625098"), 3, explicit_sign=True)
        self.assertEqual(shown, "+1,75 × 10⁻⁷")
        self.assertNotEqual(shown, "0")

    def test_large_value_uses_readable_scientific_notation(self) -> None:
        self.assertEqual(significant(Decimal("12345678"), 4), "1,235 × 10⁷")

    def test_grouping_and_spanish_decimal_marker(self) -> None:
        rule = NumberFormat(decimal_places=2, scientific_below=None, scientific_at_or_above=None)
        self.assertEqual(format_number(Decimal("12345.67"), rule), "12\u00a0345,67")

    def test_uncertainty_only_controls_position_when_it_exists(self) -> None:
        self.assertEqual(decimal_places_from_uncertainty(Decimal("0.207")), 2)
        self.assertEqual(decimal_places_from_uncertainty(Decimal("1.646")), 1)
        with self.assertRaises(ValueError):
            decimal_places_from_uncertainty(0)

    def test_exact_identifiers_remain_outside_magnitude_formatter(self) -> None:
        exact_values = ["2026", "A1", "M2", "Tabla 7"]
        self.assertEqual(exact_values, ["2026", "A1", "M2", "Tabla 7"])

    def test_comparison_uses_unrounded_inputs_and_preserves_direction(self) -> None:
        comparison = Comparison("A", 0.0005945, "B", 0.0013557, "kg N-eq/kg")
        self.assertGreater(comparison.difference_right_minus_left, 0)
        self.assertGreater(comparison.percentage_right_vs_left, 0)
        self.assertEqual(significant(comparison.left, 4), "5,945 × 10⁻⁴")
        self.assertEqual(significant(comparison.right, 4), "0,001356")

    def test_formatting_is_idempotent_and_does_not_mutate_source(self) -> None:
        source = Decimal("90.789753984")
        first = significant(source, 4)
        second = significant(source, 4)
        self.assertEqual(first, second)
        self.assertEqual(source, Decimal("90.789753984"))


if __name__ == "__main__":
    unittest.main()
