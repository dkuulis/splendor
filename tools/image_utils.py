"""Shared image preparation for asset resizing tools (requires Pillow)."""

from PIL import Image


def load_cropped_rgba(source):
    """Load an RGBA image and crop transparent margins around visible pixels."""
    with Image.open(source) as original:
        image = original.convert("RGBA")
    # Ignore faint edge pixels when measuring the crop, but preserve the alpha
    # inside it. The source must already have a transparent background.
    bounds = image.getchannel("A").point(lambda alpha: 255 if alpha > 8 else 0).getbbox()
    if bounds is None:
        raise ValueError("Input image is fully transparent.")
    return image.crop(bounds)
