from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "Academic_documents" / "evidencia_fotografica" / "originales"
OUT_DIR = ROOT / "outputs" / "documentos_tfg" / "recursos_integral"

SYSTEM_PHOTO_FIGURE = OUT_DIR / "fig_fotografica_sistema_fisico.jpg"
SAMPLING_PHOTO_FIGURE = OUT_DIR / "fig_fotografica_muestreo_conservacion.jpg"
BIOENERGY_PHOTO_FIGURE = OUT_DIR / "fig_fotografica_bioenergia.jpg"
PHOTOGRAPHIC_FIGURES = (
    SYSTEM_PHOTO_FIGURE,
    SAMPLING_PHOTO_FIGURE,
    BIOENERGY_PHOTO_FIGURE,
)

PANEL_SIZE = (1100, 850)
GUTTER = 28
LABEL_HEIGHT = 74
BACKGROUND = (255, 255, 255)
BORDER = (60, 60, 60)


@dataclass(frozen=True)
class PhotoSpec:
    photo_id: str
    file_name: str
    sha256: str
    # Recorte normalizado aplicado después de corregir la orientación EXIF.
    crop: tuple[float, float, float, float] | None = None
    contain: bool = False


@dataclass(frozen=True)
class FigureSpec:
    output: Path
    panels: tuple[PhotoSpec, ...]


PHOTO_SPECS = {
    "F002": PhotoSpec(
        "F002",
        "IMG_20240729_091802452.jpg",
        "838f70ae091f7a6ec462d459072d731435a1bba270fb9923822f8bac301a95c8",
    ),
    "F003": PhotoSpec(
        "F003",
        "IMG_20240729_092803070.jpg",
        "b3e4f8ccef78caa786cf853259f584fe675c77ab9c62076439d9e7227588ef56",
    ),
    "F007": PhotoSpec(
        "F007",
        "IMG_20240927_112207937_HDR.jpg",
        "d0d92b565b5ff45f3b7f2ddc53ceb51d600cbd6ad94f028f9bb703c061b6c2c2",
        crop=(0.04, 0.08, 0.96, 0.84),
    ),
    "F009": PhotoSpec(
        "F009",
        "IMG_20240927_113823018_HDR.jpg",
        "27863032e82844619b21824cdceb0e6fd089706282a1a4580840b0bd3350bad7",
        crop=(0.03, 0.10, 0.97, 0.82),
    ),
    "F019": PhotoSpec(
        "F019",
        "20251110_084714.jpg",
        "2bbb128062f01e34dda2405b9754e3af690068f62034304c52235a55afe87026",
        # Elimina el rostro y conserva manos, recipiente, guantes y punto de toma.
        crop=(0.12, 0.47, 0.96, 0.96),
    ),
    "F021": PhotoSpec(
        "F021",
        "20251110_105840.jpg",
        "ffcf720e4dd3e7f7511ae269970c528a0d3d470c8fd99f9d523f38c7a5eed676",
        crop=(0.12, 0.12, 0.88, 0.90),
    ),
    "F022": PhotoSpec(
        "F022",
        "20251110_111758.jpg",
        "368b400937222ad6b4234746dfa5fbf4294286f52b327c7f16b51aeb4a37233d",
        crop=(0.16, 0.18, 0.88, 0.96),
    ),
    "F025": PhotoSpec(
        "F025",
        "20251110_112459.jpg",
        "fcb2007c58836e6c242f714decda1f9d231ecbaa2ffd70fd703dbe3dce7cf963",
        crop=(0.08, 0.05, 0.92, 0.94),
    ),
    "F029": PhotoSpec(
        "F029",
        "20251110_164018.jpg",
        "747d521b6cbf6a70b1b4363917d8f58ef8a88ddee598df86fa8152f482454bb3",
        crop=(0.10, 0.08, 0.94, 0.94),
    ),
    "F030": PhotoSpec(
        "F030",
        "20251111_084800.jpg",
        "4e0bc9286a6c79d4cc5907d0e8f914de7d1a6003056d4c8517b78c2d728fa67b",
        crop=(0.18, 0.28, 0.90, 0.84),
    ),
    "F036": PhotoSpec(
        "F036",
        "20260721_104251.jpg",
        "b4cb222cccaf85d8267e07f7e71234728780f959679183464826710be366bafc",
        contain=True,
    ),
    "F038": PhotoSpec(
        "F038",
        "20260721_171948.jpg",
        "a74517f20bb72153ce2bf195075d60da24840b5399d0a7cc8f501297078c176b",
        crop=(0.03, 0.06, 0.93, 0.94),
    ),
}


