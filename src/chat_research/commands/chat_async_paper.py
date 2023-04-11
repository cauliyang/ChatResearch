import asyncio
import datetime
import os
from pathlib import Path
from typing import Optional

import aiohttp
from loguru import logger
from pydantic import BaseModel, validator

from ..areader import AsyncBaseReader
from ..paper_with_image import Paper
from ..provider import async_arxiv as arxiv


class PaperParams(BaseModel):
    pdf: str
    query: str
    key_word: str
    filter_keys: Optional[list[str]] = None
    max_results: int
    sort: str
    save_image: bool
    file_format: str
    language: str

    @validator("pdf")
    def pdf_path_must_exist(cls, v):
        if not Path(v).exists():
            raise ValueError("pdf_path must exist")
        return v


class Reader(AsyncBaseReader):
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
            root_path,
            language,
            args.file_format,
            args.save_image,
        )

        self.user_name = user_name  # name of the reader
        self.key_word = key_word  # keyword of interest to the reader
        self.filter_keys = filter_keys  # keywords used to filter abstracts
        self.query = query  # search query entered by the reader
        self.sort = sort  # sorting method selected by the reader

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
        results = list(search.results())

        logger.info("All search:")
        for index, result in enumerate(results):
            logger.info(
                f"{index=}, title={result.title} {result.updated.strftime('%Y-%m-%d')}"
            )

        # if self.filter_keys is empty then do not filter out
        if not self.filter_keys:
            return results

        filter_results = []

        logger.info(f"filter_keys {self.filter_keys}")
        # 确保每个关键词都能在摘要中找到，才算是目标论文
        for index, result in enumerate(search.results()):
            abs_text = result.summary.replace("-\n", "-").replace("\n", " ")
            meet_num = 0
            for f_key in self.filter_keys:
                if f_key.lower() in abs_text.lower():
                    meet_num += 1
            if meet_num == len(self.filter_keys):
                filter_results.append(result)

        logger.info(f"filter_results: {len(filter_results)}")
        logger.info("filter_papers:")
        for index, result in enumerate(filter_results):
            logger.info(
                f"{index=}, title={result.title} {result.updated.strftime('%Y-%m-%d')}"
            )

        return filter_results

    def download_pdf(self, filter_results):
        return asyncio.run(self._download_pdf(filter_results))

    @staticmethod
    def create_paper(results_mapping, paper_path):
        result = results_mapping[paper_path.name]
        paper = Paper(
            path=paper_path,
            url=result.entry_id,
            title=result.title,
            abs=result.summary.replace("-\n", "-").replace("\n", " "),
            authers=[str(aut) for aut in result.authors],
        )
        return paper

    async def _download_pdf(self, filter_results):
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

        paper_list = []
        tasks = []
        results_mapping = {}

        async with aiohttp.ClientSession() as session:
            for _, result in enumerate(filter_results):
                title_str = self.validateTitle(result.title)
                pdf_name = title_str + ".pdf"
                tasks.append(result.download_pdf(session, path.as_posix(), pdf_name))
                results_mapping[pdf_name] = result

            for done_task in asyncio.as_completed(tasks):
                try:
                    paper_path = await done_task
                    paper_list.append(self.create_paper(results_mapping, paper_path))

                except Exception as e:
                    logger.warning(f"download_error: {e}")

        return paper_list

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
        "-p",
        "--pdf",
        type=str,
        default="",
        metavar="",
        help="if none, the bot will download from arxiv with query",
    )

    subparser.add_argument(
        "-q",
        "--query",
        type=str,
        default="all: ChatGPT robot",
        metavar="",
        help="the query string, ti: xx, au: xx, all: xx (default: %(default)s)",
    )

    subparser.add_argument(
        "-k",
        "--key-word",
        type=str,
        default="reinforcement learning",
        metavar="",
        help="the key word of user research fields (default: %(default)s)",
    )

    subparser.add_argument(
        "-m",
        "--max-results",
        type=int,
        default=1,
        metavar="",
        help="the maximum number of results (default: %(default)s)",
    )

    subparser.add_argument(
        "-s",
        "--sort",
        type=str,
        default="Relevance",
        metavar="",
        help="another is LastUpdatedDate (default: %(default)s)",
    )

    subparser.add_argument(
        "-f",
        "--file-format",
        type=str,
        default="md",
        choices=["md", "txt", "pdf", "tex"],
        metavar="",
        help="the format of the exported file, if you save the picture, it is best to be md, if not, the txt will not be messy (default: %(default)s)",
    )

    subparser.add_argument(
        "-l",
        "--language",
        type=str,
        default="en",
        metavar="",
        help="The other output lauguage is English, is en (default: %(default)s)",
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
        "--save-image",
        default=False,
        metavar="",
        help="save image? It takes a minute or two to save a picture! But pretty (default: %(default)s)",
    )

    return name


def main(args):
    if args.sort == "Relevance":
        sort = arxiv.SortCriterion.Relevance
    elif args.sort == "LastUpdatedDate":
        sort = arxiv.SortCriterion.LastUpdatedDate
    else:
        sort = arxiv.SortCriterion.Relevance

    if args.pdf:
        reader = Reader(
            key_word=args.key_word,
            query=args.query,
            filter_keys=args.filter_keys,
            sort=sort,
            args=args,
        )
        reader.show_info()
        paper_list = []
        if args.pdf.endswith(".pdf"):
            paper_list.append(Paper(path=args.pdf))
            logger.info(f"read pdf file {args.pdf}")
        else:
            logger.info(f"read pdf files from path {args.pdf}")
            for root, dirs, files in os.walk(args.pdf):
                logger.trace(f"root: {root}, dirs: {dirs}, files: {files}")
                for filename in files:
                    if filename.endswith(".pdf"):
                        paper_list.append(Paper(path=os.path.join(root, filename)))

        logger.info("paper_num: {}".format(len(paper_list)))
        for paper_index, paper in enumerate(paper_list):
            name = Path(paper.path).name
            logger.info(f"{paper_index=}, {name=}")
        reader.summary_with_chat(paper_list=paper_list, key_words=reader.key_word)
    else:
        reader = Reader(
            key_word=args.key_word,
            query=args.query,
            filter_keys=args.filter_keys,
            sort=sort,
            args=args,
        )
        reader.show_info()
        filter_results = reader.filter_arxiv(max_results=args.max_results)
        paper_list = reader.download_pdf(filter_results)
        reader.summary_with_chat(paper_list=paper_list, key_words=reader.key_word)

    reader.show_token_usage()


def cli(args):
    parameters = PaperParams(**vars(args))
    main(parameters)
