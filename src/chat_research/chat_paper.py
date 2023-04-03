import datetime
import os
from pathlib import Path

import arxiv
import tenacity
from loguru import logger
from pydantic import BaseModel, validator

from .paper_with_image import Paper
from .reader import BaseReader


class PaperParams(BaseModel):
    pdf_path: str
    query: str
    key_word: str
    filter_keys: str
    max_results: int
    sort: str
    save_image: bool
    file_format: str
    language: str

    @validator("pdf_path")
    def pdf_path_must_exist(cls, v):
        if not Path(v).exists():
            raise ValueError("pdf_path must exist")
        return v


# 定义Reader类
class Reader(BaseReader):
    # 初始化方法，设置属性
    def __init__(
        self,
        key_word,
        query,
        filter_keys,
        root_path=".",
        sort=arxiv.SortCriterion.SubmittedDate,
        user_name="defualt",
        args=None,
    ):
        if args is None:
            raise ValueError("args is None")

        if args.language == "en":
            language = "English"
        elif args.language == "zh":
            language = "Chinese"
        else:
            language = "English"

        super().__init__(
            filter_keys,
            root_path,
            language,
            args.file_format,
            args.save_image,
        )

        self.user_name = user_name  # 读者姓名
        self.key_word = key_word  # 读者感兴趣的关键词
        self.query = query  # 读者输入的搜索查询
        self.sort = sort  # 读者选择的排序方式

    def get_arxiv(self, max_results=30):
        search = arxiv.Search(
            query=self.query,
            max_results=max_results,
            sort_by=self.sort,
            sort_order=arxiv.SortOrder.Descending,
        )
        return search

    def filter_arxiv(self, max_results=30):
        search = self.get_arxiv(max_results=max_results)
        logger.info("all search:")
        for index, result in enumerate(search.results()):
            logger.info(f"{index=}, {result.title=}, {result.updated}")

        filter_results = []
        filter_keys = self.filter_keys

        logger.info(f"filter_keys {self.filter_keys}")
        # 确保每个关键词都能在摘要中找到，才算是目标论文
        for index, result in enumerate(search.results()):
            abs_text = result.summary.replace("-\n", "-").replace("\n", " ")
            meet_num = 0
            for f_key in filter_keys.split(" "):
                if f_key.lower() in abs_text.lower():
                    meet_num += 1
            if meet_num == len(filter_keys.split(" ")):
                filter_results.append(result)
                # break
        logger.info(f"filter_results: {len(filter_results)}")
        logger.info("filter_papers:")
        for index, result in enumerate(filter_results):
            logger.info(f"{index=}, {result.title=}, {result.updated}")
        return filter_results

    def download_pdf(self, filter_results):
        # 先创建文件夹
        date_str = str(datetime.datetime.now())[:13].replace(" ", "-")

        query_str = (
            self.query.replace("au:", "")
            .replace("title: ", "")
            .replace("ti: ", "")
            .replace(":", " ")[:25]
        )

        path = self.root_path / "pdf_files" / f"{query_str}-{date_str}"
        path.mkdir(parents=True, exist_ok=True)

        logger.info(f"All_paper: {len(filter_results)}")
        # 开始下载：
        paper_list = []

        for _, result in enumerate(filter_results):
            try:
                title_str = self.validateTitle(result.title)
                pdf_name = title_str + ".pdf"
                # result.download_pdf(path, filename=pdf_name)
                self.try_download_pdf(result, path.as_posix(), pdf_name)

                paper_path = path / pdf_name

                logger.info(f"{paper_path=}")

                paper = Paper(
                    path=paper_path,
                    url=result.entry_id,
                    title=result.title,
                    abs=result.summary.replace("-\n", "-").replace("\n", " "),
                    authers=[str(aut) for aut in result.authors],
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

    def show_info(self):
        logger.info(f"Key word: {self.key_word}")
        logger.info(f"Query: {self.query}")
        logger.info(f"Sort: {self.sort}")


def add_subcommand(parser):
    name = "paper"
    subparser = parser.add_parser(
        name, help="Fetch or Summary paper from local or arxiv"
    )
    subparser.add_argument(
        "--pdf-path",
        type=str,
        default="",
        metavar="",
        help="if none, the bot will download from arxiv with query",
    )

    subparser.add_argument(
        "--query",
        type=str,
        default="all: ChatGPT robot",
        metavar="",
        help="the query string, ti: xx, au: xx, all: xx (default: %(default)s)",
    )

    subparser.add_argument(
        "--key-word",
        type=str,
        default="reinforcement learning",
        metavar="",
        help="the key word of user research fields (default: %(default)s)",
    )

    subparser.add_argument(
        "--filter-keys",
        type=str,
        default="ChatGPT robot",
        metavar="",
        help="the filter key words, every word in the abstract must have, otherwise it will not be selected as the target paper (default: %(default)s)",
    )

    subparser.add_argument(
        "--max-results",
        type=int,
        default=1,
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
        choices=["md", "txt", "pdf"],
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


def main(args):
    # 创建一个Reader对象，并调用show_info方法
    if args.sort == "Relevance":
        sort = arxiv.SortCriterion.Relevance
    elif args.sort == "LastUpdatedDate":
        sort = arxiv.SortCriterion.LastUpdatedDate
    else:
        sort = arxiv.SortCriterion.Relevance

    if args.pdf_path:
        reader1 = Reader(
            key_word=args.key_word,
            query=args.query,
            filter_keys=args.filter_keys,
            sort=sort,
            args=args,
        )
        reader1.show_info()
        # 开始判断是路径还是文件：
        paper_list = []
        if args.pdf_path.endswith(".pdf"):
            paper_list.append(Paper(path=args.pdf_path))
            logger.info(f"read pdf file {args.pdf_path}")
        else:
            logger.info(f"read pdf files from path {args.pdf_path}")
            for root, dirs, files in os.walk(args.pdf_path):
                logger.trace(f"root: {root}, dirs: {dirs}, files: {files}")
                for filename in files:
                    # 如果找到PDF文件，则将其复制到目标文件夹中
                    if filename.endswith(".pdf"):
                        paper_list.append(Paper(path=os.path.join(root, filename)))

        logger.info("paper_num: {}".format(len(paper_list)))
        for paper_index, paper_name in enumerate(paper_list):
            name = paper_name.path.split("\\")[-1]
            logger.info(f"{paper_index=}, {name=}")

        reader1.summary_with_chat(paper_list=paper_list, key_words=reader1.key_word)
    else:
        reader1 = Reader(
            key_word=args.key_word,
            query=args.query,
            filter_keys=args.filter_keys,
            sort=sort,
            args=args,
        )
        reader1.show_info()
        filter_results = reader1.filter_arxiv(max_results=args.max_results)
        paper_list = reader1.download_pdf(filter_results)
        reader1.summary_with_chat(paper_list=paper_list, key_words=reader1.key_word)


def cli(args):
    parameters = PaperParams(**vars(args))
    main(parameters)
