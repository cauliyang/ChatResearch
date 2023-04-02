import configparser
import os
from pathlib import Path

from loguru import logger


def report_token_usage(response):
    logger.info(f"prompt_token_used: {response.usage.prompt_tokens}")
    logger.info(f"completion_token_used: {response.usage.completion_tokens}")
    logger.info(f"total_token_used: {response.usage.total_tokens}")
    logger.info(f"response_time: { response.response_ms / 1000.0}s")


def load_config():
    config = configparser.ConfigParser()

    default_path = Path.cwd() / "apikey.ini"
    global_path = Path.home() / ".config" / "apikey.ini"

    if default_path.exists():
        config.read(default_path)
    elif global_path.exists():
        config.read(global_path)

    env_api = os.environ.get("OPENAI_KEY", None)

    chat_api_list = (
        config.get("OpenAI", "OPENAI_API_KEYS")[1:-1].replace("'", "").split(",")
    )

    if env_api is not None:
        chat_api_list.append(env_api)

    if len(chat_api_list) == 0:
        logger.error("No API key found")
        raise SystemExit

    for i in chat_api_list:
        if len(i) < 52:
            logger.error(f"API key {i} is too short")
            raise SystemExit

    return config, chat_api_list
