from importlib import resources
from pathlib import Path

from .. import __PACKAGE_NAME__


def find_template_path():
    with resources.path(__PACKAGE_NAME__, "template") as f:
        template_path = f

    return Path(template_path) if isinstance(template_path, str) else template_path


def load_eis():
    template_path = find_template_path()
    return template_path / "eisvogel.tex"
