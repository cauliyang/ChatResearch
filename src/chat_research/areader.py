import asyncio
import base64
import datetime
import re
from pathlib import Path

import openai
import requests
import tenacity
import tiktoken
from loguru import logger

from .aexport import aexport
from .paper_with_image import Paper
from .utils import load_config


class AsyncBaseReader:
    def __init__(self, root_path, language, file_format, save_image):
        if isinstance(root_path, str):
            root_path = Path(root_path)

        self.root_path = root_path
        self.language = language
        self.file_format = file_format

        self.config, self.chat_api_list = load_config()
        self.cur_api = 0

        self.gitee_key = self.config["Gitee"]["api"] if save_image else ""

        self.max_token_num = 4096
        self.encoding = tiktoken.get_encoding("gpt2")
        self.token_usage = 0

    async def _summary_with_chat(self, paper_list: list[Paper], key_words):
        await asyncio.gather(
            *[
                self.summary_with_chat_for_one_paper(paper, index, key_words)
                for index, paper in enumerate(paper_list)
            ]
        )

    def summary_with_chat(self, paper_list: list[Paper], key_words):
        asyncio.run(self._summary_with_chat(paper_list, key_words))

    def update_title(self, text):
        for line in text.split("\n"):
            if "Title:" in line:
                return line.split("Title:")[1].strip()

    async def summary_with_chat_for_one_paper(
        self, paper: Paper, paper_index: int, key_words
    ):
        htmls = []
        text = ""
        text += "Title:" + paper.title
        text += "Url:" + paper.url
        text += "Abstrat:" + paper.abs
        text += "Paper_info:" + paper.section_text_dict["paper_info"]
        # intro
        text += list(paper.section_text_dict.values())[0]
        chat_summary_text = ""

        try:
            chat_summary_text = await self.chat_summary(text=text, key_words=key_words)
        except Exception as e:
            logger.warning(f"summary_error: {e}")
            if "maximum context" in str(e):
                current_tokens_index = (
                    str(e).find("your messages resulted in")
                    + len("your messages resulted in")
                    + 1
                )
                offset = int(str(e)[current_tokens_index : current_tokens_index + 4])
                summary_prompt_token = offset + 1000 + 150
                chat_summary_text = await self.chat_summary(
                    text=text,
                    key_words=key_words,
                    summary_prompt_token=summary_prompt_token,
                )
            else:
                raise e

        if (
            paper.title == ""
            and (title := self.update_title(chat_summary_text)) is not None
        ):
            paper.title = title

        htmls.append("## Paper:" + str(paper_index + 1))
        htmls.append("\n\n\n")
        htmls.append(chat_summary_text)

        # 第二步总结方法：
        # WARNING，由于有些文章的方法章节名是算法名，
        # 所以简单的通过关键词来筛选，很难获取，后面需要用其他的方案去优化。
        method_key = ""
        for parse_key in paper.section_text_dict.keys():
            if "method" in parse_key.lower() or "approach" in parse_key.lower():
                method_key = parse_key
                break

        if method_key != "":
            text = ""
            method_text = ""
            summary_text = ""
            summary_text += "<summary>" + chat_summary_text
            # methods
            method_text += paper.section_text_dict[method_key]
            text = summary_text + "\n\n<Methods>:\n\n" + method_text
            chat_method_text = ""
            try:
                chat_method_text = await self.chat_method(
                    text=text, key_words=key_words
                )
            except Exception as e:
                logger.error(f"method_error: {e}")
                if "maximum context" in str(e):
                    current_tokens_index = (
                        str(e).find("your messages resulted in")
                        + len("your messages resulted in")
                        + 1
                    )
                    offset = int(
                        str(e)[current_tokens_index : current_tokens_index + 4]
                    )
                    method_prompt_token = offset + 800 + 150
                    chat_method_text = await self.chat_method(
                        text=text,
                        key_words=key_words,
                        method_prompt_token=method_prompt_token,
                    )
            htmls.append(chat_method_text)
        else:
            chat_method_text = ""

        htmls.append("\n" * 4)

        # 第三步总结全文，并打分：
        conclusion_key = ""
        for parse_key in paper.section_text_dict.keys():
            if "conclu" in parse_key.lower():
                conclusion_key = parse_key
                break

        text = ""
        conclusion_text = ""
        summary_text = ""
        summary_text += (
            "<summary>"
            + chat_summary_text
            + "\n <Method summary>:\n"
            + chat_method_text
        )

        if conclusion_key != "":
            # conclusion
            conclusion_text += paper.section_text_dict[conclusion_key]
            text = summary_text + "\n\n<Conclusion>:\n\n" + conclusion_text
        else:
            text = summary_text

        chat_conclusion_text = ""
        try:
            chat_conclusion_text = await self.chat_conclusion(
                text=text, key_words=key_words
            )
        except Exception as e:
            logger.info(f"conclusion_error: {e}")
            if "maximum context" in str(e):
                current_tokens_index = (
                    str(e).find("your messages resulted in")
                    + len("your messages resulted in")
                    + 1
                )
                offset = int(str(e)[current_tokens_index : current_tokens_index + 4])
                conclusion_prompt_token = offset + 800 + 150
                chat_conclusion_text = await self.chat_conclusion(
                    text=text,
                    key_words=key_words,
                    conclusion_prompt_token=conclusion_prompt_token,
                )
        htmls.append(chat_conclusion_text)
        htmls.append("\n" * 4)

        # # 整合成一个文件，打包保存下来。
        date_str = str(datetime.datetime.now())[:13].replace(" ", "-")
        export_path = self.root_path / "export"

        if not export_path.exists():
            export_path.mkdir(parents=True, exist_ok=True)

        file_name = (
            Path(export_path) / f"{date_str}-{self.validateTitle(paper.title[:80])}"
        )

        await aexport(
            content="\n".join([item.strip() for item in htmls]),
            file_name=file_name.with_suffix(f".{self.file_format}"),
        )

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
    )
    async def chat_conclusion(self, text, key_words, conclusion_prompt_token=800):
        openai.api_key = self.chat_api_list[self.cur_api]
        self.cur_api += 1
        self.cur_api = (
            0 if self.cur_api >= len(self.chat_api_list) - 1 else self.cur_api
        )
        text_token = len(self.encoding.encode(text))
        clip_text_index = int(
            len(text) * (self.max_token_num - conclusion_prompt_token) / text_token
        )
        clip_text = text[:clip_text_index]

        messages = [
            {
                "role": "system",
                "content": f"You are a reviewer in the field of [{key_words}] and you need to critically review this article",
            },
            # chatgpt 角色
            {
                "role": "assistant",
                "content": "This is the <summary> and <conclusion> part of an English literature, where <summary> you have already summarized, but <conclusion> part, I need your help to summarize the following questions:"
                + clip_text,
            },
            # 背景知识，可以参考OpenReview的审稿流程
            {
                "role": "user",
                "content": """
                 8. Make the following summary.Be sure to use {} answers (proper nouns need to be marked in English).
                    - (1):What is the significance of this piece of work?
                    - (2):Summarize the strengths and weaknesses of this article in three dimensions: innovation point, performance, and workload.
                    .......
                 Follow the format of the output later:
                 8. Conclusion: \n\n
                    - (1):xxx;\n
                    - (2):Innovation point: xxx; Performance: xxx; Workload: xxx;\n

                 Be sure to use {} answers (proper nouns need to be marked in English), statements as concise and academic as possible, do not repeat the content of the previous <summary>, the value of the use of the original numbers, be sure to strictly follow the format, the corresponding content output to xxx, in accordance with \n line feed, ....... means fill in according to the actual requirements, if not, you can not write.
                 """.format(
                    self.language, self.language
                ),
            },
        ]
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            # prompt需要用英语替换，少占用token。
            messages=messages,
        )
        result = ""
        for choice in response.choices:
            result += choice.message.content

        result = self.format_text(result)
        logger.trace(f"conclusion_result:\n{result}")
        self.report_token_usage(response)

        return result

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
    )
    async def chat_method(self, text, key_words, method_prompt_token=800):
        openai.api_key = self.chat_api_list[self.cur_api]
        self.cur_api += 1
        self.cur_api = (
            0 if self.cur_api >= len(self.chat_api_list) - 1 else self.cur_api
        )
        text_token = len(self.encoding.encode(text))
        clip_text_index = int(
            len(text) * (self.max_token_num - method_prompt_token) / text_token
        )
        clip_text = text[:clip_text_index]

        messages = [
            {
                "role": "system",
                "content": f"You are a researcher in the field of [{key_words}] who is good at summarizing papers using concise statements",
            },
            # chatgpt 角色
            {
                "role": "assistant",
                "content": "This is the <summary> and <Method> part of an English document, where <summary> you have summarized, but the <Methods> part, I need your help to read and summarize the following questions."
                + clip_text,
            },
            # 背景知识
            {
                "role": "user",
                "content": """
                 7. Describe in detail the methodological idea of this article. Be sure to use {} answers (proper nouns need to be marked in English). For example, its steps are.
                    - (1):...
                    - (2):...
                    - (3):...
                    - .......
                 Follow the format of the output that follows:
                 7. Methods: \n\n
                    - (1):xxx;\n
                    - (2):xxx;\n
                    - (3):xxx;\n
                    ....... \n\n

                 Be sure to use {} answers (proper nouns need to be marked in English), statements as concise and academic as possible, do not repeat the content of the previous <summary>, the value of the use of the original numbers, be sure to strictly follow the format, the corresponding content output to xxx, in accordance with \n line feed, ....... means fill in according to the actual requirements, if not, you can not write.
                 """.format(
                    self.language, self.language
                ),
            },
        ]
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages,
        )

        result = ""
        for choice in response.choices:
            result += choice.message.content

        result = self.format_text(result)
        logger.trace(f"method_result:\n{result}")
        self.report_token_usage(response)

        return result

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
    )
    async def chat_summary(self, text, key_words, summary_prompt_token=1100):
        openai.api_key = self.chat_api_list[self.cur_api]
        self.cur_api += 1
        self.cur_api = (
            0 if self.cur_api >= len(self.chat_api_list) - 1 else self.cur_api
        )
        text_token = len(self.encoding.encode(text))
        clip_text_index = int(
            len(text) * (self.max_token_num - summary_prompt_token) / text_token
        )
        clip_text = text[:clip_text_index]

        messages = [
            {
                "role": "system",
                "content": f"You are a researcher in the field of [{key_words}]  who is good at summarizing papers using concise statements",
            },
            {
                "role": "assistant",
                "content": "This is the title, author, link, abstract and introduction of an English document. I need your help to read and summarize the following questions: "
                + clip_text,
            },
            {
                "role": "user",
                "content": f"""
                 1. Mark the title of the paper
                 2. list all the authors' names (use English)
                 3. mark the first author's affiliation (use English)
                 4. mark the keywords of this article (use English)
                 5. link to the paper, Github code link (if available, fill in Github:None if not)
                 6. summarize according to the following four points.Be sure to use {self.language} answers (proper nouns need to be marked in English)
                    - (1):What is the research background of this article?
                    - (2):What are the past methods? What are the problems with them? Is the approach well motivated?
                    - (3):What is the research methodology proposed in this paper?
                    - (4):On what task and what performance is achieved by the methods in this paper? Can the performance support their goals?
                 Follow the format of the output that follows:
                 1. Title: xxx\n\n
                 2. Authors: xxx\n\n
                 3. Affiliation: xxx\n\n
                 4. Keywords: xxx\n\n
                 5. Urls: xxx or xxx , xxx \n\n
                 6. Summary: \n\n
                    - (1):xxx;\n
                    - (2):xxx;\n
                    - (3):xxx;\n
                    - (4):xxx.\n\n

                 Be sure to use {self.language} answers (proper nouns need to be marked in English), statements as concise and academic as possible, do not have too much repetitive information, numerical values using the original numbers, be sure to strictly follow the format,
                 the corresponding content output to xxx, in accordance with \n line feed.
                 """,
            },
        ]

        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        result = ""

        for choice in response.choices:
            result += choice.message.content

        result = self.format_text(result)
        logger.trace(f"summary_result:\n{result}")

        self.report_token_usage(response)

        return result

    @staticmethod
    def format_text(text):
        result = ""
        for line in text.split("\n"):
            result += line.strip() + "\n"
        return result

    def validateTitle(self, title):
        # 将论文的乱七八糟的路径格式修正
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "_", title)  # 替换为下划线
        return new_title

    def show_token_usage(self):
        money = self.token_usage / 1000 * 0.002
        logger.info(f"TOKENS: {self.token_usage} / PRICES: ${money:.6f}")

    def report_token_usage(self, response):
        logger.trace(f"prompt_token_used: {response.usage.prompt_tokens}")
        logger.trace(f"completion_token_used: {response.usage.completion_tokens}")
        logger.trace(f"total_token_used: {response.usage.total_tokens}")
        logger.trace(f"response_time: { response.response_ms / 1000.0}s")
        self.token_usage += response.usage.total_tokens

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
    )
    def upload_gitee(self, image_path, image_name="", ext="png"):
        """
        上传到码云
        :return:
        """
        with open(image_path, "rb") as f:
            base64_data = base64.b64encode(f.read())
            base64_content = base64_data.decode()

        date_str = (
            str(datetime.datetime.now())[:19].replace(":", "-").replace(" ", "-")
            + "."
            + ext
        )
        path = image_name + "-" + date_str

        payload = {
            "access_token": self.gitee_key,
            "owner": self.config["Gitee"]["owner"],
            "repo": self.config["Gitee"]["repo"],
            "path": self.config["Gitee"]["path"],
            "content": base64_content,
            "message": "upload image",
        }
        # 这里需要修改成你的gitee的账户和仓库名，以及文件夹的名字：
        url = (
            "https://gitee.com/api/v5/repos/"
            + self.config["Gitee"]["owner"]
            + "/"
            + self.config["Gitee"]["repo"]
            + "/contents/"
            + self.config["Gitee"]["path"]
            + "/"
            + path
        )
        rep = requests.post(url, json=payload).json()
        logger.info(f"{rep=}")
        if "content" in rep.keys():
            image_url = rep["content"]["download_url"]
        else:
            image_url = (
                r"https://gitee.com/api/v5/repos/"
                + self.config["Gitee"]["owner"]
                + "/contents/"
                + self.config["Gitee"]["path"]
                + "/"
                + path
            )

        return image_url
