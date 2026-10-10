"""Valida la integridad de una carpeta de evidencia presencial SimaPro."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


CHECKSUM_FILENAME = "SHA256SUMS.csv"
README_FILENAME = "README.md"
EXPECTED_COLUMNS = ["filename", "sha256"]
SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


class EvidenceValidationError(ValueError):
    """Indica que una carpeta de evidencia no supera el control de integridad."""


@dataclass(frozen=True)
class EvidenceValidationResult:
    session_dir: Path
    file_count: int
    png_count: int
    pdf_count: int


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _declared_path(session_dir: Path, filename: str) -> Path:
    relative = PurePosixPath(filename)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise EvidenceValidationError(f"Ruta de evidencia no permitida: {filename!r}")
    candidate = session_dir.joinpath(*relative.parts).resolve()
    try:
        candidate.relative_to(session_dir.resolve())
    except ValueError as exc:
        raise EvidenceValidationError(f"Ruta fuera de la carpeta de sesión: {filename!r}") from exc
    return candidate


def validate_session_evidence(session_dir: Path) -> EvidenceValidationResult:
    session_dir = Path(session_dir)
    if not session_dir.is_dir():
        raise EvidenceValidationError(f"No existe la carpeta de sesión: {session_dir}")

    readme_path = session_dir / README_FILENAME
    checksum_path = session_dir / CHECKSUM_FILENAME
    if not readme_path.is_file():
        raise EvidenceValidationError(f"Falta {README_FILENAME} en {session_dir}")
    if not checksum_path.is_file():
        raise EvidenceValidationError(f"Falta {CHECKSUM_FILENAME} en {session_dir}")

    with checksum_path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise EvidenceValidationError(
                f"Columnas inválidas en {CHECKSUM_FILENAME}: {reader.fieldnames}; "
                f"se esperaban {EXPECTED_COLUMNS}"
            )
        rows = list(reader)

    filenames = [row["filename"] for row in rows]
    duplicates = sorted({name for name in filenames if filenames.count(name) > 1})
    if duplicates:
        raise EvidenceValidationError(f"Nombres duplicados en {CHECKSUM_FILENAME}: {duplicates}")

    declared = set(filenames)
    actual = {
        path.relative_to(session_dir).as_posix()
        for path in session_dir.rglob("*")
        if path.is_file() and path != checksum_path
    }
    if declared != actual:
        missing = sorted(declared - actual)
        unlisted = sorted(actual - declared)
        raise EvidenceValidationError(
            "El inventario SHA-256 no coincide con la carpeta: "
            f"ausentes={missing}, no declarados={unlisted}"
        )

    for row in rows:
        filename = row["filename"]
        expected_digest = row["sha256"]
        if not SHA256_PATTERN.fullmatch(expected_digest):
            raise EvidenceValidationError(f"Huella SHA-256 inválida para {filename}")
        evidence_path = _declared_path(session_dir, filename)
        if not evidence_path.is_file():
            raise EvidenceValidationError(f"Archivo declarado pero ausente: {filename}")
        actual_digest = sha256(evidence_path)
        if actual_digest != expected_digest.lower():
            raise EvidenceValidationError(
                f"Huella SHA-256 incorrecta para {filename}: "
                f"esperada={expected_digest.lower()}, obtenida={actual_digest}"
            )

    return EvidenceValidationResult(
        session_dir=session_dir,
        file_count=len(actual),
        png_count=sum(name.lower().endswith(".png") for name in actual),
        pdf_count=sum(name.lower().endswith(".pdf") for name in actual),
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Valida README, inventario y huellas SHA-256 de una sesión SimaPro."
    )
    parser.add_argument("session_dir", type=Path, help="Carpeta de evidencia de la sesión")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = validate_session_evidence(args.session_dir)
    except EvidenceValidationError as exc:
        print(f"VALIDACIÓN EVIDENCIA SIMAPRO: FAIL — {exc}", file=sys.stderr)
        return 1
    print(
        "VALIDACIÓN EVIDENCIA SIMAPRO: PASS — "
        f"{result.file_count} archivos; {result.png_count} PNG; {result.pdf_count} PDF"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
