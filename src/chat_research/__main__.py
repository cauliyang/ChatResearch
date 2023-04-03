import argparse
import sys
from typing import Any, Optional

from loguru import logger

from . import chat_arxiv, chat_config, chat_paper, chat_response, chat_reviewer


class RichArgParser(argparse.ArgumentParser):
    """RichArgParser."""

    def __init__(self, *args: Any, **kwargs: Any):
        """RichArgParser."""
        from rich.console import Console

        self.console = Console()
        super().__init__(*args, **kwargs)

    @staticmethod
    def _color_message(message: str, color: str = "green") -> str:
        """Color message."""
        import re

        pattern = re.compile(r"(?P<arg>-{1,2}[-|\w]+)")
        return pattern.sub(lambda m: f"[bold {color}]{m.group('arg')}[/]", message)

    def _print_message(self, message: Optional[str], file: Any = None) -> None:
        if message:
            self.console.print(self._color_message(message))


class RichHelpFormatter(argparse.HelpFormatter):
    """RichHelpFormatter."""

    def __init__(self, *args: Any, **kwargs: Any):
        """RichHelpFormatter."""
        super().__init__(*args, max_help_position=42, width=100, **kwargs)  # type: ignore


def cli():
    parser = RichArgParser(
        description="[red]chatre[/] Use ChatGPT to accelerate research",
        formatter_class=RichHelpFormatter,
    )

    subparser = parser.add_subparsers(
        title="subcommand",
        description="valid subcommand",
        dest="subcommand",
    )

    logger.remove()
    logger.add(
        sys.stdout,
        format="'<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
    )

    chat_reviewer_command = chat_reviewer.add_subcommand(subparser)
    chat_arxiv_command = chat_arxiv.add_subcommnd(subparser)
    chat_response_command = chat_response.add_subcommand(subparser)
    chat_paper_command = chat_paper.add_subcommand(subparser)
    chat_config_command = chat_config.add_subcommand(subparser)
    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        raise SystemExit

    if args.subcommand == chat_paper_command:
        chat_paper.cli(args)
    elif args.subcommand == chat_arxiv_command:
        chat_arxiv.cli(args)
    elif args.subcommand == chat_response_command:
        chat_response.cli(args)
    elif args.subcommand == chat_reviewer_command:
        chat_reviewer.cli(args)
    elif args.subcommand == chat_config_command:
        chat_config.cli(args)
    else:
        logger.error("Invalid subcommand")
        parser.print_help()
        raise SystemExit

    logger.success("Done")
