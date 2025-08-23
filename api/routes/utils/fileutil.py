import base64
from io import BytesIO
from pathlib import Path

from PIL import Image


def save_base64_image(base64_str: str, file_path: str) -> str | None:
    """
    Convert and save a Base64 image string to a file.
    Auto-detects image type and appends extension if missing.

    Args:
        base64_str (str): Base64 encoded image string (with or without data:image/...;base64, prefix).
        file_path (str): Path to save the decoded image (extension optional).

    Returns:
        str: The path where the image was saved if successful.
        None: If decoding fails or type can't be detected.
    """
    try:
        if "," in base64_str:
            base64_str = base64_str.split(",", 1)[1]

        image_data = base64.b64decode(base64_str)

        image = Image.open(BytesIO(image_data))
        assert image.format is not None, "Could not determine image format"
        ext = image.format.lower()
        
        file_path = f"{file_path}.{ext}"
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(file_path)

        return file_path
    except Exception as e:
        print(f"Failed to save image: {e}")
        return None
