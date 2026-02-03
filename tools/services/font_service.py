import math
from datetime import datetime

from loguru import logger
from pixel_font_builder import FontBuilder, WeightName, SerifStyle, SlantStyle, WidthStyle, Glyph, opentype
from pixel_font_knife import glyph_file_util, glyph_mapping_util, kerning_util
from pixel_font_knife.glyph_file_util import GlyphFlavorGroup

from tools import configs
from tools.configs import path_define, options
from tools.configs.options import FontSize, LanguageFlavor, FontFormat


class DesignContext:
    @staticmethod
    def load(font_size: FontSize) -> DesignContext:
        glyph_files = {}
        for width_mode_dir_name in ('common', 'proportional'):
            context = glyph_file_util.load_context(path_define.glyphs_dir.joinpath(font_size, width_mode_dir_name))
            glyph_files.update(context)

        for mapping in configs.mappings:
            glyph_mapping_util.apply_mapping(glyph_files, mapping)

        return DesignContext(font_size, glyph_files)

    font_size: FontSize
    _glyph_files: dict[int, GlyphFlavorGroup]
    _alphabet: set[str] | None
    _kerning_values: dict[tuple[str, str], int] | None

    def __init__(
            self,
            font_size: FontSize,
            glyph_files: dict[int, GlyphFlavorGroup],
    ):
        self.font_size = font_size
        self._glyph_files = glyph_files
        self._alphabet = None
        self._kerning_values = None

    @property
    def alphabet(self) -> set[str]:
        if self._alphabet is None:
            self._alphabet = {chr(code_point) for code_point in self._glyph_files if code_point >= 0}
        return self._alphabet

    @property
    def kerning_values(self) -> dict[tuple[str, str], int]:
        if self._kerning_values is None:
            self._kerning_values = kerning_util.calculate_kerning_values(configs.kerning_config, self._glyph_files)
        return self._kerning_values

    def _create_builder(self, language_flavor: LanguageFlavor) -> FontBuilder:
        font_config = configs.font_configs[self.font_size]

        builder = FontBuilder()
        builder.font_metric.font_size = font_config.font_size_y
        builder.font_metric.horizontal_layout.ascent = font_config.ascent
        builder.font_metric.horizontal_layout.descent = font_config.descent
        builder.font_metric.vertical_layout.ascent = math.ceil(font_config.line_height / 2)
        builder.font_metric.vertical_layout.descent = -math.floor(font_config.line_height / 2)
        builder.font_metric.x_height = font_config.x_height
        builder.font_metric.cap_height = font_config.cap_height
        builder.font_metric.underline_position = font_config.underline_position
        builder.font_metric.underline_thickness = 1
        builder.font_metric.strikeout_position = font_config.strikeout_position
        builder.font_metric.strikeout_thickness = 1

        builder.meta_info.version = configs.version
        builder.meta_info.created_time = datetime.fromisoformat(f'{configs.version.replace('.', '-')}T00:00:00Z')
        builder.meta_info.modified_time = builder.meta_info.created_time
        builder.meta_info.family_name = f'Capsule Pixel {self.font_size}px {language_flavor}'
        builder.meta_info.weight_name = WeightName.REGULAR
        builder.meta_info.serif_style = SerifStyle.SANS_SERIF
        builder.meta_info.slant_style = SlantStyle.NORMAL
        builder.meta_info.width_style = WidthStyle.PROPORTIONAL
        builder.meta_info.manufacturer = 'TakWolf'
        builder.meta_info.designer = 'TakWolf'
        builder.meta_info.description = 'Open source Pan-CJK pixel font'
        builder.meta_info.copyright_info = 'Copyright (c) 2026, TakWolf (https://takwolf.com), with Reserved Font Name "Capsule Pixel"'
        builder.meta_info.license_info = 'This Font Software is licensed under the SIL Open Font License, Version 1.1'
        builder.meta_info.vendor_url = 'https://capsule-pixel-font.takwolf.com'
        builder.meta_info.designer_url = 'https://takwolf.com'
        builder.meta_info.license_url = 'https://github.com/TakWolf/capsule-pixel-font/blob/master/LICENSE-OFL'

        glyph_sequence = glyph_file_util.get_glyph_sequence(self._glyph_files, [language_flavor])
        for glyph_file in glyph_sequence:
            horizontal_offset_x = 0
            horizontal_offset_y = font_config.baseline - font_config.font_size_y - (glyph_file.height - font_config.font_size_y) // 2
            vertical_offset_x = -math.ceil(glyph_file.width / 2)
            vertical_offset_y = (font_config.font_size_y - glyph_file.height) // 2 - 1
            builder.glyphs.append(Glyph(
                name=glyph_file.glyph_name,
                horizontal_offset=(horizontal_offset_x, horizontal_offset_y),
                advance_width=glyph_file.width,
                vertical_offset=(vertical_offset_x, vertical_offset_y),
                advance_height=font_config.font_size_y,
                bitmap=glyph_file.bitmap.data,
            ))

        character_mapping = glyph_file_util.get_character_mapping(self._glyph_files, language_flavor)
        builder.character_mapping.update(character_mapping)

        builder.kerning_values.update(self.kerning_values)

        builder.opentype_config.fields_override.head_y_max = font_config.ascent
        builder.opentype_config.fields_override.head_y_min = font_config.descent

        return builder

    def make_fonts(self, font_formats: list[FontFormat]):
        path_define.outputs_dir.mkdir(parents=True, exist_ok=True)

        if len(font_formats) > 0:
            for language_flavor in options.language_flavors:
                builder = self._create_builder(language_flavor)
                for font_format in font_formats:
                    file_path = path_define.outputs_dir.joinpath(f'capsule-pixel-{self.font_size}px-{language_flavor}.{font_format}')
                    match font_format:
                        case 'otf.woff':
                            builder.save_otf(file_path, flavor=opentype.Flavor.WOFF)
                        case 'otf.woff2':
                            builder.save_otf(file_path, flavor=opentype.Flavor.WOFF2)
                        case 'ttf.woff':
                            builder.save_ttf(file_path, flavor=opentype.Flavor.WOFF)
                        case 'ttf.woff2':
                            builder.save_ttf(file_path, flavor=opentype.Flavor.WOFF2)
                        case _:
                            getattr(builder, f'save_{font_format}')(file_path)
                    logger.info("Make font: '{}'", file_path)


def load_design_contexts(font_sizes: list[FontSize]) -> dict[FontSize, DesignContext]:
    design_contexts = {font_size: DesignContext.load(font_size) for font_size in font_sizes}
    return design_contexts
