from pathlib import Path

import toml
from loguru import logger

from ..utils import CONFIG_FILE_NAME

DEFAULT_CONFIG = {
    "OpenAI": {"OPENAI_API_KEYS": ["sk-key1", "sk-key2"]},
    "Gitee": {
        "api": "your_gitee_api",
        "owner": "your_gitee_name",
        "repo": "your_repo_name",
        "path": "files_name_in_your_repo",
    },
}

MAP_NAMES = {"OPENAI_API_KEY": "OPENAI_API_KEYS"}


def create_config_file(config=DEFAULT_CONFIG, file: Path = Path(CONFIG_FILE_NAME)):
    with open(file, "w") as f:
        toml.dump(config, f)


def read_key_value_pair(pairs: list[str]) -> dict[str, str]:
    result = {}
    for pair in pairs:
        key, value = pair.split("=")
        if key not in MAP_NAMES.keys():
            logger.warning(f"Key {key} is not a valid key in {MAP_NAMES.keys()}")
            raise SystemExit
        result[MAP_NAMES[key]] = value

    return result


def add_subcommand(parse):
    name = "config"
    subparser = parse.add_parser(name, help="Generate configuration file")
    subparser.add_argument(
        "set",
        metavar="key=value",
        nargs="*",
        action="extend",
        help="Set a number of key value pairs for configuration.",
    )

    return name


def cli(args):
    if args.set:
        default_path = Path.cwd() / CONFIG_FILE_NAME
        global_path = Path.home() / ".config" / CONFIG_FILE_NAME
        key_value_pairs = read_key_value_pair(args.set)

        if default_path.exists():
            config = toml.load(default_path)
            path = default_path
        elif global_path.exists():
            config = toml.load(global_path)
            path = global_path
        else:
            config = DEFAULT_CONFIG
            path = default_path

        for key, value in key_value_pairs.items():
            original_key = config["OpenAI"][key]
            if original_key == ["sk-key1", "sk-key2"]:
                config["OpenAI"][key] = [value]
            else:
                config["OpenAI"][key] = config["OpenAI"][key] + [value]

        create_config_file(config, path)

    else:
        create_config_file()
        logger.success("chatre.toml created")
