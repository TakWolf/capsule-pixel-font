import math

from PIL import Image, ImageFont, ImageDraw
from PIL.ImageFont import FreeTypeFont
from loguru import logger

from tools import configs
from tools.configs import path_define
from tools.configs.options import FontSize, LanguageFlavor
from tools.services.font_service import DesignContext


def _load_font(font_size: FontSize, language_flavor: LanguageFlavor, scale: int = 1) -> FreeTypeFont:
    file_path = path_define.outputs_dir.joinpath(f'capsule-pixel-{font_size}px-{language_flavor}.otf.woff2')
    return ImageFont.truetype(file_path, configs.font_configs[font_size].font_size_y * scale)


def _draw_text(
        image: Image.Image,
        xy: tuple[float, float],
        text: str,
        font: FreeTypeFont,
        text_color: tuple[int, int, int, int] = (0, 0, 0, 255),
        shadow_color: tuple[int, int, int, int] | None = None,
        line_height: int | None = None,
        line_gap: int = 0,
        is_horizontal_centered: bool = False,
        is_vertical_centered: bool = False,
):
    draw = ImageDraw.Draw(image)
    x, y = xy
    default_line_height = sum(font.getmetrics())
    if line_height is None:
        line_height = default_line_height
    y += (line_height - default_line_height) / 2
    spacing = line_height + line_gap - font.getbbox('A')[3]
    if is_horizontal_centered:
        x -= draw.textbbox((0, 0), text, font=font)[2] / 2
    if is_vertical_centered:
        y -= line_height / 2
    if shadow_color is not None:
        draw.text((x + 1, y + 1), text, fill=shadow_color, font=font, spacing=spacing)
    draw.text((x, y), text, fill=text_color, font=font, spacing=spacing)


def _draw_text_background(
        image: Image.Image,
        alphabet: list[str],
        step: int,
        font_size_x: int,
        box_width: int,
        box_height: int,
        font: FreeTypeFont,
        text_color: tuple[int, int, int, int],
):
    draw = ImageDraw.Draw(image)
    alphabet = [c for c in alphabet if 0x4E00 <= ord(c) <= 0x9FFF]
    if not alphabet:
        alphabet.append('\u3000')
    count_x = math.ceil(image.width / box_width)
    count_y = math.ceil(image.height / box_height)
    offset_x = (image.width - count_x * box_width) / 2 + (box_width - font_size_x) / 2
    offset_y = (image.height - count_y * box_height) / 2 + (box_height - sum(font.getmetrics())) / 2
    alphabet_index = 0
    for y in range(count_y):
        for x in range(count_x):
            draw.text((offset_x + x * box_width, offset_y + y * box_height), alphabet[alphabet_index % len(alphabet)], fill=text_color, font=font)
            alphabet_index += step


def make_preview_image(font_size: FontSize):
    font_latin = _load_font(font_size, 'latin')
    font_zh_cn = _load_font(font_size, 'zh_cn')
    font_zh_tr = _load_font(font_size, 'zh_tr')
    font_ja = _load_font(font_size, 'ja')
    font_config = configs.font_configs[font_size]
    font_size_x = font_config.font_size_x
    line_height = font_config.line_height

    image = Image.new('RGBA', (font_size_x * 27, font_size_x * 2 + line_height * 9), (255, 255, 255, 255))
    _draw_text(image, (font_size_x, font_size_x), '胶囊像素字体 / Capsule Pixel Font', font_zh_cn)
    _draw_text(image, (font_size_x, font_size_x + line_height), '我们度过的每个平凡的日常，也许就是连续发生的奇迹。', font_zh_cn)
    _draw_text(image, (font_size_x, font_size_x + line_height * 2), '我們度過的每個平凡的日常，也許就是連續發生的奇蹟。', font_zh_tr)
    _draw_text(image, (font_size_x, font_size_x + line_height * 3), '日々、私たちが過ごしている日常は、', font_ja)
    _draw_text(image, (font_size_x, font_size_x + line_height * 4), '実は奇跡の連続なのかもしれない。', font_ja)
    _draw_text(image, (font_size_x, font_size_x + line_height * 5), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', font_latin)
    _draw_text(image, (font_size_x, font_size_x + line_height * 6), 'the quick brown fox jumps over a lazy dog.', font_latin)
    _draw_text(image, (font_size_x, font_size_x + line_height * 7), '0123456789', font_latin)
    _draw_text(image, (font_size_x, font_size_x + line_height * 8), '★☆☺☹♠♡♢♣♤♥♦♧☀☼♩♪♫♬☂☁⚓✈⚔☯', font_latin)
    image = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)

    path_define.outputs_dir.mkdir(parents=True, exist_ok=True)
    file_path = path_define.outputs_dir.joinpath(f'preview-{font_size}px.png')
    image.save(file_path)
    logger.info("Make preview image: '{}'", file_path)


