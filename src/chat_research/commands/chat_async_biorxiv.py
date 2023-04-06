import asyncio
import datetime
from typing import Optional

import aiohttp
from loguru import logger
from pydantic import BaseModel

from ..areader import AsyncBaseReader
from ..paper_with_image import Paper
from ..provider import async_biorxiv as biorxiv


class Params(BaseModel):
    date: Optional[str] = None
    days: Optional[int] = None
    server: str
    category: list[str]
    filter_keys: Optional[list[str]] = None
    max_results: int
    sort: str
    save_image: bool
    file_format: str
    language: str


class Reader(AsyncBaseReader):
    def __init__(
        self,
        category: list[str],
        filter_keys: list[str],
        root_path=".",
        sort=biorxiv.SortCriterion.SubmittedDate,
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

        self.user_name = user_name  # 读者姓名
        self.sort = sort  # 读者选择的排序方式
        self.args = args
        self.category = category
        self.filter_keys = filter_keys

    def get_biorxiv(self, max_results=30):
        if self.args.days is not None:
            return biorxiv.Search(
                days=self.args.days,
                server=self.args.server,
                max_results=max_results,
            )
        else:
            start_date, end_date = self.args.date.strip().split(":")
            return biorxiv.Search(
                start_date=start_date,
                end_date=end_date,
                server=self.args.server,
                max_results=max_results,
            )

    def filter_arxiv(self, max_results=30) -> list[biorxiv.Result]:
        search = self.get_biorxiv(max_results=max_results)
        results = list(search.results())

        logger.info("All search:")
        for index, result in enumerate(results):
            logger.info(
                f"{index=}, title={result.title} {result.date.strftime('%Y-%m-%d')}"
            )

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
            logger.info(
                f"{index=}, title={result.title} {result.date.strftime('%Y-%m-%d')}"
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
            abs=result.abstract.replace("-\n", "-").replace("\n", " "),
            authers=[str(aut) for aut in result.authors.split(",")],
        )

        return paper

    async def _download_pdf(self, filter_results):
        date_str = str(datetime.datetime.now())[:13].replace(" ", "-")
        category_str = "-".join([c for c in self.category])
        path = self.root_path / "pdf_files" / f"{category_str}-{date_str}"
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
        categories = ",".join(self.category)
        logger.info(f"Categories: {categories}")
        logger.info(f"Sort: {self.sort}")
        logger.info(f"Max_results: {self.args.max_results}")
        if self.args.days is not None:
            logger.info(f"Day: {self.args.days}")
        else:
            logger.info(f"Date: {self.args.date}")


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
        default=2,
        metavar="",
        help="the last days of arxiv papers of this query (default: %(default)s)",
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
        "-m",
        "--max-results",
        type=int,
        default=20,
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
        "-c",
        "--category",
        type=str,
        default="bioinformatics",
        choices=CATEGORY_LIST,
        action="extend",
        nargs="+",
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
        "--save-image",
        default=False,
        metavar="",
        help="save image? It takes a minute or two to save a picture! But pretty (default: %(default)s)",
    )

    return name


def main(args):
    if args.sort == "Relevance":
        sort = biorxiv.SortCriterion.Relevance
    elif args.sort == "LastUpdatedDate":
        sort = biorxiv.SortCriterion.LastUpdatedDate
    else:
        sort = biorxiv.SortCriterion.Relevance

    reader = Reader(
        category=args.category,
        filter_keys=args.filter_keys,
        sort=sort,
        args=args,
    )

    reader.show_info()
    filter_results = reader.filter_arxiv(max_results=args.max_results)
    paper_list = reader.download_pdf(filter_results)

    key_words = ",".join(reader.category)
    reader.summary_with_chat(paper_list, key_words)
    reader.show_token_usage()


def cli(args):
    if not isinstance(args.category, list):
        args.category = [args.category]

    parser = Params(**vars(args))
    main(parser)
