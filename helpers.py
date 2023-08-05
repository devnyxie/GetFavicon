import pydantic
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

def generator(domain: pydantic.HttpUrl):
    message = domain.upper()[0]
    bgColor = "white"
    bgSize = (150,150)
    baseFont ="font/Roboto-Regular.ttf"
    font = ImageFont.truetype(baseFont, 150,)
    fontColor = "black"
    W, H = bgSize
    image = Image.new('RGB', bgSize, bgColor)
    draw = ImageDraw.Draw(image)
    _, _, w, h = draw.textbbox((0, 0), message, font=font)
    draw.text(((W - w) / 2, (H - h) / 2), message, font=font, fill=fontColor)
    export = BytesIO()
    image.save(export, 'PNG')
    return {"icon": export.getvalue(), "format": 'image/PNG'}

def detect_image_format(image_data):
    try:
        with Image.open(BytesIO(image_data)) as img:
            return img.format
    except IOError:
        return None
