__PACKAGE_NAME__ = "chat_research"


from rich.traceback import install

from . import areader, paper, paper_with_image, utils

install()

__all__ = ["paper", "paper_with_image", "utils", "areader"]
