import configparser
import datetime
import os

import openai
import tenacity
import tiktoken

from loguru import logger
from pydantic import BaseModel
from pydantic import validator
from pathlib import Path


# ChatResponse
class ResponseParams(BaseModel):
    comment_path: str
    file_format: str
    language: str

    @validator("comment_path")
    def comment_path_must_exist(cls, v):
        if not Path(v).exists():
            raise ValueError("comment_path must exist")
        return v


# 定义Response类
class Response:
    # 初始化方法，设置属性
    def __init__(self, args=None):
        if args is None:
            raise ValueError("args is None")

        if args.language == "en":
            self.language = "English"
        elif args.language == "zh":
            self.language = "Chinese"
        else:
            self.language = "Chinese"

            # 创建一个ConfigParser对象
        self.config = configparser.ConfigParser()
        # 读取配置文件
        self.config.read("apikey.ini")
        OPENAI_KEY = os.environ.get("OPENAI_KEY", "")
        # 获取某个键对应的值
        self.chat_api_list = (
            self.config.get("OpenAI", "OPENAI_API_KEYS")[1:-1]
            .replace("'", "")
            .split(",")
        )
        self.chat_api_list.append(OPENAI_KEY)

        # prevent short strings from being incorrectly used as API keys.
        self.chat_api_list = [
            api.strip() for api in self.chat_api_list if len(api) > 20
        ]

        self.cur_api = 0
        self.file_format = args.file_format
        self.max_token_num = 4096
        self.encoding = tiktoken.get_encoding("gpt2")

    def response_by_chatgpt(self, comment_path):
        htmls = []
        # 读取回复的内容
        with open(comment_path, "r", encoding="utf-8") as f:
            comments = f.read()

        chat_response_text = self.chat_response(text=comments)
        htmls.append(chat_response_text)

        # 将审稿意见保存起来
        date_str = str(datetime.datetime.now())[:13].replace(" ", "-")
        export_path = os.path.join("./", "response_file")
        if not os.path.exists(export_path):
            os.makedirs(export_path)
        file_name = os.path.join(
            export_path, date_str + "-Response." + self.file_format
        )
        self.export_to_markdown("\n".join(htmls), file_name=file_name)
        htmls = []

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
    )
    def chat_response(self, text):
        openai.api_key = self.chat_api_list[self.cur_api]
        self.cur_api += 1
        self.cur_api = (
            0 if self.cur_api >= len(self.chat_api_list) - 1 else self.cur_api
        )
        response_prompt_token = 1000
        text_token = len(self.encoding.encode(text))
        input_text_index = int(
            len(text) * (self.max_token_num - response_prompt_token) / text_token
        )
        input_text = "This is the review comments:" + text[:input_text_index]
        messages = [
            {
                "role": "system",
                "content": """You are the author, you submitted a paper, and the reviewers gave the review comments.
                Please reply with what we have done, not what we will do.
                You need to extract questions from the review comments one by one, and then respond point-to-point to the reviewers’ concerns.
                Please answer in {}. Follow the format of the output later:
                - Response to reviewers
                #1 reviewer
                Concern #1: xxxx
                Author response: xxxxx

                Concern #2: xxxx
                Author response: xxxxx
                ...

                #2 reviewer
                Concern #1: xxxx
                Author response: xxxxx

                Concern #2: xxxx
                Author response: xxxxx
                ...

                #3 reviewer
                Concern #1: xxxx
                Author response: xxxxx

                Concern #2: xxxx
                Author response: xxxxx
                ...

                """.format(
                    self.language
                ),
            },
            {"role": "user", "content": input_text},
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        result = ""
        for choice in response.choices:
            result += choice.message.content
        logger.info("********" * 10)
        logger.info(result)
        logger.info("********" * 10)
        logger.info("prompt_token_used:", response.usage.prompt_tokens)
        logger.info("completion_token_used:", response.usage.completion_tokens)
        logger.info("total_token_used:", response.usage.total_tokens)
        logger.info("response_time:", response.response_ms / 1000.0, "s")
        return result

    def export_to_markdown(self, text, file_name, mode="w"):
        # 使用markdown模块的convert方法，将文本转换为html格式
        # html = markdown.markdown(text)
        # 打开一个文件，以写入模式
        with open(file_name, mode, encoding="utf-8") as f:
            # 将html格式的内容写入文件
            f.write(text)


def chat_response_main(args):
    Response1 = Response(args=args)
    Response1.response_by_chatgpt(comment_path=args.comment_path)


def add_subcommand(parser):
    name = "response"
    subparser = parser.add_parser(name)
    subparser.add_argument(
        "--comment-path",
        type=str,
        metavar="",
        help="path of comment",
        required=True,
    )
    subparser.add_argument(
        "--file-format",
        type=str,
        default="txt",
        metavar="",
        help="output file format (default: %(default)s)",
    )
    subparser.add_argument(
        "--language",
        type=str,
        default="en",
        metavar="",
        help="output language, en or zh (default: %(default)s)",
    )

    return name


def cli(args):
    parameter = ResponseParams(**vars(args))
    chat_response_main(parameter)
