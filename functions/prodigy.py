from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap
import os
import random


def get_stars(level: int):

    if level == 1:
        return 0

    stars = round(0.0066 * level ** 3 + 0.348 * level ** 2 + 18.2 * level - 28.7)
    return stars


def get_level(stars: int):
    level = round(0.00000000183 * stars ** 3 - 0.0000152 * stars ** 2 + 0.0454 * stars + 1.72)
    return level


def noot(image, noot_face, text, footer=None):
    font = ImageFont.truetype('./resources/fonts/abeezee.ttf', 30)

    if noot_face == 'random':
        file = random.choice(os.listdir('./resources/noot'))
        noot_image = Image.open(f'./resources/noot/{file}')
    else:
        noot_image = Image.open(f'./resources/noot/{noot_face}.PNG')

    resize_y = round(noot_image.size[1] * image.size[0] / noot_image.size[0])
    noot_image = noot_image.resize(size=(image.size[0], resize_y))

    lines = textwrap.wrap(text, width=40)
    draw = ImageDraw.Draw(noot_image)
    y = 50

    for line in lines:
        draw.text((235, y), line, font=font, fill=(0, 0, 0))
        y += 45

    pasted = (0, image.size[1] - noot_image.size[1])
    image.paste(noot_image, pasted, noot_image)

    if footer is not None:
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('./resources/fonts/abeezee.ttf', 20)
        x = 900 - font.getsize(footer)[0]
        draw.text((x, image.size[1] - 40), footer, font=font, fill=(0, 0, 0))

    output_buffer = BytesIO()
    image.save(output_buffer, "png")
    output_buffer.seek(0)

    return output_buffer
