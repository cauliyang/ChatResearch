from chat_research import paper, paper_with_image
from pathlib import Path
from loguru import logger


def test_paper():
    path = Path("test/demo.pdf")
    paper.Paper(path=path)


def test_paper_with_image():
    path = Path("test/demo.pdf")
    paper_instance = paper_with_image.Paper(path=path)
    for key, value in paper_instance.section_text_dict.items():
        logger.info(key, value)
        logger.info("*" * 40)
