import shutil
import subprocess
from pathlib import Path

from loguru import logger


# https://github.com/Wandmalfarbe/pandoc-latex-template
def export(content: str, file_name: Path, keep_md: bool = False):
    if file_name.suffix == ".md" or file_name.suffix == ".txt":
        export_to_markdown(content, file_name, mode="w")
    elif file_name.suffix == ".pdf":
        export_to_pdf(content, file_name, mode="w", keep_md=keep_md)
    else:
        raise ValueError("Unsupported file format")


def combine_md(md_files: list[Path], output_file: Path):
    content = ""

    for i in md_files:
        with open(i, "r") as f:
            content += f.read()
        content += "\n"

    with open(output_file, "w") as f:
        f.write(content)


def md2pdf(md_file: Path, pdf_file: Path) -> bool:
    if shutil.which("pandoc") is None:
        raise FileNotFoundError("pandoc not found")

    cmd = [
        "pandoc",
        md_file,
        "-o",
        pdf_file,
    ]

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        logger.warning("failed to output pdf then fall back to md")
        return False
    else:
        return True


def export_to_markdown(text, file_name, mode="w"):
    # 使用markdown模块的convert方法，将文本转换为html格式
    # html = markdown.markdown(text)
    # 打开一个文件，以写入模式
    with open(file_name, mode, encoding="utf-8") as f:
        # 将html格式的内容写入文件
        f.write(text)


# WARN: https://github.com/Wandmalfarbe/pandoc-latex-template/issues/92
def export_to_pdf(text: str, file_name: Path, mode="w", keep_md: bool = False):
    export_to_markdown(text, file_name.with_suffix(".md"), mode)
    flag = md2pdf(file_name.with_suffix(".md"), file_name.with_suffix(".pdf"))

    if flag:
        if not keep_md:
            file_name.with_suffix(".md").unlink()
