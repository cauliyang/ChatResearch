import os
from pathlib import Path

import toml
from loguru import logger


def report_token_usage(response):
    logger.info(f"prompt_token_used: {response.usage.prompt_tokens}")
    logger.info(f"completion_token_used: {response.usage.completion_tokens}")
    logger.info(f"total_token_used: {response.usage.total_tokens}")
    logger.info(f"response_time: { response.response_ms / 1000.0}s")


def load_config():
    default_path = Path.cwd() / "apikey.toml"
    global_path = Path.home() / ".config" / "apikey.toml"

    if default_path.exists():
        config = toml.load(default_path)
    elif global_path.exists():
        config = toml.load(global_path)
    else:
        raise FileNotFoundError("No apikey.toml found")

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
