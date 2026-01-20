from pathlib import Path

project_root_dir = Path(__file__).parent.joinpath('..', '..').resolve()

assets_dir = project_root_dir.joinpath('assets')
glyphs_dir = assets_dir.joinpath('glyphs')
