from xdg_base_dirs import xdg_config_home
from pygments.styles import get_style_by_name


CONFIG_DIR = xdg_config_home() / "pykli"

MONOKAI_STYLE = get_style_by_name('monokai')
