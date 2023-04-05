# https://github.com/Wandmalfarbe/pandoc-latex-template
import asyncio
import shlex
import shutil
from pathlib import Path

import aiofiles
from loguru import logger


async def run(cmd) -> bool:
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    logger.trace(f"[{cmd!r} exited with {proc.returncode}]")
    if stdout:
        logger.trace(f"[stdout]\n{stdout.decode()}")
    if stderr:
        logger.error(f"[stderr]\n{stderr.decode()}")

    return True if proc.returncode == 0 else False


async def amd2pdf(md_file: Path, pdf_file: Path) -> bool:
    if shutil.which("pandoc") is None:
        raise FileNotFoundError("pandoc not found")

    cmd = [
        "pandoc",
        md_file.as_posix(),
        "-o",
        pdf_file.as_posix(),
    ]

    _cmd = shlex.join(cmd)
    is_success = await run(_cmd)

    if not is_success:
        logger.warning("failed to output pdf then fall back to md")

    return is_success


async def aexport(content: str, file_name: Path, keep_md: bool = False):
    if file_name.suffix == ".md" or file_name.suffix == ".txt":
        await aexport_to_markdown(content, file_name, mode="w")
    elif file_name.suffix == ".pdf":
        await aexport_to_pdf(content, file_name, mode="w", keep_md=keep_md)
    else:
        raise ValueError("Unsupported file format")


async def aexport_to_markdown(text: str, file_name, mode="w"):
    async with aiofiles.open(file_name, mode, encoding="utf-8") as f:
        await f.write(text)


async def aexport_to_pdf(text: str, file_name: Path, mode="w", keep_md: bool = False):
    await aexport_to_markdown(text, file_name.with_suffix(".md"), mode)
    flag = await amd2pdf(file_name.with_suffix(".md"), file_name.with_suffix(".pdf"))

    if flag:
        if not keep_md:
            file_name.with_suffix(".md").unlink()
