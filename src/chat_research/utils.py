from loguru import logger


def report_token_usage(response):
    logger.info(f"prompt_token_used: {response.usage.prompt_tokens}")
    logger.info(f"completion_token_used: {response.usage.completion_tokens}")
    logger.info(f"total_token_used: {response.usage.total_tokens}")
    logger.info(f"response_time: { response.response_ms / 1000.0}s")
