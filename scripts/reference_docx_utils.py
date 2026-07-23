from __future__ import annotations

import hashlib
from pathlib import Path


REFERENCE_DOCX_NAME = "TFG_ACV_Estiercol_MASTER.docx"
REGISTERED_REFERENCE_SHA256 = (
    "98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def get_reference_docx_path(project_root: Path) -> Path:
    reference_dir = project_root / "MASTER_escrito"
    if not reference_dir.is_dir():
        raise FileNotFoundError(
            "No existe la carpeta protegida de referencia: MASTER_escrito/"
        )

    docx_files = sorted(
        path
        for path in reference_dir.rglob("*")
        if path.is_file() and path.suffix.lower() == ".docx"
    )
    if len(docx_files) != 1:
        names = ", ".join(path.name for path in docx_files) or "ninguno"
        raise RuntimeError(
            "MASTER_escrito/ debe contener exactamente un archivo .docx. "
            f"Archivos encontrados: {names}"
        )

    reference_docx = docx_files[0]
    if reference_docx.name != REFERENCE_DOCX_NAME:
        raise RuntimeError(
            "El único archivo .docx de MASTER_escrito/ debe llamarse "
            f"{REFERENCE_DOCX_NAME}; se encontró {reference_docx.name}."
        )

    current_hash = sha256_file(reference_docx)
    if current_hash != REGISTERED_REFERENCE_SHA256:
        raise RuntimeError(
            "El hash SHA-256 del documento maestro protegido no coincide con el "
            f"registrado. Esperado: {REGISTERED_REFERENCE_SHA256}. "
            f"Encontrado: {current_hash}."
        )
    return reference_docx


def assert_reference_docx_intact(reference_docx: Path, before_hash: str) -> str:
    after_hash = sha256_file(reference_docx)
    if after_hash != before_hash:
        raise RuntimeError(
            "El documento maestro protegido cambió durante la generación. "
            f"Hash anterior: {before_hash}. Hash posterior: {after_hash}."
        )
    if after_hash != REGISTERED_REFERENCE_SHA256:
        raise RuntimeError(
            "El documento maestro protegido ya no coincide con el hash SHA-256 "
            f"registrado: {REGISTERED_REFERENCE_SHA256}."
        )
    return after_hash
