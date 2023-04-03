import base64
import datetime
import re
from pathlib import Path

import openai
import requests
import tenacity
import tiktoken
from loguru import logger
from pydantic import BaseModel

from .paper_with_image import Paper
from .provider import biorxiv
from .utils import load_config, report_token_usage


class Params(BaseModel):
    date: str
    days: int
    server: str
    category: list[biorxiv.Category]
    key_word: str
    filter_keys: list[str]
    max_results: int
    sort: str
    save_image: bool
    file_format: str
    language: str


class Reader:
    def __init__(
        self,
        category: list[biorxiv.Category],
        key_word: list[str],
        filter_keys: list[str],
        root_path=".",
        sort=biorxiv.SortCriterion.SubmittedDate,
        user_name="defualt",
        args=None,
    ):
        self.user_name = user_name  # 读者姓名
        self.key_word = key_word  # 读者感兴趣的关键词
        self.sort = sort  # 读者选择的排序方式

        if args is None:
            raise ValueError("args is None")

        if args.language == "en":
            self.language = "English"
        elif args.language == "zh":
            self.language = "Chinese"
        else:
            self.language = "English"

        self.category = category  # 读者选择的类别
        self.filter_keys = filter_keys  # 用于在摘要中筛选的关键词
        self.root_path = Path(root_path)

        self.config, self.chat_api_list = load_config()
        self.cur_api = 0

        self.file_format = args.file_format
        self.gitee_key = self.config["Gitee"]["api"] if args.save_image else ""

        self.max_token_num = 4096
        self.encoding = tiktoken.get_encoding("gpt2")
        self.args = args

    def get_biorxiv(self, max_results=30):
        if self.args.days is not None:
            return biorxiv.Search(
                days=self.args.days,
                server=self.args.server,
                max_results=max_results,
            )
        else:
            return biorxiv.Search(
                start_date=self.args.start_date,
                end_date=self.args.end_date,
                server=self.args.server,
                max_results=max_results,
            )

    def filter_arxiv(self, max_results=30) -> list[biorxiv.Result]:
        search = self.get_biorxiv(max_results=max_results)
        results = list(search.results())

        logger.info("all search:")
        for index, result in enumerate(results):
            logger.info(f"{index=}, {result.title=}, {result.date}")

        # if self.filter_keys is empty then do not filter out
        if not self.filter_keys:
            return results

        filter_results = []

        logger.info(f"filter_keys {self.filter_keys}")
        # 确保每个关键词都能在摘要中找到，才算是目标论文
        for index, result in enumerate(results):
            abs_text = result.abstract.replace("-\n", "-").replace("\n", " ").lower()
            meet_num = 0

            for f_key in self.filter_keys:
                if f_key.lower() in abs_text:
                    meet_num += 1

            if meet_num == len(self.filter_keys):
                filter_results.append(result)

        logger.info(f"filter_results: {len(filter_results)}")
        logger.info("filter_papers:")
        for index, result in enumerate(filter_results):
            logger.info(f"{index=}, {result.title=}, {result.date}")

        return filter_results

    def validateTitle(self, title):
        # 将论文的乱七八糟的路径格式修正
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "_", title)  # 替换为下划线
        return new_title

    def download_pdf(self, filter_results):
        # 先创建文件夹
        date_str = str(datetime.datetime.now())[:13].replace(" ", "-")

        category_str = "-".join([c.value for c in self.category])

        path = self.root_path / "pdf_files" / f"{category_str}-{date_str}"
        path.mkdir(parents=True, exist_ok=True)

        logger.info(f"All_paper: {len(filter_results)}")
        # 开始下载：
        paper_list = []
        for _, result in enumerate(filter_results):
            try:
                title_str = self.validateTitle(result.title)
                pdf_name = title_str + ".pdf"
                self.try_download_pdf(result, path.as_posix(), pdf_name)
                paper_path = path / pdf_name

                logger.info(f"{paper_path=}")
                paper = Paper(
                    path=paper_path,
                    url=result.entry_id,
                    title=result.title,
                    abs=result.abstract.replace("-\n", "-").replace("\n", " "),
                    authers=[str(aut) for aut in result.authors.split(",")],
                )
                paper_list.append(paper)

            except Exception as e:
                logger.warning(f"download_error: {e}")
                pass

        return paper_list

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
    )
    def try_download_pdf(self, result, path, pdf_name):
        result.download_pdf(path, filename=pdf_name)

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

    def summary_with_chat(self, paper_list):
        htmls = []
        for paper_index, paper in enumerate(paper_list):
            # 第一步先用title，abs，和introduction进行总结。
            text = ""
            text += "Title:" + paper.title
            text += "Url:" + paper.url
            text += "Abstrat:" + paper.abs
            text += "Paper_info:" + paper.section_text_dict["paper_info"]
            # intro
            text += list(paper.section_text_dict.values())[0]
            chat_summary_text = ""

            try:
                chat_summary_text = self.chat_summary(text=text)
            except Exception as e:
                logger.warning(f"summary_error: {e}")
                if "maximum context" in str(e):
                    current_tokens_index = (
                        str(e).find("your messages resulted in")
                        + len("your messages resulted in")
                        + 1
                    )
                    offset = int(
                        str(e)[current_tokens_index : current_tokens_index + 4]
                    )
                    summary_prompt_token = offset + 1000 + 150
                    chat_summary_text = self.chat_summary(
                        text=text, summary_prompt_token=summary_prompt_token
                    )
                else:
                    raise e

            htmls.append("## Paper:" + str(paper_index + 1))
            htmls.append("\n\n\n")
            htmls.append(chat_summary_text)

            # 第二步总结方法：
            # TODO，由于有些文章的方法章节名是算法名，所以简单的通过关键词来筛选，很难获取，后面需要用其他的方案去优化。
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
                    chat_method_text = self.chat_method(text=text)
                except Exception as e:
                    logger.info(f"method_error: {e}")
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
                        chat_method_text = self.chat_method(
                            text=text, method_prompt_token=method_prompt_token
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
                chat_conclusion_text = self.chat_conclusion(text=text)
            except Exception as e:
                logger.info(f"conclusion_error: {e}")
                if "maximum context" in str(e):
                    current_tokens_index = (
                        str(e).find("your messages resulted in")
                        + len("your messages resulted in")
                        + 1
                    )
                    offset = int(
                        str(e)[current_tokens_index : current_tokens_index + 4]
                    )
                    conclusion_prompt_token = offset + 800 + 150
                    chat_conclusion_text = self.chat_conclusion(
                        text=text, conclusion_prompt_token=conclusion_prompt_token
                    )
            htmls.append(chat_conclusion_text)
            htmls.append("\n" * 4)

            # # 整合成一个文件，打包保存下来。
            date_str = str(datetime.datetime.now())[:13].replace(" ", "-")

            export_path = self.root_path / "export"

            if not export_path.exists():
                export_path.mkdir(parents=True, exist_ok=True)

            mode = "w" if paper_index == 0 else "a"

            file_name = (
                Path(export_path)
                / f"{date_str}-{self.validateTitle(paper.title[:80])}.{self.file_format}"
            )

            self.export_to_markdown(
                "\n".join([item.strip() for item in htmls]),
                file_name=file_name,
                mode=mode,
            )

            htmls = []

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
    )
    def chat_conclusion(self, text, conclusion_prompt_token=800):
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

        key_words = ",".join(self.key_word)
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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            # prompt需要用英语替换，少占用token。
            messages=messages,
        )
        result = ""
        for choice in response.choices:
            result += choice.message.content

        logger.info(f"conclusion_result:\n{result}")
        report_token_usage(response)

        return result

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
    )
    def chat_method(self, text, method_prompt_token=800):
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

        key_words = ",".join(self.key_word)
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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        result = ""
        for choice in response.choices:
            result += choice.message.content
        logger.info(f"method_result:\n{result}")
        report_token_usage(response)

        return result

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
    )
    def chat_summary(self, text, summary_prompt_token=1100):
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

        key_words = ",".join(self.key_word)
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
                "content": """
                 1. Mark the title of the paper (with Chinese translation)
                 2. list all the authors' names (use English)
                 3. mark the first author's affiliation (output {} translation only)
                 4. mark the keywords of this article (use English)
                 5. link to the paper, Github code link (if available, fill in Github:None if not)
                 6. summarize according to the following four points.Be sure to use {} answers (proper nouns need to be marked in English)
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

                 Be sure to use {} answers (proper nouns need to be marked in English), statements as concise and academic as possible, do not have too much repetitive information, numerical values using the original numbers, be sure to strictly follow the format, the corresponding content output to xxx, in accordance with \n line feed.
                 """.format(
                    self.language, self.language, self.language
                ),
            },
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        result = ""
        for choice in response.choices:
            result += choice.message.content

        logger.info(f"summary_result:\n{result}")

        report_token_usage(response)

        return result

    def export_to_markdown(self, text, file_name, mode="w"):
        # 使用markdown模块的convert方法，将文本转换为html格式
        # html = markdown.markdown(text)
        # 打开一个文件，以写入模式
        with open(file_name, mode, encoding="utf-8") as f:
            # 将html格式的内容写入文件
            f.write(text)

            # 定义一个方法，打印出读者信息

    def show_info(self):
        key_words = ",".join(self.key_word)
        categories = ",".join([c.name for c in self.category])

        logger.info(f"Key word: {key_words}")
        logger.info(f"Categories: {categories}")
        logger.info(f"Sort: {self.sort}")


