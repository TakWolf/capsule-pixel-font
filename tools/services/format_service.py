from pixel_font_knife import glyph_file_util

from tools.configs import path_define, options
from tools.configs.options import FontSize


def format_glyphs(font_size: FontSize):
    for width_mode_dir_name in ('common', 'proportional'):
        width_mode_dir = path_define.glyphs_dir.joinpath(font_size, width_mode_dir_name)
        context = glyph_file_util.load_context(width_mode_dir)
        glyph_file_util.normalize_context(context, width_mode_dir, options.language_flavors)
