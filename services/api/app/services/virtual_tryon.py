import base64
import io
from typing import Tuple

from PIL import Image, ImageOps


def _ensure_rgba(image: Image.Image) -> Image.Image:
    if image.mode != "RGBA":
        return image.convert("RGBA")
    return image


def _scale_garment_to_torso(garment: Image.Image, frame_width: int, frame_height: int) -> Tuple[Image.Image, Tuple[int, int]]:
    garment = _ensure_rgba(garment)
    garment = ImageOps.contain(garment, (max(80, frame_width // 2), max(100, frame_height // 2)))

    target_width = int(frame_width * 0.58)
    target_height = int((garment.height / garment.width) * target_width)
    if target_height > frame_height * 0.7:
        target_height = int(frame_height * 0.7)
        target_width = int((garment.width / garment.height) * target_height)

    resized = garment.resize((target_width, target_height))
    x = int(frame_width * 0.23)
    y = int(frame_height * 0.17)
    return resized, (x, y)


def generate_virtual_tryon(person_image: Image.Image, garment_image: Image.Image) -> Image.Image:
    """Create a simple try-on preview by overlaying a cropped garment onto the torso area."""
    person = _ensure_rgba(person_image)
    garment = _ensure_rgba(garment_image)

    person = ImageOps.exif_transpose(person)
    garment = ImageOps.exif_transpose(garment)

    if person.size[0] == 0 or person.size[1] == 0:
        raise ValueError("Person image is empty.")
    if garment.size[0] == 0 or garment.size[1] == 0:
        raise ValueError("Garment image is empty.")

    composite = person.copy()
    resized_garment, (x_offset, y_offset) = _scale_garment_to_torso(garment, composite.width, composite.height)

    mask = resized_garment.getchannel("A")
    garment_rgb = resized_garment.convert("RGBA")
    composite.paste(garment_rgb, (x_offset, y_offset), mask)

    return composite


def image_to_base64(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"
