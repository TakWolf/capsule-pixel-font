import yaml

from tools.configs import path_define
from tools.configs.options import FontSize


class FontConfig:
    @staticmethod
    def load(font_size: FontSize) -> FontConfig:
        data = yaml.safe_load(path_define.configs_dir.joinpath(f'font-{font_size}px.yml').read_bytes())
        font_size_x = data['font-size-x']
        font_size_y = data['font-size-y']
        assert font_size == f'{font_size_x}x{font_size_y}'
        canvas_size = data['canvas-size']
        baseline = data['baseline']
        ascent = data['ascent']
        descent = data['descent']
        x_height = data['x-height']
        cap_height = data['cap-height']
        underline_position = data['underline-position']
        strikeout_position = data['strikeout-position']
        return FontConfig(
            font_size,
            font_size_x,
            font_size_y,
            canvas_size,
            baseline,
            ascent,
            descent,
            x_height,
            cap_height,
            underline_position,
            strikeout_position,
        )

    font_size: FontSize
    font_size_x: int
    font_size_y: int
    canvas_size: int
    baseline: int
    ascent: int
    descent: int
    x_height: int
    cap_height: int
    underline_position: int
    strikeout_position: int

    def __init__(
            self,
            font_size: FontSize,
            font_size_x: int,
            font_size_y: int,
            canvas_size: int,
            baseline: int,
            ascent: int,
            descent: int,
            x_height: int,
            cap_height: int,
            underline_position: int,
            strikeout_position: int,
    ):
        self.font_size = font_size
        self.font_size_x = font_size_x
        self.font_size_y = font_size_y
        self.canvas_size = canvas_size
        self.baseline = baseline
        self.ascent = ascent
        self.descent = descent
        self.x_height = x_height
        self.cap_height = cap_height
        self.underline_position = underline_position
        self.strikeout_position = strikeout_position

    @property
    def line_height(self) -> int:
        return self.ascent - self.descent
