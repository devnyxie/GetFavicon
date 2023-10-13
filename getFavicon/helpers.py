from PIL import Image
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def detect_image_format_and_size(image_data):
    try:
        with Image.open(BytesIO(image_data)) as img:
            format = img.format
            width, height = img.size
            return format, width, height
    except IOError:
        return None, None, None
