from chat_research import Paper
from pathlib import Path


def test_main():
    path = Path("test/demo.pdf")
    paper = Paper(path=path)
    paper.parse_pdf()
