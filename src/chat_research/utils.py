import os
from pathlib import Path

import toml
from loguru import logger

CONFIG_FILE_NAME = "chatre.toml"
DEFAULT_PATH = Path.cwd() / CONFIG_FILE_NAME
GLOBAL_PATH = Path.home() / ".config" / "chatre" / CONFIG_FILE_NAME


def report_token_usage(response):
    logger.info(f"prompt_token_used: {response.usage.prompt_tokens}")
    logger.info(f"completion_token_used: {response.usage.completion_tokens}")
    logger.info(f"total_token_used: {response.usage.total_tokens}")
    logger.info(f"response_time: { response.response_ms / 1000.0}s")


def load_config():
    if DEFAULT_PATH.exists():
        config = toml.load(DEFAULT_PATH)
    elif GLOBAL_PATH.exists():
        config = toml.load(GLOBAL_PATH)
    else:
        raise FileNotFoundError("No chatre.toml found")

    chat_api_list = config["OpenAI"]["OPENAI_API_KEYS"]

    env_api = os.environ.get("OPENAI_API_KEY", None)
    if env_api is not None:
        chat_api_list.append(env_api)

    new_chat_api_list = []
    for i in chat_api_list:
        if len(i.strip()) < 51:
            logger.warning(f"API key {i} is too short, it will be skipped.")
        else:
            new_chat_api_list.append(i.strip())

    if len(new_chat_api_list) == 0:
        logger.error("No API key found")
        raise SystemExit

    return config, new_chat_api_list
