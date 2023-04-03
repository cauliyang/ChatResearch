import toml
from loguru import logger

from .utils import CONFIG_FILE_NAME


def create_config_file():
    config = {
        "OpenAI": {"OPENAI_API_KEYS": ["sk-key1", "sk-key2"]},
        "Gitee": {
            "api": "your_gitee_api",
            "owner": "your_gitee_name",
            "repo": "your_repo_name",
            "path": "files_name_in_your_repo",
        },
    }
    with open(CONFIG_FILE_NAME, "w") as f:
        toml.dump(config, f)


def add_subcommand(parse):
    name = "config"
    _ = parse.add_parser(name, help="Generate configuration file")
    return name


def cli(args):
    create_config_file()
    logger.success("apikey.toml created")
