import uuid
from io import BytesIO
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont, ImageFile

W = 940
H = 788
SYMBOLS_ON_STRING = 20
FONT = ImageFont.truetype(
    "/home/codefather/PycharmProjects/telegram-cms/services/telegram/plugins/image_generator/fonts/18524.ttf", 80
    # "/app/services/telegram/plugins/image_generator/fonts/18524.ttf", 80
)
WATERMARK_TEXT = "@senior_software_engineer"
WATERMARK_COLOR = (0, 0, 0, 100)
WATERMARK_FONT = ImageFont.truetype(
    "/home/codefather/PycharmProjects/telegram-cms/services/telegram/plugins/image_generator/fonts/oswald/Oswald-Light.ttf",
    50
    # "/app/services/telegram/plugins/image_generator/fonts/oswald/Oswald-Light.ttf", 50
)


def create_image(avatar: bytes, text: str, size: Tuple[int, int]):
    template: Image.Image = Image.open('template.png').convert("RGBA")

    img = Image.new("RGBA", template.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    rectangle_up_b = 10
    rectangle_down_b = size[1] - 10
    rectangle_right_b = size[0] - 10
    rectangle_left_b = 10

    color_x, color_y, color_z, shadow = 48, 48, 48, 255

    # draw.rectangle(
    #     (rectangle_left_b, rectangle_down_b, rectangle_right_b, rectangle_up_b),
    #     fill=(color_x, color_y, color_z, shadow), outline=(color_x, color_y, color_z, shadow))

    tg_img = BytesIO()
    tg_img.name = f"/app/services/telegram/plugins/image_generator/{str(uuid.uuid4())}.png"

    img = Image.alpha_composite(template, img)
    img.save(f'1.png', optimize=True, quality=100)
    # img.show()


def get_image_size_from_text(len_t: int) -> (int, int):
    result = (400, 200)
    if len_t > 100:
        result = (400, 200 + int(len_t / 2))
    return result


text = 'False: I mean... it was ok when a 17 year old strolled his fat funky ass ' \
       'across state lines and killed people so I see not…'

avatar = open('avatar.jpg', 'rb')
create_image(avatar=avatar.read(), text=text, size=get_image_size_from_text(len(text)))
avatar.close()
