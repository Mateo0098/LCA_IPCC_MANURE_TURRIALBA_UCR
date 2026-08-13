"""Comparaciones cuantitativas reproducibles para la prosa académica."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Comparison:
    left_label: str
    left: float
    right_label: str
    right: float
    unit: str

    def __post_init__(self) -> None:
        if not self.unit.strip():
            raise ValueError("Toda comparación debe declarar una unidad.")
        if not all(math.isfinite(value) for value in (self.left, self.right)):
            raise ValueError("Los valores comparados deben ser finitos.")

    @property
    def difference_right_minus_left(self) -> float:
        return self.right - self.left

    @property
    def percentage_right_vs_left(self) -> float:
        if self.left == 0:
            raise ZeroDivisionError("No puede calcularse un porcentaje relativo con base cero.")
        return self.difference_right_minus_left / self.left * 100.0

    @property
    def higher_label(self) -> str | None:
        if self.left == self.right:
            return None
        return self.left_label if self.left > self.right else self.right_label

    @property
    def lower_label(self) -> str | None:
        if self.left == self.right:
            return None
        return self.right_label if self.left > self.right else self.left_label

    def assert_consistent(self, *, difference: float, percentage: float) -> None:
        if not math.isclose(difference, self.difference_right_minus_left, rel_tol=1e-12, abs_tol=1e-12):
            raise RuntimeError("El signo o valor de la diferencia no coincide con los valores comparados.")
        if not math.isclose(percentage, self.percentage_right_vs_left, rel_tol=1e-12, abs_tol=1e-12):
            raise RuntimeError("El porcentaje no coincide con los valores comparados.")
        if (difference > 0) != (percentage > 0) or (difference < 0) != (percentage < 0):
            raise RuntimeError("La diferencia absoluta y la porcentual tienen signos incompatibles.")

    def assert_rounding_unambiguous(self, decimals: int) -> None:
        if self.left != self.right and round(self.left, decimals) == round(self.right, decimals):
            raise RuntimeError(
                f"La comparación {self.left_label}/{self.right_label} queda ambigua con {decimals} decimales."
            )


def dominant(items: dict[str, float], *, decimals: int) -> tuple[str, float]:
    if not items:
        raise ValueError("No hay candidatos para determinar el valor dominante.")
    if any(not math.isfinite(value) for value in items.values()):
        raise ValueError("Los candidatos dominantes deben ser finitos.")
    ordered = sorted(items.items(), key=lambda item: item[1], reverse=True)
    if len(ordered) > 1 and round(ordered[0][1], decimals) == round(ordered[1][1], decimals):
        raise RuntimeError(f"La dominancia queda ambigua con {decimals} decimales: {ordered[:2]}.")
    return ordered[0]
