__version__ = "0.1.0"
__PACKAGE_NAME__ = "chat-research"


from rich.traceback import install

from . import paper, paper_with_image, utils

install()

__all__ = ["paper", "paper_with_image", "utils"]
