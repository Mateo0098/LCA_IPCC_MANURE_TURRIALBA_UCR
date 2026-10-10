from __future__ import annotations

import csv
import hashlib
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_simapro_session_evidence import (  # noqa: E402
    EvidenceValidationError,
    validate_session_evidence,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_checksums(session_dir: Path, filenames: list[str]) -> None:
    with (session_dir / "SHA256SUMS.csv").open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=["filename", "sha256"])
        writer.writeheader()
        for filename in filenames:
            writer.writerow({"filename": filename, "sha256": _sha256(session_dir / filename)})


class SimaProSessionEvidenceTests(unittest.TestCase):
    def _session(self, temporary: str) -> Path:
        session_dir = Path(temporary) / "session"
        session_dir.mkdir()
        (session_dir / "README.md").write_text("# Sesión\n", encoding="utf-8")
        (session_dir / "captura.png").write_bytes(b"png evidence")
        (session_dir / "resultados.pdf").write_bytes(b"pdf evidence")
        _write_checksums(session_dir, ["README.md", "captura.png", "resultados.pdf"])
        return session_dir

    def test_valid_session_passes(self) -> None:
        with TemporaryDirectory() as temporary:
            result = validate_session_evidence(self._session(temporary))
            self.assertEqual(result.file_count, 3)
            self.assertEqual(result.png_count, 1)
            self.assertEqual(result.pdf_count, 1)

    def test_hash_mismatch_fails(self) -> None:
        with TemporaryDirectory() as temporary:
            session_dir = self._session(temporary)
            (session_dir / "captura.png").write_bytes(b"changed")
            with self.assertRaisesRegex(EvidenceValidationError, "Huella SHA-256 incorrecta"):
                validate_session_evidence(session_dir)

    def test_unlisted_file_fails(self) -> None:
        with TemporaryDirectory() as temporary:
            session_dir = self._session(temporary)
            (session_dir / "extra.txt").write_text("extra", encoding="utf-8")
            with self.assertRaisesRegex(EvidenceValidationError, "no declarados"):
                validate_session_evidence(session_dir)

    def test_duplicate_filename_fails(self) -> None:
        with TemporaryDirectory() as temporary:
            session_dir = self._session(temporary)
            checksum_path = session_dir / "SHA256SUMS.csv"
            with checksum_path.open("a", encoding="utf-8", newline="") as target:
                target.write(f"README.md,{_sha256(session_dir / 'README.md')}\n")
            with self.assertRaisesRegex(EvidenceValidationError, "Nombres duplicados"):
                validate_session_evidence(session_dir)

    def test_invalid_columns_fail(self) -> None:
        with TemporaryDirectory() as temporary:
            session_dir = self._session(temporary)
            (session_dir / "SHA256SUMS.csv").write_text("name,digest\n", encoding="utf-8")
            with self.assertRaisesRegex(EvidenceValidationError, "Columnas inválidas"):
                validate_session_evidence(session_dir)


if __name__ == "__main__":
    unittest.main()
