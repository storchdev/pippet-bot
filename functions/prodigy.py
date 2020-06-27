import os
import random
import textwrap
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance


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
    new_image = image.copy()
    new_image.paste(noot_image, pasted, noot_image)

    if footer is not None:
        draw = ImageDraw.Draw(new_image)
        font = ImageFont.truetype('./resources/fonts/abeezee.ttf', 20)
        x = 900 - font.getsize(footer)[0]
        draw.text((x, new_image.size[1] - 40), footer, font=font, fill=(0, 0, 0))

    output_buffer = BytesIO()
    new_image.save(output_buffer, "png")
    output_buffer.seek(0)

    return output_buffer


def new_item(rarity, path, item_path, text):
    background = Image.open(path)
    enhancer = ImageEnhance.Brightness(background)
    background = enhancer.enhance(0.2)

    rarity_card = Image.open(f'./resources/rarity_cards/{rarity}.png')

    lines = textwrap.wrap(text, width=14)
    y = 20 if len(lines) > 1 else 35
    font = ImageFont.truetype('./resources/fonts/allerta.ttf', 40)
    draw = ImageDraw.Draw(rarity_card)
    center = rarity_card.size[0] / 2

    for line in lines:
        size = font.getsize(line)[0] / 2
        x = round(center - size)
        draw.text(xy=(x, y), text=line, fill=(0, 0, 0), font=font)

    y = round(background.size[1] / 3)
    x = round(rarity_card.size[0] * background.size[1] / rarity_card.size[1] / 3)
    rarity_card = rarity_card.resize(size=(x, y))

    pet_image = Image.open(item_path)
    mask = pet_image.convert(mode='RGBA').split()[3]

    center_x, center_y = round(rarity_card.size[0] / 2), round(rarity_card.size[1] / 2)
    size_x, size_y = round(pet_image.size[0] / 2), round(pet_image.size[1] / 2)
    x, y = center_x - size_x, center_y - size_y
    rarity_card.paste(pet_image, (x, y), mask)
    mask = rarity_card.convert(mode='RGBA').split()[3]

    center = round(background.size[0] / 2)
    size = round(rarity_card.size[0] / 2)
    x, y = center - size, 100
    background.paste(rarity_card, (x, y), mask)

    return background