def make_readme_banner(design_contexts: dict[FontSize, DesignContext]):
    font_x1 = _load_font('12x16', 'zh_cn')
    font_x2 = _load_font('12x16', 'zh_cn', 2)
    alphabet = sorted(design_contexts['12x16'].alphabet)
    font_config = configs.font_configs['12x16']
    line_height = font_config.line_height
    font_size_x = 12
    box_width = 14
    box_height = 18
    text_color = (255, 255, 255, 255)
    shadow_color = (80, 80, 80, 255)

    image_background = Image.open(path_define.images_dir.joinpath('readme-banner-background.png'))
    image = Image.new('RGBA', (image_background.width, image_background.height), (0, 0, 0, 0))
    _draw_text_background(image, alphabet, 50, font_size_x, box_width, box_height, font_x1, (200, 200, 200, 255))
    image.paste(image_background, mask=image_background)
    _draw_text(image, (image.width / 2, 36), '胶囊像素字体', font_x2, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 36 + line_height * 2 + 4), '★ 开源的泛中日韩像素字体 ★', font_x1, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)

    path_define.outputs_dir.mkdir(parents=True, exist_ok=True)
    file_path = path_define.outputs_dir.joinpath('readme-banner.png')
    image.save(file_path)
    logger.info("Make readme banner: '{}'", file_path)


def make_github_banner(design_contexts: dict[FontSize, DesignContext]):
    font_title = _load_font('12x16', 'zh_cn', 2)
    font_latin = _load_font('12x16', 'latin')
    font_zh_cn = _load_font('12x16', 'zh_cn')
    alphabet = sorted(design_contexts['12x16'].alphabet)
    font_config = configs.font_configs['12x16']
    line_height = font_config.line_height
    font_size_x = 12
    box_width = 14
    box_height = 18
    text_color = (255, 255, 255, 255)
    shadow_color = (80, 80, 80, 255)

    image_background = Image.open(path_define.images_dir.joinpath('github-banner-background.png'))
    image = Image.new('RGBA', (image_background.width, image_background.height), (0, 0, 0, 0))
    _draw_text_background(image, alphabet, 12, font_size_x, box_width, box_height, font_zh_cn, (200, 200, 200, 255))
    image.paste(image_background, mask=image_background)
    _draw_text(image, (image.width / 2, 50 + line_height), '胶囊像素字体 / Capsule Pixel Font', font_title, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 50 + line_height * 3), '★ 开源的泛中日韩像素字体 ★', font_zh_cn, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 50 + line_height * 5), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 50 + line_height * 6), 'the quick brown fox jumps over a lazy dog.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 50 + line_height * 7), '0123456789', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 50 + line_height * 8), '★☆☺☹♠♡♢♣♤♥♦♧☀☼♩♪♫♬☂☁⚓✈⚔☯', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)

    path_define.outputs_dir.mkdir(parents=True, exist_ok=True)
    file_path = path_define.outputs_dir.joinpath('github-banner.png')
    image.save(file_path)
    logger.info("Make github banner: '{}'", file_path)


