from xdg_base_dirs import xdg_config_home
from pygments.styles import get_style_by_name
import logging


CONFIG_DIR = xdg_config_home() / "pykli"

HISTORY_FILE = CONFIG_DIR / "history"

LOG_FILE = CONFIG_DIR / "pykli.log"

MONOKAI_STYLE = get_style_by_name('monokai')

CONFIG_DIR.mkdir(exist_ok=True, parents=True)

logging.basicConfig(level=logging.INFO,
    filename=LOG_FILE, filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.getLogger(__name__).setLevel(logging.DEBUG)

LOG = logging.getLogger(__name__)

