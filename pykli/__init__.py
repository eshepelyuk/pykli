from xdg_base_dirs import xdg_config_home
from pygments.styles import get_style_by_name


CONFIG_DIR = xdg_config_home() / "pykli"

HISTORY_FILE = CONFIG_DIR / "history"

LOG_FILE = CONFIG_DIR / "pykli.log"

MONOKAI_STYLE = get_style_by_name('monokai')

CONFIG_DIR.mkdir(exist_ok=True, parents=True)