def main(args):
    # 创建一个Reader对象，并调用show_info方法
    if args.sort == "Relevance":
        sort = biorxiv.SortCriterion.Relevance
    elif args.sort == "LastUpdatedDate":
        sort = biorxiv.SortCriterion.LastUpdatedDate
    else:
        sort = biorxiv.SortCriterion.Relevance

    categories = [biorxiv.Category.from_str(c) for c in args.category]

    reader = Reader(
        category=categories,
        key_word=args.key_word,
        filter_keys=args.filter_keys,
        sort=sort,
        args=args,
    )

    reader.show_info()
    filter_results = reader.filter_arxiv(max_results=args.max_results)
    paper_list = reader.download_pdf(filter_results)
    reader.summary_with_chat(paper_list)


CATEGORY_LIST = [
    "animal behavior and cogtition",
    "biochemistry",
    "bioengineering",
    "bioinformatics",
    "biophysics",
    "cancer biology",
    "clinical trials",
    "developmental biology",
    "ecology",
    "epidemiology",
    "evolutionary biology",
    "genetics",
    "genomics",
    "immunology",
    "microbiology",
    "molecular biology",
    "neuroscience",
    "paleontology",
    "pathology",
    "pharmacology and toxicology",
    "physiology",
    "plant biology",
    "scientific communication and education",
    "synthetic biology",
    "systems biology",
    "zoology",
]