FIGURE_SPECS = (
    FigureSpec(
        SYSTEM_PHOTO_FIGURE,
        tuple(PHOTO_SPECS[key] for key in ("F002", "F003", "F007", "F009")),
    ),
    FigureSpec(
        SAMPLING_PHOTO_FIGURE,
        tuple(PHOTO_SPECS[key] for key in ("F019", "F021", "F022", "F025")),
    ),
    FigureSpec(
        BIOENERGY_PHOTO_FIGURE,
        tuple(PHOTO_SPECS[key] for key in ("F029", "F030", "F036", "F038")),
    ),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_sources() -> None:
    for spec in PHOTO_SPECS.values():
        source = SOURCE_DIR / spec.file_name
        if not source.is_file():
            raise FileNotFoundError(f"Falta el original fotográfico {spec.photo_id}: {source}")
        actual = sha256_file(source)
        if actual != spec.sha256:
            raise RuntimeError(
                f"El SHA-256 del original {spec.photo_id} no coincide: {actual} != {spec.sha256}"
            )


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _crop_normalized(
    image: Image.Image, crop: tuple[float, float, float, float] | None
) -> Image.Image:
    if crop is None:
        return image
    left, top, right, bottom = crop
    if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
        raise ValueError(f"Recorte normalizado inválido: {crop}")
    width, height = image.size
    box = (
        round(left * width),
        round(top * height),
        round(right * width),
        round(bottom * height),
    )
    return image.crop(box)


def _render_panel(spec: PhotoSpec, label: str) -> Image.Image:
    source = SOURCE_DIR / spec.file_name
    with Image.open(source) as raw:
        image = ImageOps.exif_transpose(raw).convert("RGB")
    image = _crop_normalized(image, spec.crop)

    content_size = (PANEL_SIZE[0], PANEL_SIZE[1] - LABEL_HEIGHT)
    if spec.contain:
        resized = ImageOps.contain(image, content_size, method=Image.Resampling.LANCZOS)
        content = Image.new("RGB", content_size, BACKGROUND)
        offset = (
            (content_size[0] - resized.width) // 2,
            (content_size[1] - resized.height) // 2,
        )
        content.paste(resized, offset)
    else:
        content = ImageOps.fit(
            image,
            content_size,
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )

    panel = Image.new("RGB", PANEL_SIZE, BACKGROUND)
    panel.paste(content, (0, LABEL_HEIGHT))
    draw = ImageDraw.Draw(panel)
    draw.rectangle((0, 0, PANEL_SIZE[0] - 1, PANEL_SIZE[1] - 1), outline=BORDER, width=3)
    draw.text((24, 14), label, fill=(0, 0, 0), font=_font(42))
    return panel


def generate_figure(spec: FigureSpec) -> None:
    if len(spec.panels) != 4:
        raise ValueError("Las figuras fotográficas se componen actualmente en una cuadrícula 2 × 2.")
    width = PANEL_SIZE[0] * 2 + GUTTER * 3
    height = PANEL_SIZE[1] * 2 + GUTTER * 3
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    for index, photo in enumerate(spec.panels):
        row, column = divmod(index, 2)
        x = GUTTER + column * (PANEL_SIZE[0] + GUTTER)
        y = GUTTER + row * (PANEL_SIZE[1] + GUTTER)
        panel = _render_panel(photo, f"({chr(ord('a') + index)})")
        canvas.paste(panel, (x, y))
    spec.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(
        spec.output,
        format="JPEG",
        quality=90,
        optimize=True,
        progressive=True,
        dpi=(300, 300),
    )


def generate_photographic_figures() -> tuple[Path, ...]:
    validate_sources()
    for spec in FIGURE_SPECS:
        generate_figure(spec)
    return PHOTOGRAPHIC_FIGURES


def main() -> None:
    generated = generate_photographic_figures()
    for path in generated:
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