def make_itch_io_banner(design_contexts: dict[FontSize, DesignContext]):
    font_x1 = _load_font('12x16', 'zh_cn')
    font_x2 = _load_font('12x16', 'zh_cn', 2)
    alphabet = sorted(design_contexts['12x16'].alphabet)
    font_config = configs.font_configs['12x16']
    line_height = font_config.line_height
    font_size_x = 12
    box_width = 14
    box_height = 18
    text_color = (255, 255, 255, 255)
    shadow_color = (80, 80, 80, 255)

    image_background = Image.open(path_define.images_dir.joinpath('itch-io-banner-background.png'))
    image = Image.new('RGBA', (image_background.width, image_background.height), (0, 0, 0, 0))
    _draw_text_background(image, alphabet, 38, font_size_x, box_width, box_height, font_x1, (200, 200, 200, 255))
    image.paste(image_background, mask=image_background)
    _draw_text(image, (image.width / 2, 38), '胶囊像素字体', font_x2, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 38 + line_height * 2 + 4), '★ 开源的泛中日韩像素字体 ★', font_x1, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)

    path_define.outputs_dir.mkdir(parents=True, exist_ok=True)
    file_path = path_define.outputs_dir.joinpath('itch-io-banner.png')
    image.save(file_path)
    logger.info("Make itch.io banner: '{}'", file_path)


def make_itch_io_cover():
    font_title = _load_font('12x16', 'zh_cn', 2)
    font_latin = _load_font('12x16', 'latin')
    font_zh_cn = _load_font('12x16', 'zh_cn')
    font_zh_tr = _load_font('12x16', 'zh_tr')
    font_ja = _load_font('12x16', 'ja')
    font_config = configs.font_configs['12x16']
    line_height = font_config.line_height
    text_color = (255, 255, 255, 255)
    shadow_color = (80, 80, 80, 255)

    image = Image.open(path_define.images_dir.joinpath('itch-io-cover-background.png'))
    _draw_text(image, (image.width / 2, 10), '胶囊像素字体', font_title, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 10 + line_height * 2), 'Capsule Pixel Font', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 3), '我们度过的每个平凡的日常，也许就是连续发生的奇迹。', font_zh_cn, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 4), '我們度過的每個平凡的日常，也許就是連續發生的奇蹟。', font_zh_tr, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 5), '日々、私たちが過ごしている日常は、', font_ja, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 6), '実は奇跡の連続なのかもしれない。', font_ja, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 7), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 8), 'the quick brown fox jumps over a lazy dog.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 9), '0123456789', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)

    path_define.outputs_dir.mkdir(parents=True, exist_ok=True)
    file_path = path_define.outputs_dir.joinpath('itch-io-cover.png')
    image.save(file_path)
    logger.info("Make itch.io cover: '{}'", file_path)


def make_afdian_cover():
    font_title = _load_font('12x16', 'zh_cn', 2)
    font_latin = _load_font('12x16', 'latin')
    font_zh_cn = _load_font('12x16', 'zh_cn')
    font_zh_tr = _load_font('12x16', 'zh_tr')
    font_ja = _load_font('12x16', 'ja')
    font_config = configs.font_configs['12x16']
    line_height = font_config.line_height
    text_color = (255, 255, 255, 255)
    shadow_color = (80, 80, 80, 255)

    image = Image.open(path_define.images_dir.joinpath('afdian-cover-background.png'))
    _draw_text(image, (image.width / 2, 16), '胶囊像素字体', font_title, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 16 + line_height * 2), 'Capsule Pixel Font', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 16 + line_height * 3), '★ 开源的泛中日韩像素字体 ★', font_zh_cn, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 16 + line_height * 5), '我们度过的每个平凡的日常，也许就是连续发生的奇迹。', font_zh_cn, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 16 + line_height * 6), '我們度過的每個平凡的日常，也許就是連續發生的奇蹟。', font_zh_tr, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 16 + line_height * 7), '日々、私たちが過ごしている日常は、', font_ja, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 16 + line_height * 8), '実は奇跡の連続なのかもしれない。', font_ja, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 16 + line_height * 10), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 16 + line_height * 11), 'the quick brown fox jumps over a lazy dog.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 16 + line_height * 12), '0123456789', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)

    path_define.outputs_dir.mkdir(parents=True, exist_ok=True)
    file_path = path_define.outputs_dir.joinpath('afdian-cover.png')
    image.save(file_path)
    logger.info("Make afdian cover: '{}'", file_path)
