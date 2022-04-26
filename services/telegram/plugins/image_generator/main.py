from io import BytesIO
from typing import List
import random
import os
import time
import uuid

from PIL import Image, ImageDraw, ImageFont, ImageFile

W = 940
H = 788
SYMBOLS_ON_STRING = 20
TEXT_GRADIENT = False

FONT = ImageFont.truetype(
    "/app/services/telegram/plugins/image_generator/fonts/18524.ttf", 80
)
WATERMARK_TEXT = "@senior_software_engineer"
WATERMARK_COLOR = (0, 0, 0, 100)
WATERMARK_FONT = ImageFont.truetype(
    "/app/services/telegram/plugins/image_generator/fonts/oswald/Oswald-Light.ttf", 50
)


def add_text_watermark(d: ImageDraw.ImageDraw):
    return d.text(
        xy=(245, 630),
        text=WATERMARK_TEXT,
        fill=WATERMARK_COLOR,
        font=WATERMARK_FONT,
        align="center"
    )


def write_lines(text: List[str], image: Image.Image, font: ImageFont.ImageFont) -> Image.Image:
    img = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    gradient_shadow_step = 30

    rectangle_up_b = 150
    rectangle_down_b = 450
    rectangle_right_b = 930
    rectangle_left_b = 10

    if len(text) < 3:
        top = 170

        rectangle_up_b += 10
        rectangle_down_b -= 100

    elif len(text) == 3:
        top = 170

        # rectangle_up_b += 10
        # rectangle_down_b += 80

    elif len(text) == 4:
        top = 150
        gradient_shadow_step = 25

        rectangle_up_b -= 30
        rectangle_down_b += 80

    elif len(text) == 5:
        top = 130
        gradient_shadow_step = 20

        rectangle_up_b -= 60
        rectangle_down_b += 120

    else:
        top = 200
        gradient_shadow_step = 20

        rectangle_up_b -= 80
        rectangle_down_b += 180

    color_x, color_y, color_z, shadow = 255, 255, 255, 255

    strings_y_pos = range(top, 500, 80)
    string_index = 0

    # draw.rectangle(
    #     (rectangle_left_b, rectangle_down_b, rectangle_right_b, rectangle_up_b),
    #     fill=(0, 0, 0, shadow - 210), outline=(0, 0, 0, shadow - 210))

    for line in text:
        draw.text(
            ((W - draw.textsize(line, font=font)[0]) / 2, strings_y_pos[string_index]),
            line, font=font, fill=(color_x, color_y, color_z, shadow)
        )

        if TEXT_GRADIENT:
            shadow -= gradient_shadow_step

        string_index += 1
    # add_text_watermark(d)
    return Image.alpha_composite(image, img)


def update_increment_strings_indexes(indexes: List[int]):
    indexes.reverse()
    i = 0
    for index in indexes:
        if i == 0:
            indexes[i] += 1
        else:
            indexes[i] = indexes[0] + i
        i += 1

    return indexes


def formatted_text(text: str) -> List[str]:
    l_text = text.split(" ")
    index, iteration = 0, 0
    strings, buf = [], []

    while l_text:

        if len(" ".join(buf)) + len(l_text[0]) < SYMBOLS_ON_STRING:
            buf.append(l_text[0])

        else:
            buf.append(l_text[0])
            strings.append(" ".join(buf.copy()))
            buf.clear()

        del l_text[0]

    if buf:
        strings.append(" ".join(buf.copy()))

    return strings


def get_random_template_image_path() -> str:
    return f"{os.path.abspath('/app/services/telegram/plugins/image_generator/templates/')}/" \
           f"{random.choice(os.listdir(os.path.abspath('/app/services/telegram/plugins/image_generator/templates/')))}"


def create_image(img_template_path: str, text: str) -> BytesIO:
    img = write_lines(
        text=formatted_text(text=text),
        image=Image.open(img_template_path).convert("RGBA"),
        font=FONT
    )
    tg_img = BytesIO()
    tg_img.name = f"/app/services/telegram/plugins/image_generator/{str(uuid.uuid4())}.png"

    img.save(tg_img, optimize=True, quality=100)
    return tg_img

# img_bytes = create_image(
#     img_template_path=get_random_template_image_path(),
#     text=CONTENT_TEXT
# )
