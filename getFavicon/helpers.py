from PIL import Image
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def detect_image_format(image_data):
    try:
        with Image.open(BytesIO(image_data)) as img:
            return img.format
    except IOError:
        return None
