import base64
import os
from datetime import datetime

def save_base64_image(b64_string: str, name: str | None = None, output_dir: str = 'static') -> str:
    os.makedirs(output_dir, exist_ok=True)
    header, data = b64_string.split(',', 1)

    if 'image/png' in header:
        ext = 'png'
    elif 'image/jpeg' in header or 'image/jpg' in header:
        ext = 'jpg'
    elif 'image/webp' in header:
        ext = 'webp'
    else:
        raise ValueError('Unsupported image type')

    image_data = base64.b64decode(data)

    filename = f'{name}.{ext}' if name else f'{datetime.now().strftime("%Y%m%d%H%M%S%f")}.{ext}'
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'wb') as f:
        f.write(image_data)

    return filepath
