from typing import Literal, get_args

type FontSize = Literal[
    '12x16',
]
font_sizes = list[FontSize](get_args(FontSize.__value__))

type LanguageFlavor = Literal[
    'latin',
    'zh_cn',
    'zh_hk',
    'zh_tw',
    'zh_tr',
    'ja',
    'ko',
]
language_flavors = list[LanguageFlavor](get_args(LanguageFlavor.__value__))
