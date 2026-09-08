"""
Degradation pipeline to simulate flatbed scans and mobile camera captures.
Pipeline:
PyMuPDF (render to image at target DPI) -> Pillow / NumPy (rotations, noise, shadow, blur, stamps) -> img2pdf -> PDF
"""
import io
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import pymupdf
import img2pdf
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


@dataclass
class DegradeConfig:
    dpi: int = 200
    rotation_angle: float = 0.0
    noise_sigma: float = 0.0
    blur_radius: float = 0.0
    brightness: float = 1.0
    contrast: float = 1.0
    jpeg_quality: int = 80
    grey_background: bool = False
    stamp_text: Optional[str] = None
    crease_line: bool = False
    shadow_edge: Optional[str] = None  # "left", "right", "top", "bottom"
    perspective_tilt: bool = False
    page_indices: Optional[List[int]] = None  # None = all pages


def _apply_perspective_tilt(img: Image.Image) -> Image.Image:
    """Applies a realistic mild keystoning / smartphone angle distortion."""
    w, h = img.size
    # Shrink top slightly, shift corners by 1-2%
    dx = int(w * 0.025)
    dy = int(h * 0.015)
    # (x0, y0, x1, y1, x2, y2, x3, y3)
    # top-left, top-right, bottom-right, bottom-left
    quad = (
        dx, dy,
        w - dx, 0,
        w, h,
        0, h - dy
    )
    return img.transform((w, h), Image.Transform.QUAD, data=quad, resample=Image.Resampling.BICUBIC, fillcolor=(255, 255, 255))


def _apply_gaussian_noise(img: Image.Image, sigma: float) -> Image.Image:
    """Adds zero-mean Gaussian noise to the image array."""
    if sigma <= 0:
        return img
    arr = np.array(img, dtype=np.float32)
    noise = np.random.normal(0, sigma, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def _apply_crease_line(img: Image.Image) -> Image.Image:
    """Draws a subtle paper fold crease line across the horizontal midpoint."""
    w, h = img.size
    draw = ImageDraw.Draw(img)
    y = int(h * 0.48)
    # Subtle dark line + subtle light highlight underneath
    draw.line([(0, y), (w, y)], fill=(200, 200, 200), width=1)
    draw.line([(0, y + 1), (w, y + 1)], fill=(245, 245, 245), width=1)
    return img


def _apply_shadow(img: Image.Image, edge: str = "left") -> Image.Image:
    """Simulates uneven lighting / mobile camera hand shadow on one edge."""
    w, h = img.size
    arr = np.array(img, dtype=np.float32)
    if edge == "left":
        # Darkness fades from left 25% of image
        shadow_w = int(w * 0.28)
        gradient = np.linspace(0.65, 1.0, shadow_w)  # 35% darker at leftmost
        arr[:, :shadow_w, :] *= gradient[np.newaxis, :, np.newaxis]
    elif edge == "top":
        shadow_h = int(h * 0.20)
        gradient = np.linspace(0.70, 1.0, shadow_h)
        arr[:shadow_h, :, :] *= gradient[:, np.newaxis, np.newaxis]
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def _apply_stamp(img: Image.Image, text: str) -> Image.Image:
    """Applies a realistic semi-faded red ink approval/received stamp."""
    w, h = img.size
    # Create an overlay for the stamp
    overlay = Image.new("RGBA", (360, 120), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Rounded rectangular border
    draw.rectangle([(6, 6), (354, 114)], outline=(190, 30, 30, 180), width=4)
    draw.text((30, 22), text, fill=(190, 30, 30, 190), font_size=42)
    draw.text((35, 75), "ACKNOWLEDGED / FILED", fill=(190, 30, 30, 160), font_size=18)
    
    # Rotate stamp ~ 12 degrees
    rotated = overlay.rotate(12, expand=True, resample=Image.Resampling.BICUBIC)
    
    # Paste stamp at top right margin
    img_rgba = img.convert("RGBA")
    paste_x = max(10, w - rotated.width - int(w * 0.08))
    paste_y = int(h * 0.06)
    img_rgba.paste(rotated, (paste_x, paste_y), rotated)
    return img_rgba.convert("RGB")


def scan_degrade(src_pdf_path: Path, dst_pdf_path: Path, config: DegradeConfig) -> None:
    """
    Renders src_pdf_path pages to images at config.dpi, applies physical scan/mobile artifacts,
    and encodes the degraded images back into dst_pdf_path.
    """
    doc = pymupdf.open(str(src_pdf_path))
    scale = config.dpi / 72.0
    matrix = pymupdf.Matrix(scale, scale)

    num_pages = len(doc)
    target_pages = config.page_indices if config.page_indices is not None else list(range(num_pages))
    processed_image_bytes = []

    for idx in target_pages:
        if idx >= num_pages:
            continue
        page = doc[idx]
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")

        # 1. Grey background tint (if simulating unbleached / cheap paper)
        if config.grey_background:
            grey_layer = Image.new("RGB", img.size, (244, 244, 242))
            img = Image.blend(img, grey_layer, 0.12)

        # 2. Stamp
        if config.stamp_text:
            img = _apply_stamp(img, config.stamp_text)

        # 3. Crease line
        if config.crease_line:
            img = _apply_crease_line(img)

        # 4. Shadow
        if config.shadow_edge:
            img = _apply_shadow(img, config.shadow_edge)

        # 5. Perspective tilt
        if config.perspective_tilt:
            img = _apply_perspective_tilt(img)

        # 6. Rotation / Skew (simulating feeder tilt or hand capture)
        if abs(config.rotation_angle) > 0.01:
            img = img.rotate(
                config.rotation_angle,
                resample=Image.Resampling.BICUBIC,
                expand=True,
                fillcolor=(255, 255, 255),
            )

        # 7. Brightness & Contrast
        if config.brightness != 1.0:
            img = ImageEnhance.Brightness(img).enhance(config.brightness)
        if config.contrast != 1.0:
            img = ImageEnhance.Contrast(img).enhance(config.contrast)

        # 8. Gaussian Blur (optical defocus or low-res lens)
        if config.blur_radius > 0:
            img = img.filter(ImageFilter.GaussianBlur(radius=config.blur_radius))

        # 9. Noise
        if config.noise_sigma > 0:
            img = _apply_gaussian_noise(img, config.noise_sigma)

        # 10. JPEG compression save to bytes
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=config.jpeg_quality, optimize=True)
        processed_image_bytes.append(buf.getvalue())

    doc.close()

    dst_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dst_pdf_path, "wb") as f:
        f.write(img2pdf.convert(processed_image_bytes))