def add_subcommand(parser):
    name = "biorxiv"
    subparser = parser.add_parser(name, help="Fetch and Summary paper from bioarxiv")

    subparser.add_argument(
        "--category",
        type=str,
        default="bioinformatics",
        choices=CATEGORY_LIST,
        action="extend",
        nargs="+",
        metavar="",
        help="the category of user research fields (default: %(default)s)",
    )

    group = subparser.add_mutually_exclusive_group()
    group.add_argument(
        "--date",
        type=str,
        metavar="",
        help="the date of user research fields (example 2018-08-21:2018-08-28)",
    )

    group.add_argument(
        "--days",
        type=int,
        default=1,
        metavar="",
        help="the last days of arxiv papers of this query",
    )

    subparser.add_argument(
        "--server",
        type=str,
        default="biorxiv",
        choices=["biorxiv", "medrxiv"],
        metavar="",
        help="the category of user research fields (default: %(default)s)",
    )

    subparser.add_argument(
        "--filter-keys",
        type=str,
        action="extend",
        nargs="+",
        metavar="",
        help="the filter key words, every word in the abstract must have, otherwise it will not be selected as the target paper",
    )

    subparser.add_argument(
        "--max-results",
        type=int,
        default=20,
        metavar="",
        help="the maximum number of results (default: %(default)s)",
    )

    subparser.add_argument(
        "--sort",
        type=str,
        default="Relevance",
        metavar="",
        help="another is LastUpdatedDate (default: %(default)s)",
    )

    subparser.add_argument(
        "--save-image",
        default=False,
        metavar="",
        help="save image? It takes a minute or two to save a picture! But pretty (default: %(default)s)",
    )

    subparser.add_argument(
        "--file-format",
        type=str,
        default="md",
        metavar="",
        help="the format of the exported file, if you save the picture, it is best to be md, if not, the txt will not be messy (default: %(default)s)",
    )

    subparser.add_argument(
        "--language",
        type=str,
        default="en",
        metavar="",
        help="The other output lauguage is English, is en (default: %(default)s)",
    )

    return name
